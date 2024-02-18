from argparse import Namespace
import logging
from typing import Hashable
from unittest import TestCase
from pathlib import Path
from math import inf
import unittest
from unittest import mock
from haplotype_window.sample_files import sample_bam, sample_fastq
from tempfile import TemporaryDirectory
from pybedtools.bedtool import BedTool
from smap.haplotype_window.haplotype_window import (
    Anchor,
    Window,
    Windows,
    Bam,
    Fastq,
    _FilePathWrapper,
    filter_gff_loci,
    match_bam_with_fastq,
    add_guide_targets,
    counts_to_dataframe,
    fasta_to_dict,
    counting_worker,
    merge_samples,
)
from pybedtools.cbedtools import Interval
import pysam
from io import StringIO, BytesIO
from textwrap import dedent
import pandas as pd
from smap.haplotype import INDEX_COLUMNS
from smap.plotting import PlotLevel
from smap.haplotype_window.arguments import parse_args


class TestAnchor(TestCase):
    def test_hash(self):
        test_hash = hash(Anchor("locus1_1", 1, 2))
        for test_anchor in (
            Anchor("locus1_2", 1, 2),
            Anchor("locus1_1", 2, 2),
            Anchor("locus1_1", 1, 3),
        ):
            with self.subTest(test_anchor=test_anchor):
                self.assertNotEqual(hash(test_anchor), test_hash)

    def test_hash_ignores_seq(self):
        test_hash = hash(Anchor("locus1_1", 1, 2))
        test_hash_with_seq = hash(Anchor("locus1_1", 1, 2, seq="A"))
        self.assertEqual(test_hash_with_seq, test_hash)


class TestWindow(TestCase):
    def setUp(self) -> None:
        self.anchor1 = Anchor("locus1_1", 1, 2)
        self.anchor2 = Anchor("locus1_1", 3, 4)
        self.window = Window(
            "locus1", Anchor("locus1_1", 1, 2), Anchor("locus1_1", 3, 4)
        )

    def test_iter(self):
        anchor1, anchor2 = self.window
        self.assertEqual(anchor1, self.anchor1)
        self.assertEqual(anchor2, self.anchor2)

    def test_get_interval(self):
        interval = self.window.interval()
        self.assertIsInstance(interval, Interval)
        self.assertEqual(interval.chrom, "locus1")
        self.assertEqual(interval.start, 2)
        self.assertEqual(interval.stop, 3)
        self.assertEqual(interval.strand, "+")
        self.assertEqual(interval.fields[-1], "NAME=locus1_1")

    def test_locus(self):
        self.assertEqual(self.window.locus, "locus1_1")

    def test_init_without_genome_id_raises(self):
        msg = r"Scaffold/chromosome ID can not be empty when defining an anchor\."
        with self.assertRaisesRegex(ValueError, expected_regex=msg):
            Window("", Anchor("locus1_1", 1, 2), Anchor("locus1_1", 3, 4))

    def test_anchors_dont_share_locus(self):
        msg = (
            r"The two anchors that define a window on locus1 target a different locus\."
        )
        with self.assertRaisesRegex(ValueError, expected_regex=msg):
            Window("locus1", Anchor("foo", 1, 2), Anchor("bar", 3, 4))


