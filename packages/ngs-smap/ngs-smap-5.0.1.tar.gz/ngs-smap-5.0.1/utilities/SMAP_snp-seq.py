#!usr/bin/python3

# ===============================================================================
# SMAP_snp-seq.py
# ===============================================================================

# Yves BAWIN March 2021
# Python script for primer design with primer3.
#
# ===============================================================================
# Import modules
# ===============================================================================

import argparse
import primer3
from datetime import datetime
from Bio import SeqIO
from natsort import natsorted
import pandas as pd

# ===============================================================================
# Parse arguments
# ===============================================================================

# Create an ArgumentParser object
parser = argparse.ArgumentParser(
    description="Design primers with primer3 starting from a VCF "
    "file and a reference genome sequence."
)

"""Mandatory arguments"""
parser.add_argument(
    "--vcf", type=str, help="Name of the VCF file in the input directory with SNPs."
)
parser.add_argument(
    "--reference",
    type=str,
    help="Directory and name of the reference genome sequence (in FASTA format).",
)

"""Input data options"""
parser.add_argument(
    "-i",
    "--input_directory",
    type=str,
    default=".",
    help="Input directory [current directory].",
)
parser.add_argument(
    "-r",
    "--regions",
    type=str,
    default=None,
    help="Name of the BED file in the input directory containing "
    "the genomic coordinates of regions wherein primers must "
    "be designed [no BED file provided].",
)
parser.add_argument(
    "--target_vcf",
    type=str,
    default=None,
    help="Name of the VCF file in the input directory containing "
    "target SNPs [no VCF file with target SNPs provided].",
)
parser.add_argument(
    "--reference_vcf",
    type=str,
    default=None,
    help="Name of the VCF file in the input directory containing "
    "non-polymorphic differences between the reference genome "
    "sequence and the samples for primer design [no VCF file with "
    "reference genome differences provided].",
)

"""Analysis options"""
parser.add_argument(
    "-d",
    "--variant_distance",
    type=int,
    default=500,
    help="Maximum distance (in bp) between two variants to be included "
    "in the same template [500].",
)
parser.add_argument(
    "-t",
    "--target_size",
    type=int,
    default=10,
    help="Maximum size (in bp) of a target region [10].",
)
parser.add_argument(
    "-u",
    "--target_distance",
    type=int,
    default=0,
    help="Minimum distance (in bp) between two target regions in a template [0].",
)
parser.add_argument(
    "-min",
    "--minimum_amplicon_size",
    type=int,
    default=120,
    help="Minimum size of an amplicon (including primers) in bp [120].",
)
parser.add_argument(
    "-max",
    "--maximum_amplicon_size",
    type=int,
    default=140,
    help="Maximum size of an amplicon (including primers) in bp [140].",
)
parser.add_argument(
    "--offset",
    type=int,
    default=0,
    help="Size of the offset at the 5' and 3' end of each region. "
    "Variants in the offsets are not tagged as targets for primer design "
    "[0, all variants are potential targets].",
)
parser.add_argument(
    "-minp",
    "--minimum_primer_size",
    type=int,
    default=18,
    help="Minimum size (in bp) of a primer [18].",
)
parser.add_argument(
    "-maxp",
    "--maximum_primer_size",
    type=int,
    default=27,
    help="Maximum size (in bp) of a primer [27].",
)
parser.add_argument(
    "-optp",
    "--optimal_primer_size",
    type=int,
    default=20,
    help="Optimal size (in bp) of a primer [20].",
)
parser.add_argument(
    "-max_misp",
    "--maximum_mispriming",
    type=int,
    default=12,
    help="Maximum allowed weighted similarity of a primer with the same template "
    "and other templates [12].",
)
parser.add_argument(
    "-maxn",
    "--maximum_unknown_nucleotides",
    type=int,
    default=0,
    help="Maximum number of unknown nucleotides (N) in a primer sequence [0].",
)
parser.add_argument(
    "-ex",
    "--region_extension",
    type=int,
    default=0,
    help="Extend regions in the BED file provided via the --regions option at "
    "their 5' end 3' end with the provided value [0, no region extension].",
)
parser.add_argument(
    "--retain_overlap",
    dest="remove_overlap",
    action="store_false",
    help="Retain overlap in template sequences among regions [overlap in template "
    "sequences is removed].",
)
parser.add_argument(
    "--split_template",
    dest="split_templates",
    action="store_true",
    help="Split the regions in the BED file provided via the --regions option in m"
    "ultiple templates based on the variant_distance [regions are not split].",
)

