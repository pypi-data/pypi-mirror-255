import logging
import re
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from functools import partial
from itertools import repeat, product
from multiprocessing import Pool
from pathlib import Path
from typing import (
    BinaryIO,
    Dict,
    Iterable,
    TextIO,
    Tuple,
    Union,
    Optional,
    List,
    MutableSet,
    Sequence,
)

import dnaio
import numpy as np
import pandas as pd
import pysam
from cutadapt.adapters import BackAdapter, FrontAdapter, LinkedAdapter
from cutadapt.modifiers import AdapterCutter, ModificationInfo
from pybedtools import BedTool
from pybedtools.cbedtools import Interval
from smap.haplotype import (
    HAPLOTYPES_COLUMN_NAME,
    LOCUS_COLUMN_NAME,
    REFERENCE_COLUMN_NAME,
    CountMatrix,
)
from smap.plotting import PLOT_ALL, PLOT_SUMMARY
from xopen import xopen

from .arguments import parse_args

LOGGER = logging.getLogger("Haplotype")


@dataclass
class Anchor:
    """Define an anchor: a sequence that flanks a genomic interval (window).
       Two anchors are needed to define the window.

    :param locus: name of the target (two anchors have the same target name)
    :param start: start of the anchor on the reference
    :param end: end of the anchor on the reference
    :param seq: genomics sequence, defaults to ""
    """

    locus: str  # amplicon, unique for anchor pair (see NAME= attribute)
    start: int
    end: int
    seq: str = ""

    def __hash__(self) -> int:
        return hash((self.locus, self.start, self.end))


@dataclass
class Window:
    """A region of the genome, between two anchors.

    :param genome_id: scaffold where this window resides on the reference genome.
    :param upstream_border: anchor that flanks the region upstream.
    :param downstream_border: anchor that flanks the refion downstream.
    """

    genome_id: str  # ID present in reference
    upstream_border: Anchor
    downstream_border: Anchor

    def __post_init__(self):
        if not self.genome_id:
            raise ValueError(
                "Scaffold/chromosome ID can not be empty when defining an anchor."
            )
        if self.upstream_border.locus != self.downstream_border.locus:
            raise ValueError(
                f"The two anchors that define a window on {self.genome_id} target a different locus."
            )

    def __iter__(self) -> Iterable[Anchor]:
        yield from (self.upstream_border, self.downstream_border)

    def interval(self) -> Interval:
        """Get the interval between the two anchors.

        :return: region between the end of the upstream anchor and the start of the downstream anchor.
        """
        return Interval(
            self.genome_id,
            self.upstream_border.end,
            self.downstream_border.start,
            strand="+",
            otherfields=[b"NAME=%b" % self.upstream_border.locus.encode("utf8")],
        )

    @property
    def locus(self) -> str:
        """scaffold where this window resides on the reference genome.

        :return: the scaffold ID.
        """
        return self.upstream_border.locus

    def __hash__(self) -> int:
        return hash((self.genome_id, self.upstream_border, self.downstream_border))