class TestWindows(unittest.TestCase):
    def setUp(self) -> None:
        window1 = Window(
            "locus1", Anchor("locus1_1", 1, 10), Anchor("locus1_1", 15, 20)
        )
        window2 = Window(
            "locus2", Anchor("locus2_1", 20, 27), Anchor("locus2_1", 35, 40)
        )
        self.windows = Windows([window1, window2])

    def test_read_gff(self):
        gff = dedent(
            """\
                        locus1	SMAP	forward_anchor	1	10	.	+	.	NAME=locus1_1
                        locus1	SMAP	reverse_anchor	15	20	.	+	.	NAME=locus1_1
                        locus2	SMAP	forward_anchor	20	27	.	+	.	NAME=locus2_1
                        locus2	SMAP	reverse_anchor	35	40	.	+	.	NAME=locus2_1
                     """
        )
        gff_file = StringIO(gff)
        windows = Windows.read_file(gff_file)
        window1, window2 = windows._windows
        self.assertEqual(window1.locus, "locus1_1")
        anchor1, anchor2 = window1.upstream_border, window1.downstream_border
        self.assertEqual(anchor1.start, 0)
        self.assertEqual(anchor1.end, 10)
        self.assertEqual(anchor2.start, 14)
        self.assertEqual(anchor2.end, 20)
        self.assertEqual(window1.locus, "locus1_1")

        anchor1, anchor2 = window2.upstream_border, window2.downstream_border
        self.assertEqual(anchor1.start, 19)
        self.assertEqual(anchor1.end, 27)
        self.assertEqual(anchor2.start, 34)
        self.assertEqual(anchor2.end, 40)
        self.assertEqual(window2.locus, "locus2_1")

    def test_read_gff_wrong_order(self):
        gff = dedent(
            """\
                        locus1	SMAP	forward_anchor	1	10	.	+	.	NAME=locus1_1
                        locus2	SMAP	forward_anchor	20	27	.	+	.	NAME=locus2_1
                        locus1	SMAP	reverse_anchor	15	20	.	+	.	NAME=locus1_1
                        locus2	SMAP	reverse_anchor	35	40	.	+	.	NAME=locus2_1
                     """
        )
        gff_file = StringIO(gff)
        windows = Windows.read_file(gff_file)
        window1, window2 = windows._windows
        self.assertEqual(window1.locus, "locus1_1")
        anchor1, anchor2 = window1.upstream_border, window1.downstream_border
        self.assertEqual(anchor1.start, 0)
        self.assertEqual(anchor1.end, 10)
        self.assertEqual(anchor2.start, 14)
        self.assertEqual(anchor2.end, 20)
        self.assertEqual(window1.locus, "locus1_1")

        anchor1, anchor2 = window2.upstream_border, window2.downstream_border
        self.assertEqual(anchor1.start, 19)
        self.assertEqual(anchor1.end, 27)
        self.assertEqual(anchor2.start, 34)
        self.assertEqual(anchor2.end, 40)
        self.assertEqual(window2.locus, "locus2_1")

    def test_read_gff_no_name_raises(self):
        gff = dedent(
            """\
                        locus1	SMAP	forward_anchor	1	10	.	+	.	NAME=locus1_1
                        locus1	SMAP	reverse_anchor	15	20	.	+	.	\
                     """
        )
        gff_file = StringIO(gff)
        error_message = "All .gff entries must contain a NAME field in the 9th column."
        with self.assertRaisesRegex(ValueError, error_message):
            Windows.read_file(gff_file)

    def test_read_wrong_reverse_anchors_raises(self):
        gff = dedent(
            """\
                        locus1	SMAP	forward_anchor	1	10	.	+	.	NAME=locus1_1
                        locus1	SMAP	reverse_anchor	15	20	.	-	.	NAME=locus1_1
                     """
        )
        gff_file = StringIO(gff)
        error_message = "Anchors defined in reverse orientation are not supported."
        with self.assertRaisesRegex(NotImplementedError, error_message):
            Windows.read_file(gff_file)

    def test_read_wrong_number_of_anchors(self):
        gff = dedent(
            """\
                        locus1	SMAP	forward_anchor	1	10	.	+	.	NAME=locus1_1
                     """
        )
        gff_file = StringIO(gff)
        error_message = (
            "More than 2 anchors were found for window locus1_1. "
            "Please make sure that only two entries in the anchor .gff "
            "file have the same NAME= attribute."
        )
        with self.assertRaisesRegex(ValueError, error_message):
            Windows.read_file(gff_file)

    def test_read_anchors_different_chromosomes(self):
        gff = dedent(
            """\
                        locus1	SMAP	forward_anchor	1	10	.	+	.	NAME=locus1_1
                        locus2	SMAP	reverse_anchor	15	20	.	+	.	NAME=locus1_1
                     """
        )
        gff_file = StringIO(gff)
        error_message = (
            "The two anchors in for window locus1_1 do not "
            "have matching chromosome identifiers!"
        )
        with self.assertRaisesRegex(ValueError, error_message):
            Windows.read_file(gff_file)

    def test_add_anchor_sequences(self):
        reference_fasta = dedent(
            """\
                                 >locus1
                                 AAAAAACCCCCCCCCCCGGGGGGGGGGGGGGGGGGGGGGTTTTTTTTTTT
                                 >locus2
                                 AAAAAAAAAACCCCCCCCCCCCCCCGGGGGGGGGGGGGGGTTTTTTTTTTT
                                 """
        ).encode("utf-8")
        reference_file = BytesIO(reference_fasta)
        self.windows.add_anchor_sequences(reference_file)
        window1, window2 = self.windows._windows
        upstream_1, downstream_1 = window1.upstream_border, window1.downstream_border
        self.assertEqual(upstream_1.seq, "AAAAACCCC")
        self.assertEqual(downstream_1.seq, "CCGGG")
        upstream_2, downstream_2 = window2.upstream_border, window2.downstream_border
        self.assertEqual(upstream_2.seq, "CCCCCGG")
        self.assertEqual(downstream_2.seq, "GGGGG")

    def test_add_anchor_sequence_not_in_ref_raises(self):
        reference_fasta = dedent(
            """\
                                 >foo
                                 AAAAAACCCCCCCCCCCGGGGGGGGGGGGGGGGGGGGGGTTTTTTTTTTT
                                 >bar
                                 AAAAAAAAAACCCCCCCCCCCCCCCGGGGGGGGGGGGGGGTTTTTTTTTTT
                                 """
        ).encode("utf-8")
        reference_file = BytesIO(reference_fasta)
        message = (
            r"Could not find window chromosome locus1 in the reference \.fasta file\."
        )
        with self.assertRaisesRegex(ValueError, expected_regex=message):
            self.windows.add_anchor_sequences(reference_file)

    def test_interval_bed(self):
        bed = self.windows.interval_bed()
        self.assertIsInstance(bed, BedTool)
        interval1, interval2 = bed
        self.assertEqual(interval1.chrom, "locus1")
        self.assertEqual(interval1.start, 10)
        self.assertEqual(interval1.stop, 15)
        self.assertEqual(interval1.strand, "+")
        self.assertEqual(interval1.fields[-1], "NAME=locus1_1")
        self.assertEqual(interval2.chrom, "locus2")
        self.assertEqual(interval2.start, 27)
        self.assertEqual(interval2.stop, 35)
        self.assertEqual(interval2.strand, "+")
        self.assertEqual(interval2.fields[-1], "NAME=locus2_1")

    def test_get_window(self):
        window1 = self.windows.get_window("locus1_1")
        result = Window("locus1", Anchor("locus1_1", 1, 10), Anchor("locus1_1", 15, 20))
        self.assertEqual(window1, result)

    def test_get_window_not_found_raises(self):
        message = r"Could not find window for locus foo"
        with self.assertRaisesRegex(ValueError, expected_regex=message):
            self.windows.get_window("foo")