"""Output data options"""
parser.add_argument(
    "-o",
    "--output_directory",
    type=str,
    default=".",
    help="Output directory (default = current directory).",
)
parser.add_argument(
    "-b",
    "--border_length",
    type=int,
    default=10,
    help="Border size used in the input file of SMAP haplotype-window [10].",
)
parser.add_argument(
    "-s",
    "--suffix",
    type=str,
    default="set_1",
    help="Suffix added to output files [set_1].",
)

# Parse arguments to a dictionary
args = vars(parser.parse_args())

# ===============================================================================
# Functions
# ===============================================================================


def print_date():
    print("-------------------")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("-------------------\n")
    return


"""Conversion functions"""


def fasta2dict(file=args["reference"]):
    return SeqIO.to_dict(SeqIO.parse(open(file), "fasta"))


def vcf2dict(file, in_d=args["input_directory"], store_alleles=False):
    vcf_dict = dict()
    for line in open("{}/{}".format(in_d, file)):
        if not line.startswith("#"):
            line = line.split("\t")
            pos = int(line[1]) - 1
            if store_alleles:
                pos = [pos, line[4]]
            if line[0] not in vcf_dict:
                vcf_dict[line[0]] = [pos]
            else:
                vcf_dict[line[0]].append(pos)
    return vcf_dict


def bed2dict(file, in_d=args["input_directory"]):
    bed_dict = dict()
    for line in open("{}/{}".format(in_d, file)):
        line = line.rstrip().split("\t")
        start, end = int(line[1]), int(line[2])
        assert start < end, (
            "The start coordinate of region {}:{}-{} in the BED file "
            "defined by the --regions option is larger than the end coordinate. "
            "Please adjust the BED so that the start coordinate of each region "
            "is smaller than the end coordinate.".format(line[0], line[1], line[2])
        )
        if line[0] not in bed_dict:
            bed_dict[line[0]] = [(start, end)]
        else:
            bed_dict[line[0]].append((start, end))
    return bed_dict


def dict2fasta(
    d, name, vcf=args["vcf"], out_d=args["output_directory"], s=args["suffix"]
):
    new_file = open("{}/{}_{}.fasta".format(out_d, name, s), "w+")
    for name in natsorted(list(d.keys())):
        print(">{}\n{}".format(name, d[name]), file=new_file)
    return


def dict2dataframe(primer_dict, out_d=args["output_directory"], s=args["suffix"]):
    primer_list = list()
    colnames = ["Primer_ID", "Orientation", "Start", "Stop", "Seq", "Locus_ID"]
    for id in primer_dict.keys():
        primer_list.append(
            pd.DataFrame(
                [
                    [
                        id + "_F",
                        "Forward",
                        primer_dict[id]["PrimerCoordinates"][0][0],
                        primer_dict[id]["PrimerCoordinates"][0][1],
                        primer_dict[id]["PrimerSequences"][0],
                        id + "_+",
                    ],
                    [
                        id + "_R",
                        "Reverse",
                        primer_dict[id]["PrimerCoordinates"][1][0],
                        primer_dict[id]["PrimerCoordinates"][1][1],
                        primer_dict[id]["PrimerSequences"][1],
                        id + "_+",
                    ],
                ],
                columns=colnames,
            )
        )
    df = pd.concat(primer_list, ignore_index=True)
    df.to_csv("{}/Primers_{}.txt".format(out_d, s), sep="\t", index=False)
    return