class Windows:
    """Provides methods to get window information for file and
    perform operation on multiple windows at the same time.
    """

    def __init__(self, windows: Iterable[Window]) -> None:
        self._windows = windows

    @classmethod
    def read_file(cls, open_gff: TextIO) -> "Windows":
        """Read a gff file defining one anchor per line.
           Each gff entry should define a value for the 'NAME=' attribute.
           The two anchors spanning a window must have the same NAME= value.
           All anchors are assumed to be defined in the "+" orientation,
           compared to a reference that encodes regions of interest in the same
           orientation as the mRNA is transcribed for protein creation.

        :param open_gff: an open file for reading.
        :raises NotImplementedError: Anchors defined in reverse orientation are not supported.
        :raises ValueError: The .gff entries must contain a NAME field in the 9th column.
        :raises ValueError: More than 2 anchors were found for one window.
        :raises ValueError: Two anchors in for a window do not have matching chromosome identifiers!
        :return: the newly created Windows object.
        """
        anchors = dict()
        gff = BedTool(open_gff)
        for anchor in gff:
            if anchor.strand == "-":
                raise NotImplementedError(
                    "Anchors defined in reverse orientation are not supported."
                )
            try:
                anchors.setdefault(anchor.attrs["NAME"].split(" ")[0], []).append(
                    anchor
                )
            except KeyError:
                raise ValueError(
                    "All .gff entries must contain a NAME field in the 9th column."
                )

        windows = []
        for locus, intervals in anchors.items():
            try:
                interval1, interval2 = intervals
            except ValueError as e:
                raise ValueError(
                    f"More than 2 anchors were found for window {locus}. "
                    "Please make sure that only two entries in the anchor .gff "
                    "file have the same NAME= attribute."
                ) from e
            else:
                if interval1.chrom != interval2.chrom:
                    raise ValueError(
                        f"The two anchors in for window {locus} do not have matching "
                        "chromosome identifiers!"
                    )
                anchor1 = Anchor(locus, interval1.start, interval1.end)
                anchor2 = Anchor(locus, interval2.start, interval2.end)
                windows.append(
                    Window(interval1.chrom, anchor1, anchor2)
                    if interval1 < interval2
                    else Window(interval1.chrom, anchor2, anchor1)
                )
        return cls(windows)

    def add_anchor_sequences(self, genome: BinaryIO) -> None:
        """For each window, add the reference sequences to the anchors
        by looking them up in the genome.

        :param genome: an open fasta file.
        :raises ValueError: A window references a scaffold ID that could not be found in the genome file.
        """
        with dnaio.open(genome, fileformat="fasta") as open_fasta:
            for chromosome in open_fasta:
                seq_id, seq = chromosome.name, chromosome.sequence
                for window in self._windows:
                    upstream_border, downstream_border = window
                    if window.genome_id == seq_id:
                        upstream_border.seq = seq[
                            upstream_border.start : upstream_border.end
                        ]
                        downstream_border.seq = seq[
                            downstream_border.start : downstream_border.end
                        ]

        for window in self._windows:
            if not window.upstream_border.seq and not window.downstream_border.seq:
                raise ValueError(
                    f"Could not find window chromosome {window.genome_id} in the reference .fasta file."
                )

    def interval_bed(self) -> BedTool:
        """Get the intervals between the anchors in BED format.

        :return: class:`BedTool` object containing the window intervals in BED format.
        """
        return BedTool(
            "\n".join(str(window.interval()) for window in self._windows),
            from_string=True,
        )

    def get_window(self, locus_id: str) -> Window:
        """Get a window by the target id."""
        for window in self._windows:
            if window.locus == locus_id:
                return window
        raise ValueError(f"Could not find window for locus {locus_id}")


class _FilePathWrapper:
    """
    A class to add extra operations to perform on files.

    :param file_path: location of the file on disc.
    """

    def __init__(self, file_path: Union[str, Path]) -> None:
        self._file = Path(file_path)

    def __hash__(self):
        return hash(self._file)

    def __eq__(self, other: "_FilePathWrapper") -> bool:
        return self.__class__ == other.__class__ and self._file == other._file

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._file})"

    @classmethod
    def find_in_directory(cls, directory: Path, extensions: Iterable[str]):
        """Find files in a directory with a given extension.

        :param directory: The directory to search files in.
        :param extensions: Only to return files with a given extension.
        :raises ValueError: No files were found in the given directory with the given extensions.
        :raises ValueError: The directory does not exist or is not a directory.
        """
        if not directory.is_dir():
            raise FileNotFoundError(
                f"Directory {directory} does not exist or is not a directory."
            )
        files = [
            cls(file_)
            for file_ in directory.iterdir()
            if file_.is_file()
            and (file_.suffix in extensions or "".join(file_.suffixes) in extensions)
        ]
        if not files:
            raise ValueError(
                f'No files with extension {",".join(extensions)} '
                + f"were found in directory {directory}!"
            )
        LOGGER.info(f"Found {len(files)} files in directory {directory}.")
        return files

    @property
    def file(self) -> Path:
        """Location of the file."""
        return self._file

    @property
    def stem(self) -> str:
        """Get the name of the file, with the last extension removed."""
        return self.file.stem