class TestBam(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        self.tempdir_path = Path(self.tempdir.name)
        self.test_bam_file = self.tempdir_path / "test.bam"
        with self.test_bam_file.open("wb") as open_bam:
            open_bam.write(sample_bam())
        self.bam = Bam(self.test_bam_file)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_sort(self):
        output_file = self.tempdir_path / "sorted.bam"
        output_file.touch()
        sorted_bam = self.bam.sort(output_file=output_file)
        self.assertIsInstance(sorted_bam, Bam)
        bam_file = pysam.AlignmentFile(sorted_bam._file, "rb")
        result = [
            "read2\t128\ttarget1\t1\t255\t4M\t*\t0\t0\tAACC\tIIII",
            "read1\t128\ttarget2\t1\t255\t4M\t*\t0\t0\tACGT\tIIII",
            "read3\t128\ttarget2\t1\t255\t2M1D1M\t*\t0\t0\tACT\tIII",
            "read4\t128\ttarget3\t1\t255\t4M\t*\t0\t0\tTTGG\tIIII",
        ]
        for read, result_read in zip(bam_file.fetch(), result):
            self.assertEqual(read.to_string(), result_read)
        genome_file_result = "target1\t100\ntarget2\t200\ntarget3\t300\n"
        with sorted_bam._genome_file.open("r") as genome_file:
            self.assertMultiLineEqual(genome_file.read(), genome_file_result)

        # Without target file
        with mock.patch("smap.haplotype_window.haplotype_window.Path") as mocked_path:
            created_path = mocked_path()
            mocked_path.return_value = created_path
            created_path.with_suffix.return_value = output_file
            output_file.unlink()
            sorted_bam = self.bam.sort()
            self.assertTrue(output_file.exists())
            bam_file = pysam.AlignmentFile(output_file, "rb")
            for read, result_read in zip(bam_file.fetch(), result):
                self.assertEqual(read.to_string(), result_read)

    def test_sort_reads_per_window_not_sorted(self):
        window1 = Window(
            "target1", Anchor("target1_1", 1, 2), Anchor("target1_1", 5, 10)
        )
        window2 = Window(
            "target2", Anchor("target2_1", 1, 2), Anchor("target2_1", 5, 10)
        )
        windows = Windows([window1, window2])
        logger = logging.getLogger()
        with self.assertLogs(logger) as logger_cm:
            sorted_reads = self.bam.sort_read_ids_per_window(windows)
        logged_message = logger_cm.output
        self.assertEqual(
            logged_message,
            [
                "INFO:Haplotype:4 reads parsed from original .fastq, "
                "of which 3 were assigned to a window."
            ],
        )
        result = {
            "read2": [
                (
                    Window(
                        "target1", Anchor("target1_1", 1, 2), Anchor("target1_1", 5, 10)
                    ),
                    "+",
                )
            ],
            "read1": [
                (
                    Window(
                        "target2", Anchor("target2_1", 1, 2), Anchor("target2_1", 5, 10)
                    ),
                    "+",
                )
            ],
            "read3": [
                (
                    Window(
                        "target2", Anchor("target2_1", 1, 2), Anchor("target2_1", 5, 10)
                    ),
                    "+",
                )
            ],
        }
        self.assertDictEqual(sorted_reads, result)

    def test_sort_reads_per_window_sorted_bam(self):
        window1 = Window(
            "target1", Anchor("target1_1", 1, 2), Anchor("target1_1", 5, 10)
        )
        window2 = Window(
            "target2", Anchor("target2_1", 1, 2), Anchor("target2_1", 5, 10)
        )
        windows = Windows([window1, window2])
        output_file = self.tempdir_path / "sorted.bam"
        sorted_bam = self.bam.sort(output_file)
        logger = logging.getLogger()
        with self.assertLogs(logger) as logger_cm:
            sorted_reads = sorted_bam.sort_read_ids_per_window(windows)
        logged_message = logger_cm.output
        self.assertEqual(
            logged_message,
            [
                "INFO:Haplotype:4 reads parsed from original .fastq, "
                "of which 3 were assigned to a window."
            ],
        )
        result = {
            "read2": [
                (
                    Window(
                        "target1", Anchor("target1_1", 1, 2), Anchor("target1_1", 5, 10)
                    ),
                    "+",
                )
            ],
            "read1": [
                (
                    Window(
                        "target2", Anchor("target2_1", 1, 2), Anchor("target2_1", 5, 10)
                    ),
                    "+",
                )
            ],
            "read3": [
                (
                    Window(
                        "target2", Anchor("target2_1", 1, 2), Anchor("target2_1", 5, 10)
                    ),
                    "+",
                )
            ],
        }
        self.assertDictEqual(sorted_reads, result)


class TestSampleMerging(unittest.TestCase):
    def test_merge_empty_raises(self):
        expected_message = (
            r"No reads were counted for any of the samples\. Please check your input\."
        )
        with self.assertRaisesRegex(ValueError, expected_message):
            merge_samples([pd.DataFrame([]), pd.DataFrame([])])

    def test_mergin(self):
        sample1_index = pd.MultiIndex.from_tuples(
            [
                ("target2", "target2_1", "CG"),
                ("target2", "target2_1", "C"),
                ("target5", "target5_1", "C"),
            ],
            names=["Reference", "Locus", "Haplotypes"],
        )
        sample1 = pd.DataFrame(
            [1, 0, 1], index=sample1_index, columns=["sample1"], dtype=pd.UInt8Dtype()
        )
        sample2_index = pd.MultiIndex.from_tuples(
            [
                ("target2", "target2_1", "CG"),
                ("target2", "target2_1", "C"),
                ("target1", "target1_1", "A"),
            ],
            names=["Reference", "Locus", "Haplotypes"],
        )
        sample2 = pd.DataFrame(
            [3, 1, 5], index=sample2_index, columns=["sample2"], dtype=pd.UInt8Dtype()
        )
        result = merge_samples([sample1, sample2])
        expected_index = pd.MultiIndex.from_tuples(
            [
                ("target2", "target2_1", "CG"),
                ("target2", "target2_1", "C"),
                ("target5", "target5_1", "C"),
                ("target1", "target1_1", "A"),
            ],
            names=INDEX_COLUMNS,
        )
        expected = pd.DataFrame(
            [[1, 3], [0, 1], [1, pd.NA], [pd.NA, 5]],
            dtype=pd.UInt8Dtype(),
            index=expected_index,
            columns=["sample1", "sample2"],
        )

        pd.testing.assert_frame_equal(expected, result)


class TestFastq(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        self.tempdir_path = Path(self.tempdir.name)
        self.test_fastq_file = self.tempdir_path / "test.fastq"
        with self.test_fastq_file.open("w") as open_fastq:
            open_fastq.write(sample_fastq())
        self.fastq = Fastq(self.test_fastq_file)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_count_sequences_per_window(self):
        window1 = Window(
            "target1",
            Anchor("target1_1", 1, 2, seq="A"),
            Anchor("target1_1", 5, 10, seq="C"),
        )
        window2 = Window(
            "target2",
            Anchor("target2_1", 1, 2, seq="A"),
            Anchor("target2_1", 5, 10, seq="T"),
        )

        lookup = {
            "read2": [(window1, "+")],
            "read1": [(window2, "+")],
            "read3": [(window2, "+"), (window2, "-")],
        }
        result_counts = self.fastq.count_sequences_per_window(lookup, error_rate=0)
        counts = {window1: {"A": 1}, window2: {"CG": 1, "C": 1, "G": 1}}
        self.assertDictEqual(result_counts, counts)


class TestMainFunctions(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        self.tempdir_path = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_filter_gff_loci(self):
        gff = dedent(
            """\
                    locus1	SMAP	forward_anchor	1	10	.	+	.	NAME=locus1_1
                    locus1	SMAP	reverse_anchor	15	20	.	+	.	NAME=locus1_1
                    locus2	SMAP	forward_anchor	20	27	.	+	.	NAME=locus2_1
                    locus2	SMAP	reverse_anchor	35	40	.	+	.	NAME=locus2_1
                    """
        )
        gff_file = self.tempdir_path / "test.gff"
        with gff_file.open("w") as open_gff:
            open_gff.write(gff)
        write_to = self.tempdir_path / "filtered.gff"
        filter_gff_loci(gff_file, str(write_to), [("locus2_1",)])
        result = (
            "locus2\tSMAP\tforward_anchor\t20\t27\t.\t+\t.\tNAME=locus2_1;\n"
            "locus2\tSMAP\treverse_anchor\t35\t40\t.\t+\t.\tNAME=locus2_1;\n"
        )
        with write_to.open("r") as filtered_gff:
            self.assertMultiLineEqual(filtered_gff.read(), result)

    def test_match_bam_with_fastq(self):
        fastqs = [Fastq("b.fastq"), Fastq("a.fastq"), Fastq("c.fastq")]
        bams = [Bam("a.bam"), Bam("b.bam"), Bam("c.bam")]
        res = match_bam_with_fastq(bams, fastqs)
        expected = [
            (Bam("a.bam"), Fastq("a.fastq")),
            (Bam("b.bam"), Fastq("b.fastq")),
            (Bam("c.bam"), Fastq("c.fastq")),
        ]
        self.assertEqual(res, expected)

    def test_match_bam_with_fastq_similar_name(self):
        fastqs = [Fastq("825_1.fq"), Fastq("825_11.fq")]
        bams = [Bam("825_1.bam"), Bam("825_11.bam")]
        expected = [
            (Bam("825_1.bam"), Fastq("825_1.fq")),
            (Bam("825_11.bam"), Fastq("825_11.fq")),
        ]
        res = match_bam_with_fastq(bams, fastqs)
        self.assertEqual(res, expected)

    def test_match_bam_with_fastq_extension(self):
        fastqs = [Fastq("825_1.fq.gz"), Fastq("825_11.fq.bz2")]
        bams = [Bam("825_1.bam"), Bam("825_11.bam")]
        expected = [
            (Bam("825_1.bam"), Fastq("825_1.fq.gz")),
            (Bam("825_11.bam"), Fastq("825_11.fq.bz2")),
        ]
        res = match_bam_with_fastq(bams, fastqs)
        self.assertEqual(res, expected)

    def test_match_bam_with_fastq_no_match_raises(self):
        fastqs = [Fastq("b.fastq"), Fastq("a.fastq")]
        bams = [Bam("a.bam"), Bam("b.bam"), Bam("c.bam")]
        message = ".bam c file could not be matched with any .fastq file."
        with self.assertRaisesRegex(ValueError, message):
            match_bam_with_fastq(bams, fastqs)

    def test_add_guide_targets(self):
        guides_fasta = dedent(
            """\
                              >guide1
                              AAAAAAA
                              >guide2
                              AATT
                              """
        )
        counts_index = pd.MultiIndex.from_tuples(
            [("1", "locus1", "ACGT"), ("1", "locus1", "AGT"), ("1", "locus2", "AATT")],
            names=INDEX_COLUMNS,
        )
        counts = pd.DataFrame({"bam1": [50, 50, 100]}, index=counts_index)
        guide_path = self.tempdir_path / "temp.gff"
        with guide_path.open("w") as open_fasta:
            open_fasta.write(guides_fasta)
        result = add_guide_targets(counts, guide_path)
        expected_index = pd.MultiIndex.from_tuples(
            [
                ("1", "locus1", "ACGT", "locus1"),
                ("1", "locus1", "AGT", "locus1"),
                ("1", "locus2", "AATT", "guide2"),
            ],
            names=INDEX_COLUMNS + ["Target"],
        )
        expected = pd.DataFrame(counts, index=expected_index)
        pd.testing.assert_frame_equal(expected, result)

    def test_add_guide_targets_guide_file_does_not_exist_raises(self):
        counts_index = pd.MultiIndex.from_tuples(
            [("1", "locus1", "ACGT"), ("1", "locus1", "AGT"), ("1", "locus2", "AATT")],
            names=INDEX_COLUMNS,
        )
        counts = pd.DataFrame({"bam1": [50, 50, 100]}, index=counts_index)
        message = r"foo does not exist or is not a file\."
        with self.assertRaisesRegex(FileNotFoundError, expected_regex=message):
            add_guide_targets(counts, Path("foo"))

    def test_counts_to_dataframe(self):
        window1 = Window(
            "target1",
            Anchor("target1_1", 1, 2, seq="A"),
            Anchor("target1_1", 5, 10, seq="C"),
        )
        window2 = Window(
            "target2",
            Anchor("target2_1", 1, 2, seq="A"),
            Anchor("target2_1", 5, 10, seq="T"),
        )

        counts = {window1: {"A": 1}, window2: {"CG": 1, "C": 2}}
        result = counts_to_dataframe("bam1", counts)
        expected_index = pd.MultiIndex.from_tuples(
            [
                ("target1", "target1_1", "A"),
                ("target2", "target2_1", "CG"),
                ("target2", "target2_1", "C"),
            ],
            names=INDEX_COLUMNS,
        )

        expected = pd.DataFrame(
            {"bam1": [1, 1, 2]}, index=expected_index, dtype=pd.UInt8Dtype()
        )
        pd.testing.assert_frame_equal(expected, result)

    def test_counts_to_dataframe_no_counts_for_sample(self):
        window1 = Window(
            "target1",
            Anchor("target1_1", 1, 2, seq="A"),
            Anchor("target1_1", 5, 10, seq="C"),
        )
        window2 = Window(
            "target2",
            Anchor("target2_1", 1, 2, seq="A"),
            Anchor("target2_1", 5, 10, seq="T"),
        )

        counts = {window1: {}, window2: {}}
        result = counts_to_dataframe("bam1", counts)
        expected_index = pd.MultiIndex.from_tuples([], names=INDEX_COLUMNS)
        expected = pd.DataFrame(
            {"bam1": []}, index=expected_index, dtype=pd.UInt8Dtype()
        )
        pd.testing.assert_frame_equal(expected, result)

    def test_fasta_to_dict(self):
        fasta = dedent(
            """\
                       >guide1
                       AAAAAAA
                       >guide2
                       AATT
                       """
        )
        test_fasta_path = self.tempdir_path / "temp.fa"
        with test_fasta_path.open("w") as open_fasta:
            open_fasta.write(fasta)
        result = fasta_to_dict(test_fasta_path)
        expected = {"AAAAAAA": "guide1", "AATT": "guide2"}
        self.assertDictEqual(result, expected)


class TestFilePathWrapper(TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        self.tempdir_path = Path(self.tempdir.name)
        self.file1 = self.tempdir_path / "file1.ext1.ext2"
        self.file2 = self.tempdir_path / "file2.ext1.ext2"
        self.same_as_file1 = self.tempdir_path / "file1.ext1.ext2"
        self.file1_wrapper = _FilePathWrapper(self.file1)
        self.file2_wrapper = _FilePathWrapper(self.file2)
        self.same_as_file1_wrapper = _FilePathWrapper(self.same_as_file1)
        self.file1.touch()
        self.file2.touch()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_equality(self):
        self.assertEqual(self.file1_wrapper, self.same_as_file1_wrapper)

    def test_hashable(self):
        self.assertIsInstance(self.file1_wrapper, Hashable)
        test_set = set([self.file1_wrapper, self.same_as_file1_wrapper])
        self.assertSetEqual(test_set, set([self.file1_wrapper]))

    def test_find_in_directory(self):
        res = _FilePathWrapper.find_in_directory(self.tempdir_path, [".ext1.ext2"])
        self.assertCountEqual([self.file1_wrapper, self.file2_wrapper], res)
        res = _FilePathWrapper.find_in_directory(self.tempdir_path, [".ext2"])
        self.assertCountEqual([self.file1_wrapper, self.file2_wrapper], res)

    def test_find_in_directory_not_exists_raises(self):
        message = r"Directory foo does not exist or is not a directory\."
        with self.assertRaisesRegex(FileNotFoundError, expected_regex=message):
            _FilePathWrapper.find_in_directory(Path("foo"), [".ext1.ext2"])

    def test_find_in_directory_no_files_found_raises(self):
        message = rf"No files with extension foo were found in directory {self.tempdir_path!s}!"
        with self.assertRaisesRegex(ValueError, expected_regex=message):
            _FilePathWrapper.find_in_directory(self.tempdir_path, ["foo"])

    def test_stem(self):
        res = self.file1_wrapper.stem
        self.assertEqual(res, "file1.ext1")


class TestWorkerFunction(TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        self.tempdir_path = Path(self.tempdir.name)
        self.test_bam_file = self.tempdir_path / "test.bam"
        with self.test_bam_file.open("wb") as open_bam:
            open_bam.write(sample_bam())
        self.bam = Bam(self.test_bam_file)

        self.test_fastq_file = self.tempdir_path / "test.fastq"
        with self.test_fastq_file.open("w") as open_fastq:
            open_fastq.write(sample_fastq())
        self.fastq = Fastq(self.test_fastq_file)

        self.window1 = Window(
            "target1", Anchor("target1_1", 1, 2), Anchor("target1_1", 5, 10)
        )
        self.window2 = Window(
            "target2", Anchor("target2_1", 1, 2), Anchor("target2_1", 5, 10)
        )
        self.window2.upstream_border.seq = "A"
        self.window2.downstream_border.seq = "T"
        self.window1.upstream_border.seq = "A"
        self.window1.downstream_border.seq = "C"
        self.windows = Windows([self.window1, self.window2])

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @mock.patch("smap.haplotype_window.haplotype_window.Bam", autospec=True)
    @mock.patch("smap.haplotype_window.haplotype_window.Fastq", autospec=True)
    def test_counting_worker(self, mocked_fastq, mocked_bam):
        sorted_reads = {
            "read2": [(self.window1, "+")],
            "read1": [(self.window2, "+")],
            "read3": [(self.window2, "+")],
        }
        counts = {self.window2: {"CG": 1, "C": 1}, self.window1: {"A": 1}}
        mocked_bam.sort_read_ids_per_window.return_value = sorted_reads
        type(mocked_bam).stem = mock.PropertyMock(return_value="test")
        mocked_fastq.count_sequences_per_window.return_value = counts
        res = counting_worker(mocked_bam, mocked_fastq, self.windows, error_rate=0)
        exp_index = pd.MultiIndex.from_tuples(
            [
                ("target2", "target2_1", "CG"),
                ("target2", "target2_1", "C"),
                ("target1", "target1_1", "A"),
            ],
            names=["Reference", "Locus", "Haplotypes"],
        )
        exp = pd.DataFrame(
            [1, 1, 1], index=exp_index, columns=["test"], dtype=pd.UInt8Dtype()
        )
        pd.testing.assert_frame_equal(res, exp)
        mocked_bam.sort_read_ids_per_window.assert_called_once_with(self.windows)
        mocked_fastq.count_sequences_per_window.assert_called_once_with(sorted_reads, 0)


class TestMain(TestCase):
    def test_argument_parsing(self):
        arguments = [
            "/foo/reference.fa",
            "/foo/windows.gff",
            "/foo/RG/",
            "/foo/RG/",
            "--discrete_calls",
            "dominant",
            "--dosage_filter",
            "2",
            "--frequency_interval_bounds",
            "10",
            "--plot",
            "nothing",
            "-q",
            "20",
            "-c",
            "10",
            "-p",
            "40",
            "-f",
            "5.5",
            "--memory_efficient",
        ]
        parsed_arguments = parse_args(arguments)
        expected = Namespace(
            alignments_dir=Path("/foo/RG/"),
            borders=Path("/foo/windows.gff"),
            discrete_calls="dominant",
            dosage_filter=2,
            frequency_bounds=[10.0],
            genome=Path("/foo/reference.fa"),
            guides=None,
            locus_correctness_filter=None,
            mask_frequency=0,
            max_distinct_haplotypes=inf,
            max_read_count=inf,
            memory_efficient=True,
            max_error=0,
            min_distinct_haplotypes=0,
            min_haplotype_frequency=5.5,
            min_read_count=10,
            minimum_mapping_quality=20,
            out="",
            plot=PlotLevel("nothing"),
            plot_type="png",
            processes=40,
            sample_dir=Path("/foo/RG"),
            undefined_representation=pd.NA,
            write_sorted_sequences=False,
        )
        self.assertEqual(parsed_arguments, expected)

    def test_discrete_calling_requires_bounds(self):
        arguments = [
            "/foo/reference.fa",
            "/foo/windows.gff",
            "/foo/RG/",
            "/foo/RG/",
            "--discrete_calls",
            "dominant",
        ]
        msg = r"If discrete calling is enabled, please define the interval bounds using the frequency_bounds parameter \(see --help for more information\)\."
        with self.assertRaisesRegex(ValueError, msg):
            parse_args(arguments)

    def test_max_error_bounds(self):
        arguments = [
            "/foo/reference.fa",
            "/foo/windows.gff",
            "/foo/RG/",
            "/foo/RG/",
            "--max_error",
        ]
        msg = r"The value for --max_error must be a value between 0 and 1 \(but not exactly 1\)"
        for arg_value in ("-1", "2"):
            call = arguments + [arg_value]
            with self.assertRaisesRegex(ValueError, msg):
                parse_args(call)