def dict2bed(primer_dict, name, out_d=args["output_directory"], s=args["suffix"]):
    new_bed = open("{}/{}_{}.bed".format(out_d, name, s), "w+")
    new_gff = open("{}/{}_{}.gff".format(out_d, name, s), "w+")
    for id in natsorted(list(primer_dict.keys())):
        chrom = id.split(":")[0]
        if name == "Primers":
            print(
                "{}\t{}\t{}\t{}_F\t{}_+".format(
                    chrom,
                    primer_dict[id]["PrimerCoordinates"][0][0] - 1,
                    primer_dict[id]["PrimerCoordinates"][0][1],
                    id,
                    id,
                ),
                file=new_bed,
            )
            print(
                "{}\t{}\t{}\t{}_R\t{}_+".format(
                    chrom,
                    primer_dict[id]["PrimerCoordinates"][1][0] - 1,
                    primer_dict[id]["PrimerCoordinates"][1][1],
                    id,
                    id,
                ),
                file=new_bed,
            )
            print(
                "{}\tPrimer_design\tF-primer\t{}\t{}\t.\t+\t.\tName={}_F;Locus={}_+".format(
                    chrom,
                    primer_dict[id]["PrimerCoordinates"][0][0],
                    primer_dict[id]["PrimerCoordinates"][0][1],
                    id,
                    id,
                ),
                file=new_gff,
            )
            print(
                "{}\tPrimer_design\tR-primer\t{}\t{}\t.\t-\t.\tName={}_R;Locus={}_+".format(
                    chrom,
                    primer_dict[id]["PrimerCoordinates"][1][0],
                    primer_dict[id]["PrimerCoordinates"][1][1],
                    id,
                    id,
                ),
                file=new_gff,
            )
        else:
            print(
                "{}\t{}\t{}\t{}_Amplicon\t{}_+".format(
                    chrom,
                    primer_dict[id]["PrimerCoordinates"][0][0] - 1,
                    primer_dict[id]["PrimerCoordinates"][1][1],
                    id,
                    id,
                ),
                file=new_bed,
            )
            print(
                "{}\tPrimer_design\tAmplicon\t{}\t{}\t.\t+\t.\tName={}_Amplicon;Locus={}_+".format(
                    chrom,
                    primer_dict[id]["PrimerCoordinates"][0][0],
                    primer_dict[id]["PrimerCoordinates"][1][1],
                    id,
                    id,
                ),
                file=new_gff,
            )
    return


def dict2smap(
    primer_dict,
    name,
    out_d=args["output_directory"],
    b=args["border_length"],
    s=args["suffix"],
):
    if name == "Primers":
        new = open("SMAP_haplotype_window_{}.gff".format(s), "w+")
    else:
        new = open("SMAP_haplotype_sites_{}.bed".format(s), "w+")
    #    i = 1
    for id in natsorted(list(primer_dict.keys())):
        chrom = id.split(":")[0]
        if name == "Primers":
            print(
                "{}\tSMAP\tborder_up\t{}\t{}\t.\t+\t.\tName={}".format(
                    chrom,
                    primer_dict[id]["PrimerCoordinates"][0][0] - b,
                    primer_dict[id]["PrimerCoordinates"][0][1],
                    "{}:{}-{}_+".format(
                        chrom,
                        primer_dict[id]["PrimerCoordinates"][0][1] + 1,
                        primer_dict[id]["PrimerCoordinates"][1][0] - 1,
                    ),
                ),
                file=new,
            )
            print(
                "{}\tSMAP\tborder_down\t{}\t{}\t.\t+\t.\tName={}".format(
                    chrom,
                    primer_dict[id]["PrimerCoordinates"][1][0],
                    primer_dict[id]["PrimerCoordinates"][1][1] + b,
                    "{}:{}-{}_+".format(
                        chrom,
                        primer_dict[id]["PrimerCoordinates"][0][1] + 1,
                        primer_dict[id]["PrimerCoordinates"][1][0] - 1,
                    ),
                ),
                file=new,
            )
        #            i += 1
        else:
            print(
                "{}\t{}\t{}\t{}\t.\t+\t{},{}\t.\t2\tHiPlex_{}".format(
                    chrom,
                    primer_dict[id]["PrimerCoordinates"][0][1],
                    primer_dict[id]["PrimerCoordinates"][1][0] - 1,
                    "{}:{}-{}_+".format(
                        chrom,
                        primer_dict[id]["PrimerCoordinates"][0][1] + 1,
                        primer_dict[id]["PrimerCoordinates"][1][0] - 1,
                    ),
                    primer_dict[id]["PrimerCoordinates"][0][1] + 1,
                    primer_dict[id]["PrimerCoordinates"][1][0] - 1,
                    s,
                ),
                file=new,
            )
    return