class Bam(_FilePathWrapper):
    """Represents a .bam file location, while also providing extra operations to
    perform on the bam file.

    :param bam: location of a valid .bam file.
    """

    def __init__(self, bam: Union[str, Path]) -> None:
        super().__init__(bam)
        self._genome_file: Optional[Path] = None

    def _number_of_reads(self):
        flag_stats = pysam.flagstat(str(self._file))
        total_reads = flag_stats.split("\n")[0]
        reg_string = r"(\d+ \+ \d+) in total \(QC-passed reads \+ QC-failed reads\)"
        m = re.search(reg_string, total_reads)
        qc_passed, qc_failed = m.group(1).split("+")
        return int(qc_passed) + int(qc_failed)

    @property
    def stem(self) -> str:
        """Get the name of the file, .bam extension removed if present"""
        if self.file.suffix == ".bam":
            return self.file.stem
        return self.file.name

    def sort(
        self, output_file: Optional[Path] = None, threads: Optional[int] = 1
    ) -> "Bam":
        """Sort the bam file into a new file in the current directory with a new extension ".sorted.bam".

        :param threads: The number of threads to use when sorting the bam file.
        :return: the sorted bam file
        """
        if output_file is None:
            sorted_bam_path = Path(self._file.name).with_suffix(".sorted.bam")
        else:
            sorted_bam_path = output_file
        pysam.sort(
            "-t",
            "RNAME",
            str(self.file),
            "-@",
            str(threads),
            "-o",
            str(sorted_bam_path),
        )
        pysam.index(str(sorted_bam_path))
        # The _genome_file attribute indicates whether or not the bam is sorted.
        # Genome file indicates the order of the chromosomes, together with their length
        result = Bam(sorted_bam_path)
        result._genome_file = self._generate_genome_file(sorted_bam_path)
        return result

    @staticmethod
    def _generate_genome_file(sorted_bam: Path) -> Path:
        """Create a genome file: a tab-delinited file with the first column indicating
           the chromosomes in order, and the second column indicating the chromosome length.
           This genome file can be used to perform memory-efficient intersection using bedtools.

        :param sorted_bam: a bam file with entries by chromosome.
        :return: the path to a newly created genome file.
        """
        bam_header_file = sorted_bam.with_suffix(".header")
        bam_genome_file = sorted_bam.with_suffix(".genome")
        bam_header_file.touch()  # https://github.com/pysam-developers/pysam/issues/677
        pysam.view(
            "-H",
            "-o",
            str(bam_header_file),
            str(sorted_bam),
            save_stdout=str(bam_header_file),
        )
        with bam_header_file.open("r") as open_bam_header, bam_genome_file.open(
            "w"
        ) as open_genome_file:
            for line in open_bam_header:
                if line.startswith("@SQ"):
                    to_write = line.replace("@SQ\tSN:", "").replace("LN:", "")
                    open_genome_file.write(to_write)
        bam_header_file.unlink()
        return bam_genome_file

    def sort_read_ids_per_window(
        self, windows: Windows
    ) -> Dict[str, List[Tuple[Window, str]]]:
        """For each mapped read in the bam file, retreive the window it
           was mapped to and the orientation it was mapped with.

        :param windows: the windows to sort the reads over.
        :return: a dictionairy with the read identifiers as keys and the
                 corresponding window and mapping orientation as values
        """
        result = dict()
        windows_bed = windows.interval_bed()
        extra_args = {}
        if self._genome_file:
            windows_bed = windows_bed.sort(faidx=str(self._genome_file))
            extra_args = {"g": str(self._genome_file), "sorted": True}
        intersect = windows_bed.intersect(
            str(self.file), **extra_args, wb=True, bed=True
        )
        for record in intersect:
            locus = re.search(r"NAME=(\S+)", record.fields[6])[1]
            window = windows.get_window(locus)
            read_id = record.fields[10].split(" ")[0].split("/")[0]
            read_orientation = record.fields[12]
            result.setdefault(read_id, []).append((window, read_orientation))
        number_of_reads = self._number_of_reads()
        LOGGER.info(
            f"{number_of_reads} reads parsed from original .fastq, of which {len(result)} were assigned to a window."
        )
        return result


class Fastq(_FilePathWrapper):
    """Represents a fastq file location, while also providing extra operations to
    perform on the bam file.

    :param bam: location of a valid .fastq file.
    """

    def __init__(self, fastq: Union[str, Path]) -> None:
        super().__init__(fastq)

    def count_sequences_per_window(
        self, lookup: Dict[str, List[Tuple[Window, str]]], error_rate: float, threads=1
    ) -> Dict[Window, Dict[str, int]]:
        opener = partial(xopen, threads=threads)
        counter = HaplotypeCounter(lookup, error_rate)
        with dnaio.open(self._file, opener=opener) as fq_fh:
            for read in fq_fh:
                read_id = read.name.split(" ")[0]
                try:
                    windows = lookup[read_id]
                except KeyError:
                    continue
                else:
                    for window, orientation in windows:
                        if orientation == "-":
                            read = read.reverse_complement()
                        counter.count(read, window)
        return counter.haplotype_counts

    @property
    def stem(self) -> str:
        """Get the name of the file, extensions removed if present"""
        extensions = (".fastq", ".fq", ".fasq")
        compressions = (".bzip2", ".bzp2", ".bz2", ".gzip", ".gz", "")
        extension_compression = product(extensions, compressions)
        extension_compression = sorted(
            ["".join(entry) for entry in extension_compression], key=len, reverse=True
        )
        for suffix in extension_compression:
            if self.file.name.endswith(suffix):
                return self.file.name[: -len(suffix)]
        return self.file.name


