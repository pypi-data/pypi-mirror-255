from argparse import ArgumentParser, Namespace
from pathlib import Path
from math import inf
from smap.plotting import PLOT_ALL, PLOT_NOTHING, PLOT_SUMMARY, PlotLevel
from smap.haplotype import set_default_frequency_thresholds, handle_filter_inf
import logging
from pandas import NA

LOGGER = logging.getLogger("Haplotype")


def parse_args(args):
    parser = ArgumentParser("haplotype-window")
    input_output_group = parser.add_argument_group(
        title="input and output information."
    )
    input_output_group.add_argument(
        "genome",
        type=Path,
        help="FASTA file with the reference genome sequence.",
    )
    input_output_group.add_argument(
        "borders",
        type=Path,
        help="GFF file with the coordinates of pairs of Borders that enclose a "
        "Window. Must contain NAME=<> in column 9 to denote the Window name.",
    )
    input_output_group.add_argument(
        "alignments_dir",
        type=Path,
        help="Directory containing BAM and BAM index files. All BAM files should be "
        "in the same directory (default current directory)",
    )
    input_output_group.add_argument(
        "sample_dir",
        type=Path,
        default=".",
        help="Directory containing .fastq files that were mapped onto the reference"
        " genome to create the .bam files. The .fastq file names must have "
        " the same prefix as the .bam files specified in --dir.",
    )
    input_output_group.add_argument(
        "guides",
        nargs="?",
        default=None,
        type=Path,
        help="Optional fasta file containing the sequences from gRNAs used in CRISPR "
        "genome editing. Useful when primers against the delivery vector are "
        "included in the HiPlex amplicon mixture. In multiplex setting, this list of "
        "sequences can be used to identify exactly which gRNA(s) were used in "
        "the CRISPR-Cas/gRNA delivery vector.",
    )

    input_output_group.add_argument(
        "--write_sorted_sequences",
        action="store_true",
        default=False,
        help="Write .fastq files containing the reads for each Window in a separate "
        "file per input sample.",
    )

    input_output_group.add_argument(
        "-o",
        "--out",
        dest="out",
        default="",
        type=str,
        help='Basename of the output file without extension (default: "").',
    )

    discrete_calls_group = parser.add_argument_group(
        title="Discrete calls options",
        description="Use thresholds to transform haplotype frequencies into "
        "discrete calls using fixed intervals. The assigned intervals are indicated "
        "by a running integer. This is only informative for individual samples "
        "and not for Pool-Seq data.",
    )
    discrete_calls_group.add_argument(
        "-e",
        "--discrete_calls",
        choices=["dominant", "dosage"],
        dest="discrete_calls",
        help='Set to "dominant" to transform haplotype frequency values '
        'into presence(1)/absence(0) calls per allele, or "dosage" '
        "to indicate the allele copy number.",
    )
    discrete_calls_group.add_argument(
        "-i",
        "--frequency_interval_bounds",
        nargs="+",
        dest="frequency_bounds",
        help="Frequency interval bounds for transforming haplotype "
        "frequencies into discrete calls. Custom thresholds can be "
        "defined by passing one or more space-separated values (relative "
        "frequencies in percentage). For dominant calling, one value "
        "should be specified. For dosage calling, an even total number "
        "of four or more thresholds should be specified. Default values "
        'are invoked by passing either "diploid" or "tetraploid". The '
        "default value for dominant calling (see discrete_calls "
        'argument) is 10, both for "diploid" and "tetraploid". For '
        'dosage calling, the default for diploids is "10, 10, 90, 90" '
        'and for tetraploids "12.5, 12.5, 37.5, 37.5, 62.5, 62.5, 87.5, '
        '87.5".',
    )
    discrete_calls_group.add_argument(
        # Default will be set to a new default later, need None to check
        # If a warning needs to be presented to user is option is not set.
        "-z",
        "--dosage_filter",
        type=int,
        default=None,
        dest="dosage_filter",
        help="Mask dosage calls in the loci for which the total allele count "
        "for a given locus at a given sample differs from the defined "
        "value. For example, in diploid organisms the total allele copy "
        "number must be 2, and in tetraploids the total allele copy "
        "number must be 4. (default no filtering).",
    )
    discrete_calls_group.add_argument(
        # Default will be set to a new default later, need None to check
        # A warning needs to be presented to user if option is not set.
        "--locus_correctness",
        type=float,
        default=None,
        dest="locus_correctness_filter",
        help="Create a new .gff file defining only the loci that were "
        "correctly dosage called (-z) in at least the defined percentage of samples.",
    )

    plot_group = parser.add_argument_group(title="Graphical output options")
    plot_group.add_argument(
        "--plot",
        dest="plot",
        type=PlotLevel,
        default=PLOT_SUMMARY,
        choices=(PLOT_ALL, PLOT_SUMMARY, PLOT_NOTHING),
        help='Select which plots are generated. Choosing "nothing" '
        'disables plot generation. Passing "summary" only generates '
        'graphs with information for all samples, while "all" will '
        'also generate per-sample plots [default "summary"].',
    )
    plot_group.add_argument(
        "-t",
        "--plot_type",
        dest="plot_type",
        choices=["png", "pdf"],
        default="png",
        help="Choose the file type for the plots [png].",
    )

    file_output_group = parser.add_argument_group(title="File formatting options")
    file_output_group.add_argument(
        "-m",
        "--mask_frequency",
        dest="mask_frequency",
        type=float,
        default=0,
        help="Mask haplotype frequency values below MASK_FREQUENCY for "
        "individual samples to remove noise from the final output. "
        "Haplotype frequency values below MASK_FREQUENCY are set to "
        "UNDEFINED_REPRESENTATION (see -u). Haplotypes are not removed based on this "
        "value, use '--min_haplotype_frequency' for this purpose instead.",
    )
    file_output_group.add_argument(
        "-u",
        "--undefined_representation",
        dest="undefined_representation",
        type=str,
        default=NA,
        help="Value to use for non-existing or masked data [NaN].",
    )

    filtering_group = parser.add_argument_group(title="Filtering options")
    filtering_group.add_argument(
        "-q",
        "--min_mapping_quality",
        dest="minimum_mapping_quality",
        default=30,
        type=int,
        help="Minimum bam mapping quality to retain reads for analysis [30].",
    )
    filtering_group.add_argument(
        # Use None as default because we want to check if this default is used.
        # If the user did not prvovide a value, the value will be set to 0 later.
        "-j",
        "--min_distinct_haplotypes",
        dest="min_distinct_haplotypes",
        default=None,
        type=int,
        help="Minimal number of distinct haplotypes per locus across all "
        "samples. Loci that do not fit this criterium are removed "
        "from the final output [0].",
    )
    filtering_group.add_argument(
        # Use None as default because we want to check if this default is used.
        # If the user did not prvovide a value, the value will be set to inf later.
        "-k",
        "--max_distinct_haplotypes",
        dest="max_distinct_haplotypes",
        default=None,
        type=float,  # This needs to be float, as the user can pass "inf" and only float("inf") works
        help="Maximal number of distinct haplotypes per locus across all "
        "samples. Loci that do not fit this criterium are removed from "
        "the final output [inf].",
    )
    filtering_group.add_argument(
        # Use None as default because we want to check if this default is used.
        # If the user did not prvovide a value, the value will be set to 0 later.
        "-c",
        "--min_read_count",
        dest="min_read_count",
        default=None,  # Will be set to inf by default later
        type=int,
        help="Minimal total number of reads for a locus in each sample [0].",
    )
    filtering_group.add_argument(
        # Use None as default because we want to check if this default is used.
        # If the user did not prvovide a value, the value will be set to inf later.
        "-d",
        "--max_read_count",
        dest="max_read_count",
        default=None,  # Will be set to inf by default later
        type=float,
        help="Maximal number of reads per locus per sample, read depth "
        "is calculated after filtering out the low frequency haplotypes "
        "(-f) [inf].",
    )
    filtering_group.add_argument(
        # Use None as default because we want to check if this default is used.
        # If the user did not prvovide a value, the value will be set to 0 later.
        "-f",
        "--min_haplotype_frequency",
        dest="min_haplotype_frequency",
        default=None,
        type=float,
        help="Minimal haplotype frequency (in %%) to retain the haplotype "
        "in the genotyping table. If in at least one sample the "
        "haplotype frequency is above MIN_HAPLOTYPE_FREQUENCY, the haplotype "
        "is retained. Haplotypes for which MIN_HAPLOTYPE_FREQUENCY is never "
        "reached in any of the samples are removed [0].",
    )
    filtering_group.add_argument(
        "--max_error",
        default=0,
        type=float,
        help="The maximum error rate (between 0 and 1; but not exactly 1) "
        "for finding the border sequences in the reads.",
    )

    resources_group = parser.add_argument_group(title="System resources")
    resources_group.add_argument(
        "-p",
        "--processes",
        dest="processes",
        default=1,
        type=int,
        help="Number of parallel processes [1].",
    )
    resources_group.add_argument(
        "--memory_efficient",
        dest="memory_efficient",
        action="store_true",
        default=False,
        help="Reduces the memory load significantly, but increases time to calculate results.",
    )
    parsed_args = parser.parse_args(args)
    if not 0 <= parsed_args.max_error < 1:
        raise ValueError(
            "The value for --max_error must be a value between 0 and 1 (but not exactly 1)"
        )
    parsed_args = set_default_frequency_thresholds(parsed_args)
    parsed_args = set_filter_defaults(parsed_args)
    return parsed_args


def set_filter_defaults(parsed_args: Namespace):
    warnings_dict = {
        # argument: [default_value]
        "min_distinct_haplotypes": 0,
        "max_distinct_haplotypes": inf,
        "min_read_count": 0,
        "max_read_count": inf,
        "min_haplotype_frequency": 0,
    }

    warning_message = (
        '"--%(argument)s" argument was not given. This means that '
        "this filter will not be applied. If you are sure about this, "
        'you can hide this warning by setting "--%(argument)s %(val)s" '
        "explicitly."
    )
    for argument, default_val in warnings_dict.items():
        if getattr(parsed_args, argument) is None:
            LOGGER.warning(warning_message, {"argument": argument, "val": default_val})
            setattr(parsed_args, argument, default_val)

    inf_arguments = [
        argument
        for argument, default_val in warnings_dict.items()
        if default_val == inf
    ]
    for argument in inf_arguments:
        parsed_args = handle_filter_inf(argument, parsed_args)
    return parsed_args