"""Set functions"""


def set_template(
    vcf_dict,
    ref_dict,
    regions_dict,
    target_vcf_dict,
    reference_vcf_dict,
    offset=args["offset"],
    min=args["minimum_amplicon_size"],
):
    template_dict, target_dict = dict(), dict()
    for chrom, regions in regions_dict.items():
        for region in regions:
            start, end = region
            id = "{}:{}-{}".format(chrom, start + 1, end)
            if end - start >= min:
                variants = sorted([v for v in vcf_dict[chrom] if start <= v < end])
                if target_vcf_dict:
                    targets = [
                        v
                        for v in target_vcf_dict[chrom]
                        if start + offset <= v < end - offset
                    ]
                else:
                    targets = [
                        v for v in variants if start + offset <= v < end - offset
                    ]
                if len(targets) > 0:
                    seq = ref_dict[chrom][start:end].upper()
                    if reference_vcf_dict:
                        ref_diff_dict = {
                            p[0]: p[1]
                            for p in reference_vcf_dict[chrom]
                            if start <= p[0] < end
                        }
                        seq = [
                            n
                            if start + i not in ref_diff_dict.keys()
                            else ref_diff_dict[start + i]
                            for i, n in enumerate(seq)
                        ]
                    seq = [
                        n
                        if n not in "YRSWKMDBHV" and i + start not in variants
                        else "N"
                        for i, n in enumerate(seq)
                    ]
                    template_dict[id] = "".join(seq)
                    target_dict[id] = set_target(start, targets)
            else:
                print(
                    " \t* The length of region {} was smaller than the defined minimum "
                    "length of an amplicon. Consequently, the region was not considered "
                    "for primer design. Please check your settings if you want to keep "
                    "this region in your dataset.".format(id)
                )
    dict2fasta(template_dict, "Templates")
    return template_dict, target_dict


def set_region(vcf_dict, r_dict, v_dist=args["variant_distance"]):
    regions_dict = dict()
    for chrom, regions in r_dict.items():
        if chrom in vcf_dict:
            regions_dict[chrom] = []
            for region in regions:
                start, end = region
                variants = sorted([x for x in vcf_dict[chrom] if start <= x < end])
                i, i0 = 0, 0
                while i < len(variants) - 1:
                    while (
                        i < len(variants) - 1
                        and variants[i + 1] - variants[i] <= v_dist
                    ):
                        i += 1
                    else:
                        regions_dict[chrom].append(
                            (
                                max(start, variants[i0] - round(v_dist / 2)),
                                min(end, variants[i] + round(v_dist / 2)),
                            )
                        )
                        i += 1
                        i0 = i
                if i == len(variants) - 1:
                    regions_dict[chrom].append(
                        (
                            max(start, variants[i0] - round(v_dist / 2)),
                            min(end, variants[i] + round(v_dist / 2)),
                        )
                    )
    return regions_dict


def set_target(
    start, variants, t_size=args["target_size"], t_dist=args["target_distance"]
):
    i = 0
    target_list = list()
    while i < len(variants):
        t = [n for n in variants if 0 <= n - variants[i] <= t_size]
        target_list.append([t[0] - start, t[-1] - t[0] + 1])
        i += len(t)
        while i < len(variants) and variants[i] - t[-1] <= t_dist:
            i += 1
    return target_list