class WindowAdapter(LinkedAdapter):
    """A linked adapter: two adapters that must occur in a read, seperated by an insert.
    The insert we call the Window, where the two anchors that flank the window
    are the two adapters. Can be used to match to a read.
    """

    @classmethod
    def from_window(cls, window: Window, error_rate: float) -> "WindowAdapter":
        """Construct a new linked adapter from a window.

        :param window: [description]
        :return: [description]
        """
        anchor1, anchor2 = window
        upstream_adapter = FrontAdapter(
            anchor1.seq, max_errors=error_rate, min_overlap=len(anchor1.seq)
        )
        downstream_adapter = BackAdapter(
            anchor2.seq, max_errors=error_rate, min_overlap=len(anchor2.seq)
        )
        return cls(
            upstream_adapter,
            downstream_adapter,
            front_required=True,
            back_required=True,
            name="sample",
        )


class HaplotypeCounter:
    """Counts the haplotypes for each window in a sample.

    :param lookup: for each read to be counted, a list of windows it is mapped to,
        together with the mapping orientation.
    """

    def __init__(
        self, lookup: Dict[str, List[Tuple[Window, str]]], error_rate: float
    ) -> None:
        unique_windows: MutableSet = set(
            [window for windows in lookup.values() for window, _ in windows]
        )
        self._read_handlers: Dict[Window, AdapterCutter] = {
            window: AdapterCutter([WindowAdapter.from_window(window, error_rate)])
            for window in unique_windows
        }
        self._written_reads: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

    @property
    def haplotype_counts(self) -> Dict[str, Dict[str, int]]:
        """
        Get the read counts.
        """
        return self._written_reads

    def count(self, read: dnaio.Sequence, window: Window) -> None:
        """Count a read for a certain window. Discard the read if it could not be trimmed.

        :param read: the read to be counted.
        """
        info = ModificationInfo(read)
        read = self._read_handlers[window](read, info)
        if info.matches:
            self._written_reads[window][read.sequence] += 1


def filter_gff_loci(
    gff: Union[Path, str], write_to: str, loci_to_keep: Iterable[Tuple[str, ...]]
):
    """Given a gff file, create a new gff file with only selected records.

    :param gff: an open gff gile for reading.
    :param write_to: a open file to write the filtered records to.
    :param loci_to_keep: A list of entries to keep, identified a list of the scaffold,
        start and stop position for each entry.
    """
    input_gff = BedTool(gff)
    output_bed = BedTool(
        record
        for record in input_gff
        if (record.attrs["NAME"].split(" ")[0],) in loci_to_keep
    )
    output_bed.saveas(write_to)


def match_bam_with_fastq(
    bam_files: Iterable[Bam], fastq_files: Iterable[Fastq]
) -> Iterable[Tuple[Bam, Fastq]]:
    """For each bam file in a list, find the corresponding .fastq file.

    :param bam_files: a number of bam files to matched to fastq files.
    :param fastq_files: a number of fastq files  to be match with bam files.
    :raises ValueError: A bam file could not be matched with any of the .fastq files.
    :return: a list of matched bam-fastq pairs.
    """
    fastq_bam_pairs = []
    for bam in bam_files:
        bam_stem = bam.stem
        matched = False
        for fastq in fastq_files:
            fastq_stem = fastq.stem
            if bam_stem == fastq_stem:
                matched = True
                fastq_bam_pairs.append((bam, fastq))
                break
        if not matched:
            raise ValueError(
                f".bam {bam_stem} file could not be matched with any .fastq file."
            )
    return fastq_bam_pairs