"""Primer design function"""


def design_primers(
    template_dict,
    target_dict,
    min=args["minimum_amplicon_size"],
    max=args["maximum_amplicon_size"],
    minp=args["minimum_primer_size"],
    maxp=args["maximum_primer_size"],
    optp=args["optimal_primer_size"],
    max_misp=args["maximum_mispriming"],
    maxn=args["maximum_unknown_nucleotides"],
):
    primers = dict()
    if optp < minp:
        optp = minp
        print(
            " \t* The optimal primer length was smaller than minimum primer length. "
            "Consequently, the optimal primer length was set equal to the minimum primer length "
            "(i.e. {} base pairs). "
            "Please change your primer length settings if you want to change "
            "the optimal primer length.".format(minp)
        )
    if optp > maxp:
        optp = maxp
        print(
            " \t* The optimal primer length was larger than maximum primer length. "
            "Consequently, the optimal primer length was set equal to the maximum primer length "
            "(i.e. {} base pairs). "
            "Please change your primer length settings if you want to change "
            "the optimal primer length.".format(maxp)
        )
    settings = {
        "PRIMER_PRODUCT_SIZE_RANGE": [[min, max]],
        "PRIMER_MAX_LIBRARY_MISPRIMING": max_misp,
        "PRIMER_MIN_SIZE": minp,
        "PRIMER_MAX_SIZE": maxp,
        "PRIMER_OPT_SIZE": optp,
        "PRIMER_NUM_RETURN": 1,
        "PRIMER_MAX_TEMPLATE_MISPRIMING": max_misp,
        "PRIMER_MAX_NS_ACCEPTED": maxn,
    }
    for id, seq in template_dict.items():
        targets = target_dict[id]
        SeqLib = {
            "SEQUENCE_ID": id,
            "SEQUENCE_TEMPLATE": seq,
            "SEQUENCE_TARGET": targets,
        }
        misprime_dict = {i: template_dict[i] for i in template_dict if i != id}
        results = primer3.design_primers(SeqLib, settings, misprime_lib=misprime_dict)
        nAmplicons = results["PRIMER_PAIR_NUM_RETURNED"]
        if nAmplicons > 0:
            # chrom, template_start, template_stop = id.split(':')[0], \ template_stop not used!
            #     int(id.split(':')[1].split('-')[0]), int(id.split(':')[1].split('-')[1])
            chrom, template_start = id.split(":")[0], int(
                id.split(":")[1].split("-")[0]
            )
            Fstart, Fstop = (
                template_start + results["PRIMER_LEFT_0"][0],
                template_start
                + results["PRIMER_LEFT_0"][0]
                + results["PRIMER_LEFT_0"][1]
                - 1,
            )
            Rstart, Rstop = (
                template_start
                + results["PRIMER_RIGHT_0"][0]
                - results["PRIMER_RIGHT_0"][1]
                + 1,
                template_start + results["PRIMER_RIGHT_0"][0],
            )
            Amp_id = "{}:{}-{}".format(chrom, Fstop + 1, Rstart - 1)
            primers[Amp_id] = {}
            primers[Amp_id]["PrimerSequences"] = [
                results["PRIMER_LEFT_0_SEQUENCE"],
                results["PRIMER_RIGHT_0_SEQUENCE"],
            ]
            primers[Amp_id]["PrimerCoordinates"] = [(Fstart, Fstop), (Rstart, Rstop)]
        else:
            print("\t- Region {} has no amplicon.".format(id))
    return primers


def extract_amplicons(primer_dict):
    seq_dict = dict()
    for id in primer_dict.keys():
        chrom = id.split(":")[0]
        start, end = id.split(":")[1].split("-")
        seq_dict[id] = "".join(
            [n for n in ref_dict[chrom][int(start) - 1 : int(end)].upper()]
        )
    dict2fasta(seq_dict, "Amplicons")
    return


# ===============================================================================
# Script
# ===============================================================================