def add_guide_targets(counts: pd.DataFrame, guides: Path) -> pd.DataFrame:
    if not guides.is_file():
        raise FileNotFoundError(f"{str(guides)} does not exist or is not a file.")
    guides_dict = fasta_to_dict(guides)
    new_column = [
        guides_dict.get(
            haplotype_seq, counts.index.get_level_values(LOCUS_COLUMN_NAME)[i]
        )
        for i, (haplotype_seq, _) in enumerate(
            zip(
                counts.index.get_level_values(HAPLOTYPES_COLUMN_NAME),
                counts.index.get_level_values(LOCUS_COLUMN_NAME),
            )
        )
    ]
    return counts.assign(Target=new_column).set_index("Target", append=True)


def counts_to_dataframe(sample: str, counts: Dict) -> pd.DataFrame:
    index_tuples = [
        (ref_id, locus_rep, haplotype)
        for window, haplotype_counts in counts.items()
        for (ref_id, locus_rep, haplotype) in zip(
            repeat(window.genome_id), repeat(window.locus), haplotype_counts.keys()
        )
    ]
    index = pd.MultiIndex.from_tuples(
        index_tuples,
        names=[REFERENCE_COLUMN_NAME, LOCUS_COLUMN_NAME, HAPLOTYPES_COLUMN_NAME],
    )
    df_data = {
        sample: [
            count
            for haplotype_counts in counts.values()
            for count in haplotype_counts.values()
        ]
    }
    sample_data = df_data[sample]
    largest = max(sample_data) if sample_data else 0
    min_dtype = np.min_scalar_type(largest)  # for 0 this is uint8
    dataframe_column = pd.DataFrame(df_data, index=index, dtype=min_dtype)
    return dataframe_column.convert_dtypes()  # Upgrade to dtype that supports NA


def fasta_to_dict(fasta: Path) -> Dict[str, str]:
    with dnaio.open(str(fasta)) as open_fasta:
        return {read.sequence: read.name for read in open_fasta}


def counting_worker(
    bam: Bam, fastq: Fastq, windows: Windows, error_rate: float
) -> pd.DataFrame:
    read_lookup = bam.sort_read_ids_per_window(windows)
    counts = fastq.count_sequences_per_window(read_lookup, error_rate)
    result = counts_to_dataframe(bam.stem, counts)
    LOGGER.info(
        "Done sorting %s and %s, a total of %s reads had the correct borders to trim.",
        bam,
        fastq,
        result.to_numpy().sum(),
    )
    return result


def merge_samples(columns: Sequence[pd.DataFrame]) -> pd.DataFrame:
    LOGGER.info("Joining tables for different samples.")
    if all((column.empty for column in columns)):
        raise ValueError(
            "No reads were counted for any of the samples. " "Please check your input."
        )
    return pd.concat(columns, axis="columns")


def main(args):
    parsed_args = parse_args(args)
    if not parsed_args.borders.is_file():
        raise FileNotFoundError(
            f"Border .gff file {parsed_args.borders} "
            + "does not exist or is not a file."
        )
    if not parsed_args.genome.is_file():
        raise FileNotFoundError(
            ".fasta file containing reference genome "
            + "does not exist or is not a file."
        )
    prefix = f"{parsed_args.out}_" if parsed_args.out else ""

    fastq_extensions = (".fastq", ".fq", ".bzip2", ".bzp2", ".bz2", ".gzip", ".gz")
    bam_files = Bam.find_in_directory(parsed_args.alignments_dir, (".bam",))
    fastq_files = Fastq.find_in_directory(parsed_args.sample_dir, fastq_extensions)

    if parsed_args.memory_efficient:
        LOGGER.info("Memory efficient haplotyping requested, sorting .bam files.")
        bam_files = [bam.sort(threads=parsed_args.processes) for bam in bam_files]
    fastq_bam_pairs = match_bam_with_fastq(bam_files, fastq_files)

    with parsed_args.borders.open("r") as open_gff, parsed_args.genome.open(
        "rb"
    ) as open_genome:
        windows = Windows.read_file(open_gff)
        windows.add_anchor_sequences(open_genome)
    LOGGER.info("Started sorting reads into windows.")

    with Pool(parsed_args.processes) as p:
        partial_worker = partial(
            counting_worker, windows=windows, error_rate=parsed_args.max_error
        )
        columns = p.starmap(partial_worker, fastq_bam_pairs)
    counts = merge_samples(columns)
    if parsed_args.guides:
        counts = add_guide_targets(counts, parsed_args.guides)
    count_matrix = CountMatrix(counts)
    count_matrix.filter_for_minimum_or_maximum_read_count(
        parsed_args.min_read_count, parsed_args.max_read_count
    )
    count_matrix.filter_on_minimum_haplotype_frequency(
        parsed_args.min_haplotype_frequency,
        mask_frequency=parsed_args.mask_frequency,
    )
    filename_parameters = (
        f"c{parsed_args.min_read_count}_"
        + f"f{parsed_args.min_haplotype_frequency}_"
        + f"m{parsed_args.mask_frequency}"
    )
    count_matrix.to_csv(
        f"{prefix}read_counts_{filename_parameters}.tsv",
        na_rep=parsed_args.undefined_representation,
    )
    frequency_matrix = count_matrix.calculate_frequencies()
    frequency_matrix.to_csv(
        f"{prefix}haplotype_frequencies_{filename_parameters}.tsv",
        na_rep=parsed_args.undefined_representation,
    )
    frequency_matrix.filter_for_number_of_distinct_haplotypes(
        parsed_args.min_distinct_haplotypes, parsed_args.max_distinct_haplotypes
    )
    if parsed_args.plot >= PLOT_ALL:
        frequency_matrix.plot_frequencies(
            prefix, parsed_args.plot_type, parsed_args.frequency_bounds
        )
    if parsed_args.plot >= PLOT_SUMMARY:
        frequency_matrix.plot_haplotype_counts(
            f"{prefix}haplotype_counts_frequencies", parsed_args.plot_type
        )
    if parsed_args.discrete_calls:
        dosage_matrix = frequency_matrix.calculate_discrete_calls(
            parsed_args.discrete_calls, parsed_args.frequency_bounds
        )
        dosage_matrix.to_csv(
            f"{prefix}haplotypes_{filename_parameters}_discrete_calls.tsv",
            na_rep=parsed_args.undefined_representation,
        )
        dosage_matrix.write_total_calls(
            f"{prefix}haplotypes_{filename_parameters}_discrete_calls_total.tsv",
            na_rep=parsed_args.undefined_representation,
        )
        if parsed_args.plot >= PLOT_SUMMARY:
            dosage_matrix.plot_haplotype_counts(
                f"{prefix}haplotype_counts_discrete_calls", parsed_args.plot_type
            )
        if parsed_args.dosage_filter:
            orig_dosage_matrix = deepcopy(dosage_matrix)
            dosage_matrix.filter_distinct_haplotyped_per_sample(
                parsed_args.dosage_filter
            )
            dosage_matrix.filter_for_number_of_distinct_haplotypes(
                parsed_args.min_distinct_haplotypes, parsed_args.max_distinct_haplotypes
            )
            if parsed_args.plot >= PLOT_SUMMARY:
                orig_dosage_matrix.plot_sample_completeness(
                    prefix, parsed_args.plot_type
                )
                orig_dosage_matrix.plot_sample_correctness(
                    dosage_matrix, prefix, parsed_args.plot_type
                )
                orig_dosage_matrix.plot_locus_completeness(
                    prefix, parsed_args.plot_type
                )
                orig_dosage_matrix.plot_locus_correctness(
                    dosage_matrix, prefix, parsed_args.plot_type
                )
                orig_dosage_matrix.write_locus_correctness_completeness(
                    dosage_matrix,
                    f"{prefix}locus_completeness_correctness.tsv",
                    na_rep=parsed_args.undefined_representation,
                )
                orig_dosage_matrix.write_sample_correctness_completeness(
                    dosage_matrix,
                    f"{prefix}sample_completeness_correctness.tsv",
                    na_rep=parsed_args.undefined_representation,
                )
                dosage_matrix.plot_haplotype_counts(
                    f"{prefix}haplotype_counts_discrete_calls_filtered",
                    parsed_args.plot_type,
                )
                if parsed_args.locus_correctness_filter:
                    correct_loci = orig_dosage_matrix.get_correct_loci(
                        orig_dosage_matrix, parsed_args.locus_correctness_filter
                    )
                    new_gff = f"{prefix}{filename_parameters}_correctness{parsed_args.locus_correctness_filter}_loci.gff"
                    with parsed_args.borders.open("r") as open_gff:
                        filter_gff_loci(open_gff, new_gff, correct_loci)
        dosage_matrix.to_csv(
            f"{prefix}haplotypes_{filename_parameters}_discrete_calls_filtered.tsv",
            na_rep=parsed_args.undefined_representation,
        )
        dosage_matrix.write_population_frequencies(
            f"{prefix}haplotypes_{filename_parameters}_pop_hf.tsv",
            na_rep=parsed_args.undefined_representation,
        )