if __name__ == "__main__":
    print_date()
    # Convert reference genome into dictionary.
    print(" * Reading input files ...")
    ref_dict = fasta2dict()

    # Convert VCF file(s) into dictionary.
    vcf_dict = vcf2dict(args["vcf"])

    if args["target_vcf"] is not None:
        target_vcf_dict = vcf2dict(args["target_vcf"])
    else:
        target_vcf_dict = None

    if args["reference_vcf"] is not None:
        reference_vcf_dict = vcf2dict(args["reference_vcf"], store_alleles=True)
    else:
        reference_vcf_dict = None

    # Get coordinates of regions for primer design.
    if args["regions"]:
        regions_dict = bed2dict(args["regions"])
        r_ext = args["region_extension"]
        if r_ext > 0:
            for chrom in regions_dict:
                for index, region in enumerate(regions_dict[chrom]):
                    regions_dict[chrom][index] = (
                        max(0, region[0] - r_ext),
                        min(len(ref_dict[chrom]), region[1] + r_ext),
                    )

        # Adjust partially overlapping regions and remove fully overlapping regions.
        if args["remove_overlap"]:
            print(" * Checking the overlap among regions ...")
            partial, full = list(), list()
            for chrom, regions in regions_dict.items():
                i = 0
                regions = sorted(regions)
                while i < len(regions) - 1:
                    start_1, end_1 = regions[i]
                    start_2, end_2 = regions[i + 1]
                    if end_1 <= start_2:
                        i += 1
                    else:
                        if end_2 > end_1 and start_2 > start_1:
                            partial.append(
                                [
                                    "{}:{}-{}".format(chrom, start_2 + 1, end_2),
                                    "{}:{}-{}".format(chrom, end_1 + 1, end_2),
                                ]
                            )
                            regions[i + 1] = (end_1, end_2)
                            i += 1
                        else:
                            if end_1 - start_1 >= end_2 - start_2:
                                full.append(
                                    "{}:{}-{}".format(chrom, start_2 + 1, end_2)
                                )
                                del regions[i + 1]
                            else:
                                full.append(
                                    "{}:{}-{}".format(chrom, start_1 + 1, end_1)
                                )
                                del regions[i]
                regions_dict[chrom] = regions
            if len(full) > 0:
                print(
                    " \t* {} region{} removed due to a complete overlap with another region:".format(
                        len(full), " was" if len(full) == 1 else "s were"
                    )
                )
                for region in full:
                    print(" \t\t- {}".format(region))
            if len(partial) > 0:
                print(
                    " \t* {} region{} shortened due to a partial overlap with another region:".format(
                        len(partial), " was" if len(partial) == 1 else "s were"
                    )
                )
                for region in partial:
                    print(" \t\t- {} -> {}".format(region[0], region[1]))
    else:
        regions_dict = {chrom: [(0, len(ref_dict[chrom]))] for chrom in ref_dict}

    # Create regions for primer design if no BED file is provided
    # or if the BED regions must be split.
    if not args["regions"] or args["split_templates"]:
        if target_vcf_dict:
            regions_dict = set_region(target_vcf_dict, regions_dict)
        else:
            regions_dict = set_region(vcf_dict, regions_dict)

    # Extract templates.
    print(" * Extracting template sequences ...")
    template_dict, target_dict = set_template(
        vcf_dict, ref_dict, regions_dict, target_vcf_dict, reference_vcf_dict
    )

    # Design primers.
    if len(target_dict) > 0:
        print(" * Designing primers using primer3 ...")
    primer_dict = design_primers(template_dict, target_dict)

    # Export amplicon data.
    if len(primer_dict) > 0:
        print(" * Exporting amplicon data ...")
        dict2dataframe(primer_dict)
        dict2bed(primer_dict, "Primers")
        dict2bed(primer_dict, "Amplicons")
        dict2smap(primer_dict, "Primers")
        dict2smap(primer_dict, "Amplicons")
        extract_amplicons(primer_dict)
    else:
        print(" * No primer pairs were designed.")

    print(" * Finished!\n")
    print_date()
