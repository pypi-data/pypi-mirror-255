#!/usr/bin/env python3

import argparse
import os
import time
import re
import pandas as pd
import numpy as np
import primer3
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import itertools
from Bio import SeqIO
from Bio.Seq import Seq
from collections import defaultdict
from statistics import mean
import logging
import sys
from typing import List


# Measure time needed to complete the script
start_time = time.time()
print(time.strftime("%H:%M:%S", time.localtime()))

# Pandas settings
pd.set_option(
    "display.max_rows",
    None,
    "display.max_columns",
    None,
    "display.max_colwidth",
    None,
    "display.width",
    0,
)

# Version
version = "1.6"


def parse_args(args):
    parser = get_arg_parser()
    parsed_args = parser.parse_args(args)

    if parsed_args.debug:
        parsed_args.logging_level = logging.DEBUG
    else:
        parsed_args.logging_level = logging.INFO
        sys.tracebacklimit = 0  # Suppress traceback information on errors.
    return parsed_args


def get_arg_parser():

    parser = argparse.ArgumentParser(
        description="Returns per gene specific amplicons with or without one or more guides"
    )

    # Positional arguments
    parser.add_argument(
        "FastaFile", help="Path to the Fasta file containing all genes to screen"
    )
    parser.add_argument(
        "GFFfile",
        help="Path to the GFF3 file containing at least the CDS feature with positions relative to the fasta file",
    )

    # Optional arguments
    parser.add_argument(
        "-g",
        "--gRNAfile",
        help="CRISPOR, FlashFry or other gRNA design program output file."
        "The CRISPOR and Flashfry file must contain a header and 12 columns. Check the manual for specifics",
    )

    parser.add_argument(
        "-gs",
        "--gRNAsource",
        help='What is the source of the gRNA file? Enter "CRISPOR", "FlashFry" or "other" (default = FlashFry)',
        default="FlashFry",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Name of the output files (default = SMAPdesign)",
        default="SMAPdesign",
    )

    parser.add_argument(
        "-na",
        "--numberAmplicons",
        help="The maximum number of non-overlapping amplicons per gene in the output (default = 2)",
        default=2,
        type=int,
    )

    parser.add_argument(
        "-ng",
        "--numbergRNAs",
        help="Maximum number of gRNAs to retain per amplicon (default = 2)",
        default=2,
        type=int,
    )

    parser.add_argument(
        "-minl",
        "--minimumAmpliconLength",
        help="The minimum length of the amplicons in base pairs (default = 120)",
        default=120,
        type=int,
    )

    parser.add_argument(
        "-maxl",
        "--maximumAmpliconLength",
        help="The maximum length of the amplicons in base pairs (default = 150)",
        default=150,
        type=int,
    )

    parser.add_argument(
        "-pmlm",
        "--primerMaxLibraryMispriming",
        help="The maximum allowed weighted similarity of a primer with any sequence in the target gene set (Primer3 setting) (dault = 12)",
        default=12,
        type=int,
    )

    parser.add_argument(
        "-ppmlm",
        "--primerPairMaxLibraryMispriming",
        help="The maximum allowed sum of similarities of a primer pair (one similarity for each primer) with any single sequence in the target gene set (Primer3 setting) (default = 24)",
        default=24,
        type=int,
    )

    parser.add_argument(
        "-pmtm",
        "--primerMaxTemplateMispriming",
        help="The maximum allowed similarity of a primer to ectopic sites in the template (Primer3 setting) (default = 12)",
        default=12,
        type=int,
    )

    parser.add_argument(
        "-ppmtm",
        "--primerPairMaxTemplateMispriming",
        help="The maximum allowed summed similarity of both primers to ectopic sites in the template (Primer3 setting) (default = 24)",
        default=24,
        type=int,
    )

    parser.add_argument(
        "-hp",
        "--homopolymer",
        help="The minimum number of repeated identical nucleotides in an amplicon to be discarded. E.g. if this parameter is set to 8, amplicons containing a polymer of 8 As (-...AAAAAAAA...-), Ts, Gs, or Cs or more will not be used (default = 10)",
        default=10,
        type=int,
    )

    parser.add_argument(
        "-smy",
        "--summary",
        help="Write summary file and plot of the output",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-sg",
        "--selectGenes",
        help="""List of genes (one per line) to which amplicons and guides must be designed.
        The other genes in the fasta file will be used to check for specificity only
        (default: for all genes in the fasta the design is done)""",
    )

    parser.add_argument(
        "-d",
        "--distance",
        help="Minimum number of bases between primer and gRNA (default = 15)",
        default=15,
        type=int,
    )

    parser.add_argument(
        "-go",
        "--gRNAoverlap",
        help="The minimum number of bases between the start of two gRNAs (default = 5)",
        default=5,
        type=int,
    )

    parser.add_argument(
        "-ga",
        "--generateAmplicons",
        help="""Number of amplicons to generate per gene by Primer3 (default = 150).
        To generate 50 amplicons per 1000 bases per gene enter -1""",
        default=150,
        type=int,
    )

    parser.add_argument(
        "-t",
        "--threshold",
        help="Minimum gRNA MIT score allowed (default = 80)",
        default=80,
        type=int,
    )

    parser.add_argument(
        "-b",
        "--borderLength",
        help="The length of the borders (for SMAP haplotype window) (default = 10)",
        default=10,
        type=int,
    )

    parser.add_argument(
        "-al",
        "--ampliconLabel",
        help="Number the amplicons from left to right instead of from best to worst",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-gl",
        "--gRNAlabel",
        help="Number the gRNAs from left to right instead of from best to worst",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-sf",
        "--SMAPfiles",
        help="""Write additional files for downstream analysis with other SMAP packages
        (a gff and bed border files and fasta gRNA file""",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-tr5",
        "--targetRegion5",
        help="""The fraction of the coding sequence that cannot be targeted at the 5'
        end as indicated by a float between 0 and 1 (default = 0.2)""",
        default=0.2,
        type=float,
    )

    parser.add_argument(
        "-tr3",
        "--targetRegion3",
        help="""The fraction of the coding sequence that cannot be targeted at the 3'
        end as indicated by a float between 0 and 1 (default = 0.2)""",
        default=0.2,
        type=float,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="Keep track of the primer design while the program is running",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-aa",
        "--allAmplicons",
        help="Return all amplicons with their respective gRNAs per gene (extra file)",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-tsr",
        "--targetSpecificRegion",
        help="""Only target a specific region in the gene indicated by the feature name
        in the GFF file""",
        default=None,
    )

    parser.add_argument(
        "-mpa",
        "--misPrimingAllowed",
        help="""Do not check for mispriming in the gene set when designing primers.
        By default Primer3 will not allow primers that can prime at other genes in
        the gene set""",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-rpd",
        "--restrictPrimerDesign",
        help="""This option will restrict primer design in large introns, increasing
        the speed of amplicon design.""",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-prom",
        "--promoter",
        help="""Give the last 6 bases of the promoter that will be used to express
        the gRNA. This will be taken into account when checking for BsaI or BbsI
        sites in the gRNA (default: U6 promoter = TGATTG)""",
        default="TGATTG",
    )

    parser.add_argument(
        "-scaf",
        "--scaffold",
        help="""Give the first 6 bases of the scaffold that will be used. This
        will be taken into account when checking for BsaI or BbsI sites in the gRNA
        (default = GTTTTA)""",
        default="GTTTTA",
    )

    parser.add_argument(
        "-db",
        "--debug",
        help="""Give a gff file with all amplicons designed by Primer3 and all
        gRNAs before filtering""",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-psp",
        "--preSelectedPrimers",
        help="""Give a set of amplicons/primers for which you want to find gRNAs.
        The primers should be given in a gff with featurenames Primer_forward and
        Primer_reverse.
        The forward primer should be occur before the corresponding reverse primer
        in the gff file""",
    )

    parser.add_argument(
        "-pT",
        "--polyT",
        help="Minimum number of repeated Ts (in a poly-T) in the gRNA to avoid (default = 4)",
        default=4,
        type=int,
    )

    parser.add_argument(
        "-rs",
        "--restrictionSite",
        help="Do not filter out gRNAs that contain a BsaI or BbsI restriction site",
        default=True,
        action="store_false",
    )

    parser.add_argument(
        "--version",
        help="version of SMAP design",
        action="version",
        version="%(prog)s " + version,
    )
    return parser


########################################################################################################################
""" First filtering of the Guide file"""


def reverseComplement(sequence):
    rev = str.maketrans("ACTG", "TGAC")
    return sequence.translate(rev)[::-1]


# Returns True if there is a restriction site in the guide
def restrictionSite(
    target, promoter, scaffold, checkforRestrictionSite
):  # BsaI: 5'-GGTCTC-3'    BbsI: 5'-GAAGAC-3'
    if checkforRestrictionSite:
        targetExtend = "{}{}{}".format(
            promoter, target, scaffold
        )  # add U6 promoter bases and scaffold bases
        status = True
        if (
            "GGTCTC" not in targetExtend and "GAAGAC" not in targetExtend
        ):  # check for BsaI and BbsI in forward strand
            reverseTargetExtend = reverseComplement(targetExtend)
            if (
                "GGTCTC" not in reverseTargetExtend and "GAAGAC" not in targetExtend
            ):  # check for BsaI and BbsI in reverse strand
                status = False
        return status
    else:
        return False


# Returns dictionary of GFF file
def parseGFF(GFFfile):
    with open(GFFfile, "r") as f:
        GFFdict = {}
        for line in f:
            if line[0] != "#":
                (
                    gene,
                    source,
                    featureType,
                    start,
                    stop,
                    score,
                    strand,
                    phase,
                    attributes,
                ) = line.strip().split("\t")
                if featureType == "cds":
                    featureType = featureType.upper()

                if gene not in GFFdict:
                    GFFdict[gene] = {}

                if featureType not in GFFdict[gene]:
                    GFFdict[gene][featureType] = {
                        "source": [],
                        "coordinates": [],
                        "score": [],
                        "strand": [],
                        "phase": [],
                        "attributes": [],
                    }

                GFFdict[gene][featureType]["source"].append(source)
                GFFdict[gene][featureType]["coordinates"].append([start, stop])
                GFFdict[gene][featureType]["score"].append(score)
                GFFdict[gene][featureType]["strand"].append(strand)
                GFFdict[gene][featureType]["phase"].append(phase)
                GFFdict[gene][featureType]["attributes"].append(attributes)

    # Calculate the intersect of the CDS features to handle multiple transcripts and add it to the dictionary
    for gene in GFFdict.keys():
        if "CDS" in GFFdict[gene]:
            sortedCoordinates = sorted(
                [
                    list(map(int, coordinates))
                    for coordinates in GFFdict[gene]["CDS"]["coordinates"]
                ]
            )  # turn coordinates from strings to integers and sort

            sortedCoordinates = list(
                k for k, _ in itertools.groupby(sortedCoordinates)
            )  # remove duplicates

            intersectedCoordinates = []
            for i, CDS in enumerate(sortedCoordinates):
                if i == 0:
                    intersectedCoordinates.append(CDS)
                else:
                    if CDS[0] in range(
                        intersectedCoordinates[-1][0], intersectedCoordinates[-1][1]
                    ):
                        if CDS[1] > intersectedCoordinates[-1][1]:
                            intersectedCoordinates[-1][1] = CDS[1]
                    else:
                        intersectedCoordinates.append(CDS)

            GFFdict[gene]["CDS"]["intersected"] = intersectedCoordinates

    return GFFdict


# Filter on guide location, poly T, restriction sites, specificity to make Guide dictionary
def FilterGuides(
    filename,
    ampDict,
    GFFdict,
    gRNAsource,
    MITtreshold,
    targetSpecRegion,
    promoter,
    scaffold,
    polyT,
    checkForRestrictionSite,
    debug=False,
):
    GuideDict = {}
    global SRC

    with open(filename, "r") as file:
        # header = file.readline().split()
        count = 0
        exonDict = {}  # Dictionary to keep count of the guides that target exons
        TTTTdict = {}  # Dictionary to keep count of the guides that do not have poly(T)
        restrictDict = (
            {}
        )  # Dictionary to keep count of the guides that do not have restriction site
        totalGuidesDict = {}  # Dictionary to keep count of all guides per gene
        debugGuideDict = {}  # Only filled if user selects debug option

        for line in file:
            if gRNAsource.lower() == "crispor":  # CRISPOR:
                if (
                    line[0] != "#"
                ):  # When concatenating guide files the header can be in the file multiple times
                    try:
                        (
                            geneId,
                            guideId,
                            targetSeq,
                            MITScore,
                            _,
                            offTarget,
                            targetLocus,
                            doench,
                            _,
                            OOF,
                            _,
                            _,
                        ) = line.rstrip().split("\t")
                    except Exception:
                        print(
                            "gRNA file is not in the correct format for CRISPOR gRNAs. Check the manual for correct format (12 columns)"
                        )
                        print("------------SMAP design exited------------")
                        exit()
                    MITScore = MITtreshold if MITScore == "None" else float(MITScore)
                    doench = 0 if doench == "NotEnoughFlankSeq" else doench
                    OOF = 0 if OOF == "NotEnoughFlankSeq" else OOF
                    SRC = "CRISPOR"

            elif gRNAsource.lower() == "flashfry":  # FlashFry
                if (
                    line.split()[0] != "contig"
                ):  # When concatenating guide files the header can be in the file multiple times
                    try:
                        (
                            geneId,
                            start,
                            stop,
                            targetSeq,
                            _,
                            _,
                            orientation,
                            doench,
                            _,
                            _,
                            MITScore,
                            offTarget,
                        ) = line.rstrip().split("\t")
                    except Exception:
                        print(
                            "gRNA file is not in the correct format for FlashFry gRNAs. Check the manual for correct format (12 columns)"
                        )
                        print("------------SMAP design exited------------")
                        exit()
                    count += 1
                    guideId = "gRNA" + str(count)
                    MITScore = round(float(MITScore))
                    OOF = 100
                    doench = 0 if doench == "NA" else round(float(doench) * 100)
                    SRC = "FlashFry"

            elif gRNAsource.lower() == "other":
                try:
                    (
                        geneId,
                        targetSeq,
                        MITScore,
                        offTarget,
                        doench,
                        OOF,
                    ) = line.rstrip().split("\t")
                except Exception:
                    print(
                        "gRNA is not in the correct format. Should be: GeneID  gRNAsequence  MITscore  offTarget  doench  Out-of-Frame"
                    )
                    print("------------SMAP design exited------------")
                    exit()
                count += 1
                guideId = "gRNA" + str(count)
                MITScore = 100 if MITScore == "NA" else round(float(MITScore))
                offTarget = 0 if offTarget == "NA" else offTarget
                doench = 0 if doench == "NA" else round(float(doench) * 100)
                OOF = 100 if OOF == "NA" else OOF
                SRC = "Unknown"

            else:
                print("--gRNA source should be either CRISPOR, FlashFry or other")
                print("------------SMAP design exited------------")
                exit()

            if geneId in LIST_OF_GENES:  # Only selected genes in the debug dictionary
                if debug:  # Dictionary for debugging: all gRNAs before filtering
                    if geneId in FASTA_DICT:  # Only genes in the FASTA file
                        guideCoordinate, _, strand = guideCoordinates(
                            targetSeq, FASTA_DICT[geneId]
                        )
                        if (
                            guideCoordinate
                        ):  # Only gRNAs that are found in the FASTA sequence
                            if geneId not in debugGuideDict:
                                debugGuideDict[geneId] = {}
                            if guideId not in debugGuideDict[geneId]:
                                debugGuideDict[geneId][guideId] = {
                                    "GuideId": geneId
                                    + ":gRNA"
                                    + str(len(debugGuideDict[geneId]) + 1).zfill(3),
                                    "GuideSequence": targetSeq,
                                    "GuideCoordinates": guideCoordinate,
                                    "Strand": strand,
                                    "MITscore": MITScore,
                                    "OffTargets": offTarget,
                                    "DoenchScore": doench,
                                    "OOF": OOF,
                                }

                if geneId not in totalGuidesDict:
                    totalGuidesDict[geneId] = 0
                totalGuidesDict[geneId] += 1

                if geneId not in TTTTdict:
                    TTTTdict[geneId] = 0

                if geneId not in restrictDict:
                    restrictDict[geneId] = 0

                if geneId in ampDict:
                    if "T" * polyT not in targetSeq:  # No poly T in guide
                        TTTTdict[geneId] += 1
                        if not restrictionSite(
                            targetSeq, promoter, scaffold, checkForRestrictionSite
                        ):  # No BsaI or BbsI in guide
                            restrictDict[geneId] += 1
                            if MITScore >= MITtreshold:  # Guide specificity test
                                GuideInfo = makeGuideDict(
                                    geneId,
                                    targetSeq,
                                    MITScore,
                                    offTarget,
                                    doench,
                                    OOF,
                                    GFFdict,
                                    targetSpecRegion,
                                    exonDict,
                                )
                                if GuideInfo:
                                    if geneId not in GuideDict:
                                        GuideDict[geneId] = {}
                                    GuideDict[geneId][guideId] = {
                                        "GuideId": geneId
                                        + ":gRNA"
                                        + str(len(GuideDict[geneId]) + 1).zfill(2),
                                        "GuideSequence": GuideInfo[1],
                                        "strand": GuideInfo[2],
                                        "GuideCoordinates": GuideInfo[0],
                                        "MITscore": GuideInfo[3],
                                        "OffTarget": GuideInfo[4],
                                        "DoenchScore": GuideInfo[5],
                                        "OOF": GuideInfo[6],
                                    }
    return GuideDict, exonDict, TTTTdict, restrictDict, totalGuidesDict, debugGuideDict


########################################################################################################################
""" Functions to make GuideDict and AmpDict """


# return guide coordinate (position in input sequence)
def guideCoordinates(gRNA_seq, gene_seq):
    forward = []
    reverse = []
    coordinates, NewName, strand = "", "", ""

    for m in re.finditer(gRNA_seq, gene_seq):
        forward.append((m.start() + 1, m.end()))
    for m in re.finditer(str(Seq(gRNA_seq).reverse_complement()), gene_seq):
        reverse.append((m.start() + 1, m.end()))
    if len(forward) == 1 and len(reverse) == 0:
        NewName = str(forward[0][0]) + "fwd"
        coordinates = forward[0]
        strand = "forward"
    elif len(forward) == 0 and len(reverse) == 1:
        NewName = str(reverse[0][0]) + "rev"
        coordinates = reverse[0]
        strand = "reverse"

    if coordinates and NewName:
        return coordinates, NewName, strand
    else:
        return "", "", ""


# Filter out guides that are not in the 'middle' of the gene (returns True if the guide is in the middle)
def filterGuideLocation(gene, GuideCoordinates, exonDict, GFFdict):
    # Calculate length of complete CDS, subtract intron lengths up to the guide from the guide coordinate.
    # Then calculate if the "new" guide coordinate falls in the middle of the complete CDS length
    intronLengthToGuide, totalCDSlength = 0, 0
    Guide_Start, Guide_Stop = int(GuideCoordinates[0]), int(GuideCoordinates[1])
    GuideInCDScheck = False
    Check = True

    # Calculate total CDS length and new coordinate of guide if all introns are subtracted from its start position
    for i, CDS in enumerate(GFFdict[gene]["CDS"]["intersected"]):
        CDS_Start, CDS_Stop = int(CDS[0]), int(CDS[1])
        totalCDSlength += (CDS_Stop - CDS_Start) + 1
        if i == 0:
            if GuideCoordinates[0] < CDS_Start:
                break
            else:
                intronLengthToGuide += CDS_Start - 1

        if Guide_Start not in range(
            CDS_Start, CDS_Stop + 1
        ) and Guide_Stop not in range(CDS_Start, CDS_Stop + 1):
            if Check:
                if i != 0:
                    intronLengthToGuide += CDS_Start - int(
                        GFFdict[gene]["CDS"]["intersected"][i - 1][1]
                    )
        elif Guide_Start in range(CDS_Start, CDS_Stop + 1) and Guide_Stop in range(
            CDS_Start, CDS_Stop + 1
        ):
            GuideInCDScheck = True
            if i != 0:
                intronLengthToGuide += CDS_Start - int(
                    GFFdict[gene]["CDS"]["intersected"][i - 1][1]
                )

            Check = False

    # Check if guide targets the middle CDS ("exon" also includes UTRs)
    if GuideInCDScheck:
        exonDict[gene] += 1
        GuideLocationInCDS = Guide_Start - intronLengthToGuide
        if (
            TARGET_REGION5
            <= GuideLocationInCDS / totalCDSlength
            <= (1 - TARGET_REGION3)
        ):
            return True
        else:
            return False


# Return true if the guide targets the specified region
def targetSpecificRegion(gene, GuideCoordinates, GFFdict, tsr, exonDict):
    if tsr in GFFdict[gene]:
        for region in GFFdict[gene][tsr]["coordinates"]:
            Region_Start, Region_Stop = int(region[0]), int(region[1])
            if GuideCoordinates[0] in range(Region_Start, Region_Stop + 1):
                if GuideCoordinates[1] in range(Region_Start, Region_Stop + 1):
                    exonDict[gene] += 1
                    return True
    else:
        if VERBOSE:
            if gene not in NO_CDS:
                print(
                    "Feature {} not present for this gene in the GFF file. Skipped this gene".format(
                        tsr
                    )
                )
                NO_CDS.append(gene)


# Calculate regions where no primer design is needed (long introns)
def restrictedDesign(gene, maxLength, GFFdict):
    # Restricted coordinates should be given as [[start, length], [start, length]...]
    restrictedCoordinates = []
    intersectedCoordinates = GFFdict[gene]["CDS"]["intersected"]

    geneEndCoodinate = False
    if "gene" in GFFdict[gene]:
        geneEndCoodinate = int(GFFdict[gene]["gene"]["coordinates"][0][1])
    elif "Gene" in GFFdict[gene]:
        geneEndCoodinate = int(GFFdict[gene]["Gene"]["coordinates"][0][1])

    for i, CDS in enumerate(intersectedCoordinates):
        if (
            CDS[1] < geneEndCoodinate
        ):  # Mistakes in the GFF file (CDS coordinates after end of gene)
            if i == 0:
                if CDS[0] > maxLength:
                    restrictedCoordinates.append(
                        [1, CDS[0] - maxLength - 1]
                    )  # Start of gene until first exon
            elif i != len(intersectedCoordinates) - 1:
                if CDS[0] - intersectedCoordinates[i - 1][1] > 2 * maxLength:
                    restrictedCoordinates.append(
                        [
                            intersectedCoordinates[i - 1][1] + maxLength,
                            (CDS[0] - maxLength)
                            - (intersectedCoordinates[i - 1][1] + maxLength),
                        ]
                    )  # Between long introns
            else:
                if CDS[0] - intersectedCoordinates[i - 1][1] > 2 * maxLength:
                    restrictedCoordinates.append(
                        [
                            intersectedCoordinates[i - 1][1] + maxLength,
                            (CDS[0] - maxLength)
                            - (intersectedCoordinates[i - 1][1] + maxLength),
                        ]
                    )  # Between long introns

                if geneEndCoodinate:
                    if geneEndCoodinate > CDS[1] + maxLength:
                        restrictedCoordinates.append(
                            [
                                CDS[1] + maxLength,
                                geneEndCoodinate - (CDS[1] + maxLength),
                            ]
                        )  # Between last exon and end of gene

    return restrictedCoordinates


# Check for the amplicon if there are homopolymers present (returns false if there are)
def checkForHomopolymers(gene, LeftPrimerStop, RightPrimerStart, hp, lSeq, rSeq):
    polyA = "A" * hp
    polyT = "T" * hp
    polyG = "G" * hp
    polyC = "C" * hp

    ampliconSeq = FASTA_DICT[gene][LeftPrimerStop:RightPrimerStart]

    if (
        polyA in ampliconSeq
        or polyT in ampliconSeq
        or polyG in ampliconSeq
        or polyC in ampliconSeq
    ):
        return False
    else:
        return True


# Design amplicons using primer3
def primer(
    GFFdict,
    generateAmplicons,
    minLength,
    maxLength,
    misPriming,
    restrictPrimerDesign,
    primerMaxLibraryMispriming,
    primerPairMaxLibraryMispriming,
    primerMaxTemplateMispriming,
    primerPairMaxTemplateMispriming,
    hp,
):
    count = 0
    primers = {}

    global NO_PRIMER3_AMPLICONS
    NO_PRIMER3_AMPLICONS = []

    global GENE_TOO_SHORT
    GENE_TOO_SHORT = []

    for gene, seq in FASTA_DICT.items():
        if (
            gene in LIST_OF_GENES
        ):  # Only design primers on genes that were selected, but use the other genes in the fasta to check for specificity
            if VERBOSE:
                count += 1
                print("{}/{}\t({})".format(str(count), str(len(LIST_OF_GENES)), gene))

            if len(seq) >= minLength:
                SeqLib = {"SEQUENCE_ID": gene, "SEQUENCE_TEMPLATE": seq}

                if generateAmplicons == -1:  # Default is set to 150
                    generateAmplicons = len(seq) * 0.05

                if (
                    restrictPrimerDesign
                ):  # Exclude regions from binding any primer (introns more than double the size of the max amplicon length)
                    restrictedCoordinates = restrictedDesign(gene, maxLength, GFFdict)
                    SeqLib["SEQUENCE_EXCLUDED_REGION"] = restrictedCoordinates

                settings = {
                    "PRIMER_PRODUCT_SIZE_RANGE": [[minLength, maxLength]],
                    "PRIMER_NUM_RETURN": int(generateAmplicons),
                    "PRIMER_MAX_LIBRARY_MISPRIMING": primerMaxLibraryMispriming,
                    "PRIMER_PAIR_MAX_LIBRARY_MISPRIMING": primerPairMaxLibraryMispriming,
                    "PRIMER_MAX_TEMPLATE_MISPRIMING": primerMaxTemplateMispriming,
                    "PRIMER_PAIR_MAX_TEMPALTE_MISPRIMING": primerPairMaxTemplateMispriming,
                    "PRIMER_MIN_LEFT_THREE_PRIME_DISTANCE": 5,
                    "PRIMER_MIN_RIGHT_THREE_PRIME_DISTANCE": 5,
                }

                # Check for mispriming
                if not misPriming:  # Check for mispriming (default)
                    FastaDict_copy = FASTA_DICT.copy()
                    _ = FastaDict_copy.pop(gene)
                    results = primer3.bindings.design_primers(
                        SeqLib, settings, misprime_lib=FastaDict_copy
                    )
                else:  # Do not check for mispriming
                    results = primer3.bindings.design_primers(SeqLib, settings)

                nAmplicons = results["PRIMER_PAIR_NUM_RETURNED"]
                if nAmplicons > 0:
                    primers[gene] = {}
                    leftPrimerSeq = [
                        "PRIMER_LEFT_" + str(n) + "_SEQUENCE" for n in range(nAmplicons)
                    ]
                    rightPrimerSeq = [
                        "PRIMER_RIGHT_" + str(n) + "_SEQUENCE"
                        for n in range(nAmplicons)
                    ]

                    leftPrimerCoordinates = [
                        "PRIMER_LEFT_" + str(n) for n in range(nAmplicons)
                    ]
                    rightPrimerCoordinates = [
                        "PRIMER_RIGHT_" + str(n) for n in range(nAmplicons)
                    ]

                    ampliconName = [
                        gene + "_Amplicon" + str(n + 1).zfill(3)
                        for n in range(nAmplicons)
                    ]

                    for lSeq, rSeq, lCo, rCo, name in zip(
                        leftPrimerSeq,
                        rightPrimerSeq,
                        leftPrimerCoordinates,
                        rightPrimerCoordinates,
                        ampliconName,
                    ):
                        LeftPrimerStart, LeftPrimerStop = (
                            results[lCo][0],
                            results[lCo][0] + results[lCo][1],
                        )  # Start coordinate of the pirmer is at the 5'
                        rightPrimerStart, rightPrimerStop = (
                            results[rCo][0] + 1 - results[rCo][1],
                            results[rCo][0] + 1,
                        )  # Start of the primer is at the 3' (so 5' of the positive strand)

                        if checkForHomopolymers(
                            gene,
                            int(LeftPrimerStop),
                            int(rightPrimerStart),
                            hp,
                            results[lSeq],
                            results[rSeq],
                        ):
                            primers[gene][name] = {}

                            primers[gene][name]["PrimerNames"] = [
                                name + "_fwd",
                                name + "_rev",
                            ]
                            primers[gene][name]["PrimerSequences"] = [
                                results[lSeq],
                                results[rSeq],
                            ]
                            primers[gene][name]["PrimerCoordinates"] = [
                                (LeftPrimerStart, LeftPrimerStop),
                                (rightPrimerStart, rightPrimerStop),
                            ]
                    if not primers[gene]:
                        NO_PRIMER3_AMPLICONS.append(gene)
                        if VERBOSE:
                            print("{} has no amplicons".format(gene))

                else:
                    NO_PRIMER3_AMPLICONS.append(gene)
                    if VERBOSE:
                        print("{} has no amplicons".format(gene))

            else:
                GENE_TOO_SHORT.append(gene)
                if VERBOSE:
                    print(
                        "{} ({} bp) is too short to produce amplicons of length {} - {}".format(
                            gene, len(seq), minLength, maxLength
                        )
                    )
    return primers


# Turn a set of pre-selected primers into an AmpDict dictionary
def preSelectedPrimersToDict(preSelectedPrimers):
    global NO_PRIMER3_AMPLICONS
    NO_PRIMER3_AMPLICONS = []

    global GENE_TOO_SHORT
    GENE_TOO_SHORT = []

    preSelected = {}
    with open(preSelectedPrimers, "r") as primerFile:
        for line in primerFile:
            if line[0] != "#":  # Sometimes a GFF file starts with ##gff-version...
                (
                    gene,
                    source,
                    feature,
                    start,
                    stop,
                    score,
                    strand,
                    _,
                    attributes,
                ) = line.strip().split("\t")

                if gene not in preSelected:
                    preSelected[gene] = {}

                if feature == "Primer_forward":
                    name = gene + "_Amplicon" + str(len(preSelected[gene]) + 1)
                    primerNames = [name + "_fwd"]
                    primerSequences = [FASTA_DICT[gene][int(start) : int(stop)]]
                    primerCoordinates = [(int(start), int(stop))]

                elif feature == "Primer_reverse":
                    primerNames.append(name + "_rev")
                    primerSequences.append(
                        reverseComplement((FASTA_DICT[gene][int(start) : int(stop)]))
                    )
                    primerCoordinates.append((int(start), int(stop)))

                    preSelected[gene][name] = {}

                    preSelected[gene][name]["PrimerNames"] = primerNames
                    preSelected[gene][name]["PrimerSequences"] = primerSequences
                    preSelected[gene][name]["PrimerCoordinates"] = primerCoordinates

    return preSelected


# Make a dictionary for the guides
def makeGuideDict(
    gene,
    guideSeq,
    MITscore,
    OffTargetCount,
    Doench,
    OOF,
    GFFdict,
    targetSpecRegion,
    exonDict,
):
    geneSeq = FASTA_DICT[gene]
    GuideCoordinates, guideID, strand = guideCoordinates(guideSeq, geneSeq)

    # For summary file: calculate number of guides in exons
    if gene not in exonDict:
        exonDict[gene] = 0

    if GuideCoordinates:
        if targetSpecRegion:
            if targetSpecificRegion(
                gene, GuideCoordinates, GFFdict, targetSpecRegion, exonDict
            ):  # If guide targets the specified region
                return [
                    GuideCoordinates,
                    guideSeq,
                    strand,
                    MITscore,
                    OffTargetCount,
                    Doench,
                    OOF,
                ]
        else:
            if filterGuideLocation(
                gene, GuideCoordinates, exonDict, GFFdict
            ):  # If guide is in middle of CDS
                return [
                    GuideCoordinates,
                    guideSeq,
                    strand,
                    MITscore,
                    OffTargetCount,
                    Doench,
                    OOF,
                ]


# Combine guide and amplicon dictionary
def makeCombinedDict(GuideDict, AmpDict):
    combined_dict = {}
    global NO_GUIDE
    NO_GUIDE = []
    for gene, guides in GuideDict.items():
        if gene not in combined_dict:
            combined_dict[gene] = {}
        for guide, features in guides.items():
            if guide not in combined_dict[gene]:
                combined_dict[gene][guide] = {}
            guide_start, guide_stop = (
                features["GuideCoordinates"][0],
                features["GuideCoordinates"][1],
            )
            combined_dict[gene][guide]["start"], combined_dict[gene][guide]["stop"] = (
                guide_start,
                guide_stop,
            )

    # Extract info for amplicons
    for gene, amplicons in AmpDict.items():
        if gene in combined_dict:
            for amp, features in amplicons.items():
                fwd_start, fwd_end = (
                    features["PrimerCoordinates"][0][0],
                    features["PrimerCoordinates"][0][1],
                )
                rev_start, rev_end = (
                    features["PrimerCoordinates"][1][0],
                    features["PrimerCoordinates"][1][1],
                )

                combined_dict[gene][amp + "_fwd"] = {}
                (
                    combined_dict[gene][amp + "_fwd"]["start"],
                    combined_dict[gene][amp + "_fwd"]["stop"],
                ) = (fwd_start, fwd_end)
                combined_dict[gene][amp + "_rev"] = {}
                (
                    combined_dict[gene][amp + "_rev"]["start"],
                    combined_dict[gene][amp + "_rev"]["stop"],
                ) = (rev_start, rev_end)

        else:
            NO_GUIDE.append(gene)
            if VERBOSE:
                print("No gRNAs passed the filters for gene {}".format(gene))

    return combined_dict


########################################################################################################################
"""Amplicon and Guide overlap functions"""


# Select guides that are inbetween the primers and are not too close to the primers
def GuideInAmpliconSelect(
    CompAmp, Gene_df, gene, Amplicon_Guide_dict, GuideDict, boundlength, go, N
):
    """For each compatible primer pair, find guides inbetween,
    having in mind that they should not be too close to the primers"""

    # Extract all guides in a df
    guide_df = Gene_df[Gene_df["Feature"] == "gRNA"]
    # Loop over compatible primer pairs
    for pp in CompAmp[gene]:
        # Extract primer pair coordinates
        FwStop, RevStart = (
            CompAmp[gene][pp]["PrimerCoordinates"][0][1],
            CompAmp[gene][pp]["PrimerCoordinates"][1][0],
        )

        # Filter the guide df to find compatible guides
        CandidateGuides = guide_df[
            (guide_df["start"] >= FwStop + boundlength)
            & (guide_df["stop"] <= RevStart - boundlength)
        ]

        # Extract these guides in a list
        CandidateGuidesList = list(CandidateGuides["TagId"])
        # If the list is not empty, save them
        if CandidateGuidesList:
            if len(CandidateGuidesList) > 1:
                selectedGuidesDict, overlap = GuideOverlap(
                    CandidateGuidesList, gene, GuideDict, go, N
                )

                selectedGuides = []
                selectedGuidesSeqs = []
                selectedGuidesCoordinates = []
                selectedGuidesOrientations = []
                selectedGuidesMITscore = []
                selectedGuidesOffTarget = []
                selectedGuidesDoenchScore = []
                selectedGuidesOOF = []

                for guide in selectedGuidesDict:
                    selectedGuides.append(guide)
                    selectedGuidesSeqs.append(selectedGuidesDict[guide]["Sequence"])
                    selectedGuidesCoordinates.append(
                        [
                            selectedGuidesDict[guide]["Start"],
                            selectedGuidesDict[guide]["Stop"],
                        ]
                    )
                    selectedGuidesOrientations.append(
                        selectedGuidesDict[guide]["Strand"]
                    )
                    selectedGuidesMITscore.append(selectedGuidesDict[guide]["MITscore"])
                    selectedGuidesOffTarget.append(
                        selectedGuidesDict[guide]["OffTarget"]
                    )
                    selectedGuidesDoenchScore.append(
                        selectedGuidesDict[guide]["DoenchScore"]
                    )
                    selectedGuidesOOF.append(selectedGuidesDict[guide]["OOF"])

            else:
                selectedGuides = CandidateGuidesList
                selectedGuidesSeqs = [
                    GuideDict[gene][CandidateGuidesList[0]]["GuideSequence"]
                ]
                selectedGuidesCoordinates = [
                    GuideDict[gene][CandidateGuidesList[0]]["GuideCoordinates"]
                ]
                selectedGuidesOrientations = [
                    GuideDict[gene][CandidateGuidesList[0]]["strand"]
                ]
                selectedGuidesMITscore = [
                    GuideDict[gene][CandidateGuidesList[0]]["MITscore"]
                ]
                selectedGuidesOffTarget = [
                    GuideDict[gene][CandidateGuidesList[0]]["OffTarget"]
                ]
                selectedGuidesDoenchScore = [
                    GuideDict[gene][CandidateGuidesList[0]]["DoenchScore"]
                ]
                selectedGuidesOOF = [GuideDict[gene][CandidateGuidesList[0]]["OOF"]]
                overlap = False

            AmpliconNumber = (
                gene + "_Amplicon" + str(len(Amplicon_Guide_dict[gene]) + 1).zfill(3)
            )
            Amplicon_Guide_dict[gene][AmpliconNumber]["PrimerNames"] = [
                AmpliconNumber + "_fwd",
                AmpliconNumber + "_rev",
            ]
            Amplicon_Guide_dict[gene][AmpliconNumber]["PrimerSequences"] = CompAmp[
                gene
            ][pp]["PrimerSequences"]
            Amplicon_Guide_dict[gene][AmpliconNumber]["PrimerCoordinates"] = CompAmp[
                gene
            ][pp]["PrimerCoordinates"]
            Amplicon_Guide_dict[gene][AmpliconNumber]["GuideId"] = [
                AmpliconNumber + ":gRNA" + str(i).zfill(2)
                for i in range(1, len(selectedGuides) + 1)
            ]
            Amplicon_Guide_dict[gene][AmpliconNumber][
                "GuideSequences"
            ] = selectedGuidesSeqs
            Amplicon_Guide_dict[gene][AmpliconNumber][
                "GuideCoordinates"
            ] = selectedGuidesCoordinates
            Amplicon_Guide_dict[gene][AmpliconNumber][
                "GuideOrientations"
            ] = selectedGuidesOrientations
            Amplicon_Guide_dict[gene][AmpliconNumber][
                "MITscores"
            ] = selectedGuidesMITscore
            Amplicon_Guide_dict[gene][AmpliconNumber][
                "OffTarget"
            ] = selectedGuidesOffTarget
            Amplicon_Guide_dict[gene][AmpliconNumber][
                "DoenchScore"
            ] = selectedGuidesDoenchScore
            Amplicon_Guide_dict[gene][AmpliconNumber]["OOF"] = selectedGuidesOOF
            Amplicon_Guide_dict[gene][AmpliconNumber]["overlap"] = overlap
            Amplicon_Guide_dict[gene][AmpliconNumber]["numbergRNAs"] = len(
                selectedGuides
            )

    return Amplicon_Guide_dict


# Turn dictionary into a dataframe
def MakeDataFrame(combined_dict):
    # list comprehension: makes list of tuples whereby each tuple contains GeneId, TagId, Start/stop, position
    df = pd.DataFrame.from_records(
        [
            (gene, tag, feature, coordinate)
            for gene, TagDict in combined_dict.items()
            for tag, CoordinateDict in TagDict.items()
            for feature, coordinate in CoordinateDict.items()
        ],
        columns=["GeneId", "TagId", "Start/stop", "Coordinate"],
    )

    FeatureConditions = [
        (df["TagId"].str.contains("_fwd")),
        (df["TagId"].str.contains("_rev")),
        (~df["TagId"].str.contains("_")),
    ]

    # Set corresponding feature values
    FeatureValues = ["amp_fwd", "amp_rev", "gRNA"]
    # Insert the feature column
    df.insert(
        loc=2, column="Feature", value=np.select(FeatureConditions, FeatureValues)
    )
    df_pivot = (
        df.pivot_table(
            index=["GeneId", "TagId", "Feature"],
            columns="Start/stop",
            values="Coordinate",
        )
        .reindex(["start", "stop"], axis=1)
        .reset_index()
    )
    # Sort on the start values
    return df_pivot.sort_values("start")


# Initialization function to find guides that fit within amplicons
def GuidesInAmplicons(df, CompatibleAmpDict, GuideDict, boundlength, go, N):
    # Initiate a dictionary
    Amplicon_Guide_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    group_by_gene = df.groupby("GeneId")
    for gene, group in group_by_gene:
        GuideInAmpliconSelect(
            CompatibleAmpDict,
            group,
            gene,
            Amplicon_Guide_dict,
            GuideDict,
            boundlength,
            go,
            N,
        )
    return Amplicon_Guide_dict


# Converts the dictionary that contains guides per amplicon into a dataframe
def ConvertToDataFrame(Amplicon_Guide_dict):
    df = pd.DataFrame.from_records(
        [
            (
                GeneId,
                AmpliconId,
                features["PrimerNames"][0],
                features["PrimerNames"][1],
                features["PrimerSequences"],
                features["PrimerCoordinates"],
                features["GuideId"],
                features["GuideSequences"],
                features["GuideCoordinates"],
                features["GuideOrientations"],
                features["MITscores"],
                features["OffTarget"],
                features["DoenchScore"],
                features["OOF"],
                features["overlap"],
                features["numbergRNAs"],
                mean(list(map(int, features["MITscores"]))),
                mean(list(map(int, features["OffTarget"]))),
                mean(list(map(int, features["DoenchScore"]))),
                mean(list(map(int, features["OffTarget"]))),
            )
            for GeneId, AmpliconDict in Amplicon_Guide_dict.items()
            for AmpliconId, features in AmpliconDict.items()
        ],
        columns=[
            "GeneId",
            "AmpliconId",
            "TagId_fw",
            "TagId_rv",
            "PrimerSequences",
            "PrimerCoordinates",
            "GuideId",
            "GuideSequences",
            "GuideCoordinates",
            "GuideOrientations",
            "MITscores",
            "OffTarget",
            "DoenchScore",
            "OOF",
            "Overlap",
            "numbergRNAs",
            "MITAvg",
            "OffTargetAvg",
            "DoenchAvg",
            "OOFAvg",
        ],
    )
    df = df.sort_values(
        ["numbergRNAs", "Overlap", "MITAvg", "OffTargetAvg", "DoenchAvg", "OOFAvg"],
        ascending=[False, True, False, True, False, False],
    )
    return df


# Look for guides with the least overlap in the amplicon
def GuideOverlap(Guides, gene, GuideDict, go, N):
    Row = []

    for guide in Guides:
        Row.append(
            [
                guide,
                int(GuideDict[gene][guide]["MITscore"]),
                int(GuideDict[gene][guide]["OffTarget"]),
                int(GuideDict[gene][guide]["DoenchScore"]),
                int(GuideDict[gene][guide]["OOF"]),
                int(GuideDict[gene][guide]["GuideCoordinates"][0]),
                int(GuideDict[gene][guide]["GuideCoordinates"][1]),
                GuideDict[gene][guide]["GuideSequence"],
                GuideDict[gene][guide]["strand"],
            ]
        )

    df_guides = pd.DataFrame(
        Row,
        columns=[
            "Guide",
            "MITscore",
            "OffTarget",
            "Doench",
            "OOF",
            "Start",
            "Stop",
            "Sequence",
            "Strand",
        ],
    )
    df_guides.sort_values(
        ["MITscore", "OffTarget", "Doench", "OOF"],
        ascending=[False, True, False, False],
        inplace=True,
    )

    overlap = False
    breakCheckpoint = False
    secondBestSelectedGuides = {}
    for a in range(len(df_guides)):
        selectedGuides = {}
        nonSelectedGuides = {}

        for i, (index, row) in enumerate(df_guides.iterrows()):
            if i == a:
                selectedGuides[row.Guide] = {
                    "Start": row.Start,
                    "Stop": row.Stop,
                    "MITscore": row.MITscore,
                    "OffTarget": row.OffTarget,
                    "DoenchScore": row.Doench,
                    "OOF": row.OOF,
                    "Sequence": row.Sequence,
                    "Strand": row.Strand,
                }

            elif i > a:
                selectedRanges = [
                    [features["Start"], features["Stop"]]
                    for guide, features in selectedGuides.items()
                ]

                if not any(
                    [
                        getOverlap([row.Start, row.Stop], interval)
                        for interval in selectedRanges
                    ]
                ):
                    selectedGuides[row.Guide] = {
                        "Start": row.Start,
                        "Stop": row.Stop,
                        "MITscore": row.MITscore,
                        "OffTarget": row.OffTarget,
                        "DoenchScore": row.Doench,
                        "OOF": row.OOF,
                        "Sequence": row.Sequence,
                        "Strand": row.Strand,
                    }
                else:
                    nonSelectedGuides[row.Guide] = {
                        "Start": row.Start,
                        "Stop": row.Stop,
                        "MITscore": row.MITscore,
                        "OffTarget": row.OffTarget,
                        "DoenchScore": row.Doench,
                        "OOF": row.OOF,
                        "Sequence": row.Sequence,
                        "Strand": row.Strand,
                    }
            else:
                nonSelectedGuides[row.Guide] = {
                    "Start": row.Start,
                    "Stop": row.Stop,
                    "MITscore": row.MITscore,
                    "OffTarget": row.OffTarget,
                    "DoenchScore": row.Doench,
                    "OOF": row.OOF,
                    "Sequence": row.Sequence,
                    "Strand": row.Strand,
                }

            if len(selectedGuides) == N:
                breakCheckpoint = True
                break
        if len(selectedGuides) == N:
            break

        # Keep track of the guide combination which has the most non-overlapping guides and non-selected guides
        if len(selectedGuides) > len(secondBestSelectedGuides):
            secondBestSelectedGuides = selectedGuides
            secondBestNonSelectedGuides = nonSelectedGuides

    # If there are not enough guides, add guides from the non-selected guides and add those with minimal overlap
    if not breakCheckpoint:
        if len(df_guides) != len(
            secondBestSelectedGuides
        ):  # Can only add guides if there are non-selected guides left
            selectedGuides = secondBestSelectedGuides
            nonSelectedGuides = secondBestNonSelectedGuides

            addGuides = []
            for nonSelectedGuide, features1 in nonSelectedGuides.items():
                guideDistances = []
                breakCheckpoint = False
                for selectedGuide, features2 in selectedGuides.items():
                    distance = abs(features1["Start"] - features2["Start"])
                    if distance > go:
                        guideDistances.append(distance)
                    else:
                        breakCheckpoint = True
                        break

                if guideDistances and not breakCheckpoint:
                    avgDistance = sum(guideDistances) / len(guideDistances)
                    addGuides.append((avgDistance, nonSelectedGuide))

            if addGuides:
                addGuides = sorted(
                    addGuides, reverse=True
                )  # First add those with maximal distance from selected guides

                # Add guides until there are enough or until there are no left.
                # Take into account that the added guides also have a distance of at least 'go'
                i = 0
                while len(selectedGuides) < N and i < len(addGuides):
                    if i == 0:
                        startPosAdded = nonSelectedGuides[addGuides[i][1]]["Start"]
                        selectedGuides[addGuides[i][1]] = nonSelectedGuides[
                            addGuides[i][1]
                        ]
                    else:
                        if (
                            abs(
                                startPosAdded
                                - nonSelectedGuides[addGuides[i][1]]["Start"]
                            )
                            > go
                        ):
                            selectedGuides[addGuides[i][1]] = nonSelectedGuides[
                                addGuides[i][1]
                            ]
                            startPosAdded = nonSelectedGuides[addGuides[i][1]]["Start"]
                    overlap = True
                    i += 1
        else:
            selectedGuides = secondBestSelectedGuides

    return selectedGuides, overlap


# Make dictionary from Dataframe for AmpliconOverlap function
def makeDict(df):
    overlapDict = {}

    for index, row in df.iterrows():
        gene = row.GeneId
        ampliconId = row.AmpliconId
        forwardId = row.TagId_fw
        reverseId = row.TagId_rv
        primerSequences = row.PrimerSequences
        primerCoordinates = row.PrimerCoordinates
        guideId = row.GuideId
        guideSequences = row.GuideSequences
        guideCoordinates = row.GuideCoordinates
        guideOrientations = row.GuideOrientations
        MITscores = row.MITscores
        OffTarget = row.OffTarget
        DoenchScore = row.DoenchScore
        OOF = row.OOF
        overlap = row.Overlap

        if gene not in overlapDict:
            overlapDict[gene] = {}
        overlapDict[gene][ampliconId] = {
            "PrimerNames": [forwardId, reverseId],
            "GuideId": guideId,
            "GuideSequences": guideSequences,
            "GuideCoordinates": guideCoordinates,
            "PrimerSequences": primerSequences,
            "PrimerCoordinates": primerCoordinates,
            "GuideOrientations": guideOrientations,
            "MITscores": MITscores,
            "OffTarget": OffTarget,
            "DoenchScore": DoenchScore,
            "OOF": OOF,
            "overlap": overlap,
        }
    return overlapDict


# Returns True if guides/amplicons overlap, False if guides/amplicons do not overlap
def getOverlap(oligo1, oligo2):
    """return True if both ranges overlap"""
    return min(oligo1[1], oligo2[1]) - max(oligo1[0], oligo2[0]) >= 0


# When the numbering amplicons parameter is called change the amplicon numbering from left to right
def changeAmpliconNumber(selectedAmplicons, gene, allAmps=False):
    reversedAmp = {}
    for amplicon, features in selectedAmplicons.items():
        startCoordinate = features["PrimerCoordinates"][0][0]
        reversedAmp[startCoordinate] = amplicon

    sortedCoordinates = sorted(reversedAmp.items())
    sortedSelectedAmplicons = {}
    for i, valueKey in enumerate(sortedCoordinates, 1):
        newAmpliconName = gene + "_Amplicon" + str(i).zfill(2)
        if (
            allAmps
        ):  # If all amplicons are requested and want the numbering from left to right
            newPrimerNameForward, newPrimerNameReverse = (
                newAmpliconName + "_fwd",
                newAmpliconName + "_rev",
            )
            selectedAmplicons[valueKey[1]]["PrimerNames"] = [
                newPrimerNameForward,
                newPrimerNameReverse,
            ]
            if (
                len(selectedAmplicons[valueKey[1]]) > 3
            ):  # If there are more than three features, there are also guides in the dictionary that need to change with the amplicon name
                selectedAmplicons[valueKey[1]]["GuideId"] = [
                    newAmpliconName + ":" + guide.split(":")[1]
                    for guide in selectedAmplicons[valueKey[1]]["GuideId"]
                ]
        sortedSelectedAmplicons[newAmpliconName] = selectedAmplicons[valueKey[1]]
    return sortedSelectedAmplicons


# Return two best amplicons that do not overlap
def AmpliconOverlap(overlapDict, N, ampliconLabel, gRNAlabel, onlyPrimers=False):
    ampDict = {}
    for gene, ampliconDict in overlapDict.items():
        secondBestAmplicons = {}
        for a in range(len(ampliconDict)):
            selectedAmplicons = {}
            preAmplicons = {}
            ampCount = 0
            for i, amplicon in enumerate(ampliconDict):
                if (
                    i == a
                ):  # If this is the first amplicon, directly add it to the selection
                    ampCount += 1
                    ampName = gene + "_Amplicon" + str(ampCount).zfill(2)
                    selectedAmplicons[ampName] = ampliconDict[amplicon]

                    # Eg if the third amplicon is first in the selection also check the first 2 for overlap
                    if preAmplicons:
                        for preAmp in preAmplicons:
                            aStart, aStop = (
                                preAmplicons[preAmp]["PrimerCoordinates"][0][0],
                                preAmplicons[preAmp]["PrimerCoordinates"][1][1],
                            )
                            selectedRanges = [
                                [
                                    features["PrimerCoordinates"][0][0],
                                    features["PrimerCoordinates"][1][1],
                                ]
                                for amp, features in selectedAmplicons.items()
                            ]

                            if not any(
                                [
                                    getOverlap([aStart, aStop], interval)
                                    for interval in selectedRanges
                                ]
                            ):
                                ampCount += 1
                                ampName = gene + "_Amplicon" + str(ampCount).zfill(2)
                                selectedAmplicons[ampName] = preAmplicons[preAmp]
                elif i < a:
                    preAmplicons[ampName] = ampliconDict[amplicon]

                else:  # Otherwise you need to know if this overlap with any amplicon already in the selection
                    aStart, aStop = (
                        ampliconDict[amplicon]["PrimerCoordinates"][0][0],
                        ampliconDict[amplicon]["PrimerCoordinates"][1][1],
                    )
                    selectedRanges = [
                        [
                            features["PrimerCoordinates"][0][0],
                            features["PrimerCoordinates"][1][1],
                        ]
                        for amp, features in selectedAmplicons.items()
                    ]

                    if not any(
                        [
                            getOverlap([aStart, aStop], interval)
                            for interval in selectedRanges
                        ]
                    ):
                        ampCount += 1
                        ampName = gene + "_Amplicon" + str(ampCount).zfill(2)
                        selectedAmplicons[ampName] = ampliconDict[amplicon]

                if len(selectedAmplicons) == N:
                    break
            if len(selectedAmplicons) == N:
                break

            # Get as many amplicons as possible if there are not enough to satisfy N
            if len(selectedAmplicons) > len(secondBestAmplicons):
                secondBestAmplicons = selectedAmplicons

        # If ampliconLabel is called, change the amplicon name from left to right
        if ampliconLabel:
            selectedAmplicons = changeAmpliconNumber(selectedAmplicons, gene)
            if secondBestAmplicons:
                secondBestAmplicons = changeAmpliconNumber(secondBestAmplicons, gene)

        # if selectedAmplicons length is smaller than N, choose second combination of amplicons with most amplicons
        if len(selectedAmplicons) == N:
            finalSelection = selectedAmplicons
        else:
            finalSelection = secondBestAmplicons

        # Change primer and guide names
        for amplicon in finalSelection:
            finalSelection[amplicon]["PrimerNames"] = [
                amplicon + "_fwd",
                amplicon + "_rev",
            ]

            if not onlyPrimers:
                newGuideNames = []
                for i, guide in enumerate(finalSelection[amplicon]["GuideId"]):
                    newName = amplicon + ":gRNA" + str(i + 1).zfill(2)
                    newGuideNames.append(newName)
                finalSelection[amplicon]["GuideId"] = newGuideNames
                if gRNAlabel:
                    sorted_indices = sorted(
                        range(len(finalSelection[amplicon]["GuideCoordinates"])),
                        key=lambda i: finalSelection[amplicon]["GuideCoordinates"][i],
                    )
                    finalSelection[amplicon]["GuideCoordinates"] = [
                        finalSelection[amplicon]["GuideCoordinates"][i]
                        for i in sorted_indices
                    ]
                    finalSelection[amplicon]["GuideSequences"] = [
                        finalSelection[amplicon]["GuideSequences"][i]
                        for i in sorted_indices
                    ]
                    finalSelection[amplicon]["GuideOrientations"] = [
                        finalSelection[amplicon]["GuideOrientations"][i]
                        for i in sorted_indices
                    ]

        ampDict[gene] = finalSelection

    return ampDict


########################################################################################################################
"""functions for writing messages and files"""


# Write message at the start of the program with some of the settings
def printMessage(
    borderLength,
    amplicons,
    numberAmplicons,
    minl,
    maxl,
    numbergRNAs,
    distance,
    gRNAoverlap,
    threshold,
    gRNAfile,
    targetRegion5,
    targetRegion3,
    selectGenes,
):
    if amplicons == -1:
        amplicons = "50/kb"
    print("--------------------------------------------------------")
    print(
        "|     Length Amplicons                  : "
        + str(minl)
        + "-"
        + str(maxl)
        + " bp"
        + " " * (13 - (len(str(minl)) + len(str(maxl)) + 4))
        + "|"
    )
    print(
        "|     Generate total amplicons          : "
        + str(amplicons)
        + " " * (13 - len((str(amplicons))))
        + "|"
    )
    print(
        "|     Generate non-overlapping amplicons: "
        + str(numberAmplicons)
        + " " * (13 - len(str(numberAmplicons)))
        + "|"
    )
    print(
        "|     Generate gRNAs per amplicon:      : "
        + str(numbergRNAs)
        + " " * (13 - len(str(numbergRNAs)))
        + "|"
    )
    print("--------------------------------------------------------")

    # Error messages
    if borderLength < 0:
        print("--borderLength must be a positive integer or 0")
        exit()
    if amplicons < -1:
        print("--generateAmplicons must be a positive integer or -1")
        exit()
    if numberAmplicons <= 0:
        print("--numberAmplicons must be a positive integer")
        exit()
    if minl <= 0:
        print("--minimumAmpliconLength must be a positive integer")
        exit()
    if maxl <= 0:
        print("--maximumAmpliconLength must be a positive integer")
        exit()
    if numbergRNAs <= 0:
        print("--numbergRNAs must be a positive integer")
        exit()
    if distance < 0:
        print("--distance must be a positive integer or 0")
        exit()
    if gRNAoverlap < 0:
        print("--gRNAoverlap must be a positive integer or 0")
        exit()
    if threshold < 0:
        print("--threshold must be a positive integer or 0")
        exit()
    if targetRegion5 < 0 or targetRegion5 > 1:
        print("--targetRegion5 must be a float between 0 and 1")
        exit()
    if targetRegion3 < 0 or targetRegion3 > 1:
        print("--targetRegion3 must be a float between 0 and 1")
        exit()
    if gRNAfile:
        if not os.path.isfile(gRNAfile):
            print("No such file: {}".format(gRNAfile))
            exit()
    if selectGenes:
        if not os.path.isfile(selectGenes):
            print("No such file: {}".format(selectGenes))
            exit()


# Write final output to tsv
def writeToFile(Amplicons, outputfile, tsr, onlyPrimers=False):
    # Final output: a tsv file with the amplicons and a tsv file with the guides
    if not onlyPrimers:
        gRNAfile_handle = open(outputfile + "_gRNAs.tsv", "w")

    with open(outputfile + "_primers.tsv", "w") as primerFile:
        for gene, ampliconDict in Amplicons.items():
            for amplicon, features in ampliconDict.items():
                forwardName, reverseName = (
                    features["PrimerNames"][0],
                    features["PrimerNames"][1],
                )
                forwardSeq, reverseSeq = (
                    features["PrimerSequences"][0],
                    features["PrimerSequences"][1],
                )
                primerFile.write("\t".join((gene, forwardName, forwardSeq)) + "\n")
                primerFile.write("\t".join((gene, reverseName, reverseSeq)) + "\n")

                if not onlyPrimers:
                    for guide, guideSeq in zip(
                        features["GuideId"], features["GuideSequences"]
                    ):
                        gRNAfile_handle.write("\t".join((gene, guide, guideSeq)) + "\n")

        # Write message in guide and primer file for genes that do not have amplicons
        if not tsr:
            tsr = "CDS"
        for gene in LIST_OF_GENES:
            if not onlyPrimers:
                if gene in NO_PRIMER3_AMPLICONS:
                    primerFile.write(
                        "\t".join(
                            (
                                gene,
                                "Primer3 could not design specific amplicons for this gene",
                            )
                        )
                        + "\n"
                    )
                    gRNAfile_handle.write(
                        "\t".join(
                            (
                                gene,
                                "Primer3 could not design specific amplicons for this gene",
                            )
                        )
                        + "\n"
                    )
                elif gene in GENE_TOO_SHORT:
                    primerFile.write(
                        "\t".join(
                            (
                                gene,
                                "Gene too short to produce amplicons of required length",
                            )
                        )
                        + "\n"
                    )
                    gRNAfile_handle.write(
                        "\t".join(
                            (
                                gene,
                                "Gene too short to produce amplicons of required length",
                            )
                        )
                        + "\n"
                    )
                elif gene in NO_CDS:
                    primerFile.write(
                        "\t".join(
                            (
                                gene,
                                "GFF file contains no {} feature for this gene".format(
                                    tsr
                                ),
                            )
                        )
                        + "\n"
                    )
                    gRNAfile_handle.write(
                        "\t".join(
                            (
                                gene,
                                "GFF file contains no {} feature for this gene".format(
                                    tsr
                                ),
                            )
                        )
                        + "\n"
                    )
                elif gene in NO_GUIDE:
                    primerFile.write(
                        "\t".join((gene, "No gRNAs passed the filters for this gene"))
                        + "\n"
                    )
                    gRNAfile_handle.write(
                        "\t".join((gene, "No gRNAs passed the filters for this gene"))
                        + "\n"
                    )
                else:
                    if gene not in Amplicons:
                        primerFile.write(
                            "\t".join(
                                (
                                    gene,
                                    "No amplicons with gRNAs were found for this gene",
                                )
                            )
                            + "\n"
                        )
                        gRNAfile_handle.write(
                            "\t".join(
                                (
                                    gene,
                                    "No amplicons with gRNAs were found for this gene",
                                )
                            )
                            + "\n"
                        )
            else:
                if gene in NO_PRIMER3_AMPLICONS:
                    primerFile.write(
                        "\t".join(
                            (
                                gene,
                                "Primer3 could not design specific amplicons for this gene",
                            )
                        )
                        + "\n"
                    )
                elif gene in GENE_TOO_SHORT:
                    primerFile.write(
                        "\t".join(
                            (
                                gene,
                                "Gene too short to produce amplicons of required length",
                            )
                        )
                        + "\n"
                    )

    if not onlyPrimers:
        gRNAfile_handle.close()


# Writing the GFF file with Amplicon, Guide, Primer_forward, Primer_reverse, Border_forward, Border_Left
def writeGFF(
    Amplicons,
    outputfile,
    borderLength,
    borderOnly,
    GFFdict,
    AmpDict,
    debugGuideDict=False,
    onlyPrimers=False,
):
    if borderOnly:
        borderFile = open(outputfile + "_borders.gff3", "w")
        SMAPfile = open(outputfile + "_SMAPs.bed", "w")
        if not onlyPrimers:
            gRNAfasta = open(outputfile + "_gRNAs.fasta", "w")

    outputfileName = outputfile + ".gff3"

    if debugGuideDict:
        debugFile = open(outputfile + "_debug.gff3", "w")

    with open(outputfileName, "w") as f:
        for gene in LIST_OF_GENES:
            # Structural annotations
            for featureType in GFFdict[gene]:
                for source, coordinates, score, strand, phase, attributes in zip(
                    GFFdict[gene][featureType]["source"],
                    GFFdict[gene][featureType]["coordinates"],
                    GFFdict[gene][featureType]["score"],
                    GFFdict[gene][featureType]["strand"],
                    GFFdict[gene][featureType]["phase"],
                    GFFdict[gene][featureType]["attributes"],
                ):
                    f.write(
                        "\t".join(
                            (
                                gene,
                                source,
                                featureType,
                                coordinates[0],
                                coordinates[1],
                                score,
                                strand,
                                phase,
                                attributes,
                            )
                        )
                        + "\n"
                    )

                    if debugGuideDict:
                        debugFile.write(
                            "\t".join(
                                (
                                    gene,
                                    source,
                                    featureType,
                                    coordinates[0],
                                    coordinates[1],
                                    score,
                                    strand,
                                    phase,
                                    attributes,
                                )
                            )
                            + "\n"
                        )

            if gene in Amplicons:
                for amp, features in Amplicons[gene].items():
                    # Amplicon
                    Attributes = "ID={};Name={};".format(amp, amp)
                    f.write(
                        "\t".join(
                            (
                                gene,
                                "Primer3",
                                "Amplicon",
                                str(features["PrimerCoordinates"][0][0] + 1),
                                str(features["PrimerCoordinates"][1][1]),
                                ".",
                                "+",
                                ".",
                                Attributes,
                            )
                        )
                        + "\n"
                    )

                    if borderOnly:
                        Locus = (
                            str(gene)
                            + ":"
                            + str(features["PrimerCoordinates"][0][1] + 1)
                            + "-"
                            + str(features["PrimerCoordinates"][1][0])
                            + "_+"
                        )
                        SMAPs = (
                            str(features["PrimerCoordinates"][0][1] + 1)
                            + ","
                            + str(features["PrimerCoordinates"][1][0])
                        )
                        SMAPfile.write(
                            "\t".join(
                                (
                                    gene,
                                    str(features["PrimerCoordinates"][0][1]),
                                    str(features["PrimerCoordinates"][1][0]),
                                    str(Locus),
                                    ".",
                                    "+",
                                    str(SMAPs),
                                    ".",
                                    "2",
                                    "HiPlex_Set1_" + str(outputfile),
                                )
                            )
                            + "\n"
                        )

                    # Guides
                    if not onlyPrimers:
                        for (
                            GuideId,
                            GuideSequence,
                            GuideCoordinate,
                            GuideOrientation,
                            MITscore,
                            OffTarget,
                            DoenchScore,
                            OOF,
                        ) in zip(
                            features["GuideId"],
                            features["GuideSequences"],
                            features["GuideCoordinates"],
                            features["GuideOrientations"],
                            features["MITscores"],
                            features["OffTarget"],
                            features["DoenchScore"],
                            features["OOF"],
                        ):
                            Orientation = "+" if GuideOrientation == "forward" else "-"
                            Att = (
                                "ID=" + GuideId,
                                "Sequence=" + GuideSequence,
                                "Name=" + GuideId,
                                "MITscore=" + str(MITscore),
                                "OffTargets=" + str(OffTarget),
                                "DoenchScore=" + str(DoenchScore),
                                "OOF=" + str(OOF),
                            )
                            if SRC == "FlashFry":
                                Att = Att[:-1]
                            Attributes = ";".join(Att)
                            f.write(
                                "\t".join(
                                    (
                                        gene,
                                        SRC,
                                        "gRNA",
                                        str(GuideCoordinate[0]),
                                        str(GuideCoordinate[1]),
                                        str(MITscore),
                                        Orientation,
                                        ".",
                                        Attributes.strip(),
                                    )
                                )
                                + "\n"
                            )

                            if borderOnly:
                                gRNAfasta.write(
                                    ">" + GuideId + "\n" + GuideSequence + "\n"
                                )

                    # Primers and borders
                    for PrimerId, PrimerSequence, PrimerCoordinate in zip(
                        features["PrimerNames"],
                        features["PrimerSequences"],
                        features["PrimerCoordinates"],
                    ):
                        Orientation = "+" if "fwd" in PrimerId else "-"
                        Attributes = ";".join(
                            (
                                "ID=" + PrimerId,
                                "Sequence=" + PrimerSequence,
                                "Name=" + PrimerId,
                            )
                        )
                        f.write(
                            "\t".join(
                                (
                                    gene,
                                    "Primer3",
                                    "Primer_forward"
                                    if Orientation == "+"
                                    else "Primer_reverse",
                                    str(PrimerCoordinate[0] + 1),
                                    str(PrimerCoordinate[1]),
                                    ".",
                                    Orientation,
                                    ".",
                                    Attributes.strip(),
                                )
                            )
                            + "\n"
                        )

                        borderName = (
                            PrimerId.split("_")[0] + "_" + PrimerId.split("_")[1]
                        )
                        borderSequence = PrimerSequence[-10:]
                        Attributes = ";".join(
                            (
                                "NAME=" + borderName,
                                "ID=" + borderName,
                                "Sequence=" + borderSequence,
                            )
                        )
                        f.write(
                            "\t".join(
                                (
                                    gene,
                                    "Primer3",
                                    "border_up"
                                    if Orientation == "+"
                                    else "border_down",
                                    str(PrimerCoordinate[1] - (borderLength - 1))
                                    if Orientation == "+"
                                    else str(PrimerCoordinate[0] + 1),
                                    str(PrimerCoordinate[1])
                                    if Orientation == "+"
                                    else str(PrimerCoordinate[0] + (borderLength)),
                                    ".",
                                    "+",
                                    ".",
                                    Attributes.strip(),
                                )
                            )
                            + "\n"
                        )

                        if borderOnly:
                            borderOnlyAttributes = "NAME=" + amp
                            borderFile.write(
                                "\t".join(
                                    (
                                        gene,
                                        "Primer3",
                                        "border_up"
                                        if Orientation == "+"
                                        else "border_down",
                                        str(PrimerCoordinate[1] - (borderLength - 1))
                                        if Orientation == "+"
                                        else str(PrimerCoordinate[0] + 1),
                                        str(PrimerCoordinate[1])
                                        if Orientation == "+"
                                        else str(PrimerCoordinate[0] + (borderLength)),
                                        ".",
                                        "+",
                                        ".",
                                        borderOnlyAttributes.strip(),
                                    )
                                )
                                + "\n"
                            )
            # Write debug file
            if not onlyPrimers:
                if debugGuideDict:
                    if gene in debugGuideDict:
                        for guide, features in debugGuideDict[gene].items():
                            Attributes = (
                                "ID=" + features["GuideId"],
                                "Sequence=" + features["GuideSequence"],
                                "Name=" + features["GuideId"],
                                "MITscore=" + str(features["MITscore"]),
                                "OffTargets=" + str(features["OffTargets"]),
                                "DoenchScore=" + str(features["DoenchScore"]),
                                "OOF=" + str(features["OOF"]),
                            )

                            Attributes = ";".join(Attributes)
                            orientation = (
                                "+" if features["Strand"] == "forward" else "-"
                            )

                            debugFile.write(
                                "\t".join(
                                    (
                                        gene,
                                        SRC,
                                        "gRNA",
                                        str(features["GuideCoordinates"][0]),
                                        str(features["GuideCoordinates"][1]),
                                        ".",
                                        orientation,
                                        ".",
                                        Attributes.strip(),
                                    )
                                )
                                + "\n"
                            )
                        if gene in AmpDict:
                            for amp, features in AmpDict[gene].items():
                                Attributes = "ID={};Name={};".format(amp, amp)
                                debugFile.write(
                                    "\t".join(
                                        (
                                            gene,
                                            SRC,
                                            "Amplicon",
                                            str(features["PrimerCoordinates"][0][0]),
                                            str(features["PrimerCoordinates"][1][1]),
                                            ".",
                                            "+",
                                            ".",
                                            Attributes.strip(),
                                        )
                                    )
                                    + "\n"
                                )

        if borderOnly:
            borderFile.close()
            SMAPfile.close()
            if not onlyPrimers:
                gRNAfasta.close()
        if debugGuideDict:
            debugFile.close()


# If no gRNAs pass any filters then you might want to see the debug file (otherwise SMAP design exits and does not output anything)
def writeDebugFileOnly(debugGuideDict, AmpDict, GFFdict, outputFile):
    with open(outputFile + "_debug.gff3", "w") as debugFile:
        for gene in LIST_OF_GENES:
            if gene in debugGuideDict:
                for guide, features in debugGuideDict[gene].items():
                    Attributes = (
                        "ID=" + features["GuideId"],
                        "Sequence=" + features["GuideSequence"],
                        "Name=" + features["GuideId"],
                        "MITscore=" + str(features["MITscore"]),
                        "OffTargets=" + str(features["OffTargets"]),
                        "DoenchScore=" + str(features["DoenchScore"]),
                        "OOF=" + str(features["OOF"]),
                    )

                    Attributes = ";".join(Attributes)
                    orientation = "+" if features["Strand"] == "forward" else "-"

                    debugFile.write(
                        "\t".join(
                            (
                                gene,
                                SRC,
                                "gRNA",
                                str(features["GuideCoordinates"][0]),
                                str(features["GuideCoordinates"][1]),
                                ".",
                                orientation,
                                ".",
                                Attributes.strip(),
                            )
                        )
                        + "\n"
                    )
                if gene in AmpDict:
                    for amp, features in AmpDict[gene].items():
                        Attributes = "ID={};Name={};".format(amp, amp)
                        debugFile.write(
                            "\t".join(
                                (
                                    gene,
                                    SRC,
                                    "Amplicon",
                                    str(features["PrimerCoordinates"][0][0]),
                                    str(features["PrimerCoordinates"][1][1]),
                                    ".",
                                    "+",
                                    ".",
                                    Attributes.strip(),
                                )
                            )
                            + "\n"
                        )

            for featureType in GFFdict[gene]:
                for source, coordinates, score, strand, phase, attributes in zip(
                    GFFdict[gene][featureType]["source"],
                    GFFdict[gene][featureType]["coordinates"],
                    GFFdict[gene][featureType]["score"],
                    GFFdict[gene][featureType]["strand"],
                    GFFdict[gene][featureType]["phase"],
                    GFFdict[gene][featureType]["attributes"],
                ):
                    if debugGuideDict:
                        debugFile.write(
                            "\t".join(
                                (
                                    gene,
                                    source,
                                    featureType,
                                    coordinates[0],
                                    coordinates[1],
                                    score,
                                    strand,
                                    phase,
                                    attributes,
                                )
                            )
                            + "\n"
                        )


# Write summary file
def writeSummary(
    AmpDict,
    GuideDict,
    overlapDict,
    exonDict,
    totalGuidesDict,
    numbergRNAs,
    outfile,
    TTTTdict,
    restrictDict,
):
    CountDictTotal = {}

    for gene in LIST_OF_GENES:
        CountDictTotal[gene] = {}

        if gene in AmpDict:
            CountDictTotal[gene]["Amplicons"] = len(AmpDict[gene])
        else:
            CountDictTotal[gene]["Amplicons"] = 0

        if gene in GuideDict:
            CountDictTotal[gene]["CDS"] = len(GuideDict[gene])
        else:
            CountDictTotal[gene]["CDS"] = 0

        if gene in overlapDict:
            CountDictTotal[gene]["OneAmp"] = len(overlapDict[gene])

            CountDictTotal[gene]["nAmps"] = 0
            for amps, features in overlapDict[gene].items():
                if len(features["GuideId"]) == numbergRNAs:
                    CountDictTotal[gene]["nAmps"] += 1

        else:
            CountDictTotal[gene]["OneAmp"] = 0
            CountDictTotal[gene]["nAmps"] = 0

        if gene in exonDict:
            CountDictTotal[gene]["exon"] = exonDict[gene]
        else:
            CountDictTotal[gene]["exon"] = 0

        if gene in totalGuidesDict:
            CountDictTotal[gene]["Guides"] = totalGuidesDict[gene]
        else:
            CountDictTotal[gene]["Guides"] = 0

        if gene in TTTTdict:
            CountDictTotal[gene]["TTTT"] = TTTTdict[gene]
        else:
            CountDictTotal[gene]["TTTT"] = 0

        if gene in restrictDict:
            CountDictTotal[gene]["restrict"] = restrictDict[gene]
        else:
            CountDictTotal[gene]["restrict"] = 0

    with open(outfile + "_summary.tsv", "w") as outfile:
        outfile.write(
            "\t".join(
                (
                    "Gene",
                    "Total # amplicons",
                    "Total # gRNAs",
                    "Amps with gRNAs",
                    "Amps with {} gRNAs".format(numbergRNAs),
                    "# gRNAs after TTTT filtering",
                    "# gRNAs after restriction site filtering",
                    "# gRNAs after intron filtering",
                    "# gRNAs after complete filtering",
                )
            )
            + "\n"
        )
        avgTotalAmps = []
        avgTotalGuides = []
        avgAmps1Guide = []
        avgAmpsNguides = []
        avgTTTT = []
        avgRestrict = []
        avgExons = []
        avgCDS = []
        for gene, features in CountDictTotal.items():
            avgTotalAmps.append(features["Amplicons"])
            avgTotalGuides.append(features["Guides"])
            avgAmps1Guide.append(features["OneAmp"])
            avgAmpsNguides.append(features["nAmps"])
            avgTTTT.append(features["TTTT"])
            avgRestrict.append(features["restrict"])
            avgExons.append(features["exon"])
            avgCDS.append(features["CDS"])

            outfile.write(
                "\t".join(
                    (
                        gene,
                        str(features["Amplicons"]),
                        str(features["Guides"]),
                        str(features["OneAmp"]),
                        str(features["nAmps"]),
                        str(features["TTTT"]),
                        str(features["restrict"]),
                        str(features["exon"]),
                        str(features["CDS"]),
                    )
                )
                + "\n"
            )

        outfile.write(
            "\t".join(
                (
                    "average",
                    str(round(mean(avgTotalAmps), 1)),
                    str(round(mean(avgTotalGuides), 1)),
                    str(round(mean(avgAmps1Guide), 1)),
                    str(round(mean(avgAmpsNguides), 1)),
                    str(round(mean(avgTTTT), 1)),
                    str(round(mean(avgRestrict), 1)),
                    str(round(mean(avgExons), 1)),
                    str(round(mean(avgCDS))),
                )
            )
        )


def writeAllAmplicons(
    Amplicon_Guide_dict,
    output,
    targetSpecificRegion,
    borderLength,
    bordersOnly,
    GFFdict,
    AmpDict,
    ampliconLabel,
    gRNAlabel,
    onlyPrimers=False,
):
    if ampliconLabel:
        sortedAmpGuideDict = {}
        for gene, amplicons in Amplicon_Guide_dict.items():
            sortedAmps = changeAmpliconNumber(amplicons, gene, True)
            sortedAmpGuideDict[gene] = sortedAmps
        Amplicon_Guide_dict = sortedAmpGuideDict

    if gRNAlabel:
        for gene, amplicons in Amplicon_Guide_dict.items():
            for amplicon, features in amplicons.items():
                Amplicon_Guide_dict[gene][amplicon]["GuideId"] = [
                    guide
                    for coordinate, guide in sorted(
                        zip(features["GuideCoordinates"], features["GuideId"])
                    )
                ]
    writeToFile(Amplicon_Guide_dict, output + "_allAmplicons", targetSpecificRegion)
    writeGFF(
        Amplicon_Guide_dict,
        output + "_allAmplicons",
        borderLength,
        bordersOnly,
        GFFdict,
        AmpDict,
        False,
        onlyPrimers,
    )


# Summary shown in graphs
def makeBarPlot(
    Amplicons,
    NumAmps,
    outputFile,
    ampDict,
    totalGuidesDict=False,
    Amplicon_Guide_Dict=False,
    numbergRNAs=False,
):
    # Calculate how many amplicons each gene has and how many guides each amplicon has

    occurrencesAmpGeneDict = {}
    for i in range(NumAmps + 1):
        occurrencesAmpGeneDict[i] = 0

    if numbergRNAs:
        occurencesGuideAmpliconDict = {}
        occurrencesGuideGeneDict = {}
        for i in range(1, numbergRNAs * NumAmps + 1):
            occurencesGuideAmpliconDict[i] = 0
            occurrencesGuideGeneDict[i] = 0

    count_noAmpliconsWithGuides = 0
    for gene in LIST_OF_GENES:
        if gene in Amplicons:
            occurrences = len(Amplicons[gene])
            occurrencesAmpGeneDict[occurrences] += 1

            if numbergRNAs:
                nGuides = 0
                for amplicon in Amplicons[gene]:
                    occurrencesGuides = len(Amplicons[gene][amplicon]["GuideId"])
                    occurencesGuideAmpliconDict[occurrencesGuides] += 1
                    nGuides += occurrencesGuides
                occurrencesGuideGeneDict[nGuides] += 1

        else:
            occurrencesAmpGeneDict[0] += 1
            if gene not in NO_PRIMER3_AMPLICONS:
                if gene not in GENE_TOO_SHORT:
                    if gene not in NO_GUIDE:
                        count_noAmpliconsWithGuides += 1

    xValues_geneAmplicon, yValues_geneAmplicon = [
        str(i) for i in (list(occurrencesAmpGeneDict))
    ], list(
        occurrencesAmpGeneDict.values()
    )  # upper left plot
    # Remove trailing zeros
    i = -1
    while yValues_geneAmplicon[i] == 0:
        i -= 1
    xValues_geneAmplicon, yValues_geneAmplicon = (
        xValues_geneAmplicon[: i + 1] if i != -1 else xValues_geneAmplicon,
        yValues_geneAmplicon[: i + 1] if i != -1 else yValues_geneAmplicon,
    )

    if numbergRNAs:
        xValues_ampliconGuide, yValues_ampliconGuide = [
            str(i) for i in (list(occurencesGuideAmpliconDict))
        ], list(
            occurencesGuideAmpliconDict.values()
        )  # middle left plot

        # Calculate the percentages why no amplicons were retained
        # upper right plot
        if yValues_geneAmplicon[0] != 0:
            pie_primer3 = int(
                (len(NO_PRIMER3_AMPLICONS) / yValues_geneAmplicon[0]) * 100
            )  # Primer3 was not able to design any specific amplicons
            pie_tooShort = int(
                (len(GENE_TOO_SHORT) / yValues_geneAmplicon[0]) * 100
            )  # Gene was too short
            pie_noGuides = int(
                (len(NO_GUIDE) / yValues_geneAmplicon[0]) * 100
            )  # There were no guides designed for the genes

            pie_noAmpliconsWithGuides = int(
                (count_noAmpliconsWithGuides / yValues_geneAmplicon[0]) * 100
            )  # There were no amplicons with guides

            values = [
                pie_primer3,
                pie_tooShort,
                pie_noGuides,
                pie_noAmpliconsWithGuides,
            ]
            labels = [
                "No specific amplicons were designed ({})".format(
                    len(NO_PRIMER3_AMPLICONS)
                ),
                "The gene is too short ({})".format(len(GENE_TOO_SHORT)),
                "No gRNAs passed the filters ({})".format(len(NO_GUIDE)),
                "No amplicons with gRNAs were found ({})".format(
                    count_noAmpliconsWithGuides
                ),
            ]
            # colors = ["#ff9999", "#99ff99", "#ffcc99", "#66b3ff"]
            # Remove 0% from the pie chart
            pie_values, pie_labels = [], []
            for v, l in zip(values, labels):
                if v != 0:
                    pie_values.append(v)
                    pie_labels.append(l)

        xValues_geneGuide, yValues_geneGuide = ["0"] + [
            str(i) for i in (list(occurrencesGuideGeneDict))
        ], [yValues_geneAmplicon[0]] + list(
            occurrencesGuideGeneDict.values()
        )  # upper right plot
        j = -1
        while yValues_geneGuide[j] == 0:
            j -= 1
        xValues_geneGuide, yValues_geneGuide = (
            xValues_geneGuide[: j + 1] if j != -1 else xValues_geneGuide,
            yValues_geneGuide[: j + 1] if j != -1 else yValues_geneGuide,
        )

        if any(
            yValues_ampliconGuide
        ):  # Check if there are any amplicons designed; if not don't remove the zeros
            if numbergRNAs:
                k = -1
                while yValues_ampliconGuide[k] == 0:
                    k -= 1
                xValues_ampliconGuide, yValues_ampliconGuide = (
                    xValues_ampliconGuide[: k + 1]
                    if k != -1
                    else xValues_ampliconGuide,
                    yValues_ampliconGuide[: k + 1]
                    if k != -1
                    else yValues_ampliconGuide,
                )

        # Make plot area
        fig = plt.figure(figsize=(45, 25))
        gs1 = gs.GridSpec(nrows=3, ncols=2)

        ax_geneAmplicon = plt.subplot(gs1[0, 0])  # upper left plot
        ax_geneGuide = plt.subplot(gs1[0, 1])  # upper right plot
        ax_ampliconGuide = plt.subplot(gs1[1, 0])  # middle left plot
        ax_pie = plt.subplot(gs1[1, 1])  # middle right plot
        ax_ampliconGene = plt.subplot(gs1[2, 0:2])  # bottom plot

    # Make plot area
    else:
        fig, (ax_geneAmplicon, ax_ampliconGene) = plt.subplots(
            nrows=2, ncols=1, figsize=(40, 20)
        )

    # Print some settings on the top of the graph
    requestedAmpliconsText = "amplicon" if NumAmps == 1 else "non-overlapping amplicons"
    totalAmplicons = sum(
        [int(a) * int(b) for a, b in zip(xValues_geneAmplicon, yValues_geneAmplicon)]
    )
    totalAmpliconsText = (
        "1 amplicon"
        if totalAmplicons == 1
        else "{} non-overlapping amplicons".format(totalAmplicons)
    )
    numbergRNAsText = (
        "{} gRNA".format(numbergRNAs)
        if numbergRNAs == 1
        else "{} gRNAs".format(numbergRNAs)
    )
    avgAmpGuide = round(totalAmplicons / len(LIST_OF_GENES), 2)

    if numbergRNAs:
        text = "-Submitted {} genes\n-Requested {} {} per gene\n-Requested {} per amplicon\n-Returned a total of {} (average {} per gene)".format(
            len(LIST_OF_GENES),
            NumAmps,
            requestedAmpliconsText,
            numbergRNAsText,
            totalAmpliconsText,
            avgAmpGuide,
        )
    else:
        text = "-Submitted {} genes\n-Requested {} {} per gene\n-Returned a total of {} (average {} per gene)".format(
            len(LIST_OF_GENES),
            NumAmps,
            requestedAmpliconsText,
            totalAmpliconsText,
            avgAmpGuide,
        )

    plt.gcf().text(
        0.13,
        0.91,
        text,
        fontsize=17,
        fontweight="bold",
        bbox={"facecolor": "lightgrey", "alpha": 0.5, "pad": 10},
    )

    # Upper left plot
    ax_geneAmplicon.set_title(
        "Non-overlapping amplicons per gene",
        fontsize=25,
        fontweight="bold",
        loc="right",
    )

    ax_geneAmplicon.set_xlabel("Number of amplicons", fontsize=20)

    ax_geneAmplicon.tick_params(labelsize="large")

    ax_geneAmplicon.set_ylabel("Number of genes", fontsize=20)

    ax_geneAmplicon.tick_params(labelsize="large")

    # Print the y value on the bars
    if len(xValues_geneAmplicon) in range(1, 4):
        xPos = 0.019
    else:
        xPos = (
            0.004 * len(xValues_geneAmplicon) + 0.0032
        )  # The center of the bar depends on the width of the bar which depends on the number of x values

    for x, y in zip(xValues_geneAmplicon, yValues_geneAmplicon):
        if y != 0:
            if (
                len(str(y)) > 1
            ):  # If y value is double digits it needs some extra adjusting
                if (
                    len(xValues_geneAmplicon) > 4
                ):  # Except if there are only 4 or less amplicons
                    xPos += 0.021

            ax_geneAmplicon.text(
                int(x) - xPos,
                int(y) + 0.02,
                str(y),
                color="black",
                fontweight="bold",
                fontsize=14,
            )

    ax_geneAmplicon.bar(xValues_geneAmplicon, yValues_geneAmplicon, color="#1f77b4")

    # If there is a guide file, also show how many guides are included per amplicon and how many good and bad amplicons were designed by Primer3.
    # A good amplicon is an amplicon with at least one guide (so a useable amplicon)

    if numbergRNAs:
        # Middle left plot
        ax_ampliconGuide.set_title(
            "gRNAs per amplicon", fontsize=25, fontweight="bold", loc="right"
        )

        ax_ampliconGuide.set_xlabel("Number of gRNAs", fontsize=20)

        ax_ampliconGuide.tick_params(labelsize="large")

        ax_ampliconGuide.set_ylabel("Number of amplicons", fontsize=20)

        ax_ampliconGuide.tick_params(labelsize="large")

        # Print the y value on the bars
        for a, b in zip(xValues_ampliconGuide, yValues_ampliconGuide):
            if b > 0:
                ax_ampliconGuide.text(
                    int(a) - 1,
                    int(b) + 0.02,
                    str(
                        b
                    ),  # x position -1 because it starts at 0, whereas xValues_ampliconGuide starts at 1
                    color="black",
                    fontweight="bold",
                    fontsize=14,
                )

        ax_ampliconGuide.bar(
            xValues_ampliconGuide, yValues_ampliconGuide, color="#1f77b4"
        )

        # Upper right plot
        ax_geneGuide.set_title(
            "gRNAs per gene", fontsize=25, fontweight="bold", loc="right"
        )

        ax_geneGuide.set_xlabel("Number of gRNAs", fontsize=20)

        ax_geneGuide.tick_params(labelsize="large")

        ax_geneGuide.set_ylabel("Number of genes", fontsize=20)

        ax_geneGuide.tick_params(labelsize="large")

        # Print the y value on the bars
        for a, b in zip(xValues_geneGuide, yValues_geneGuide):
            if b > 0:
                ax_geneGuide.text(
                    int(a),
                    int(b) + 0.02,
                    str(b),
                    # x position -1 because it starts at 0, whereas xValues_ampliconGuide starts at 1
                    color="black",
                    fontweight="bold",
                    fontsize=14,
                )

        ax_geneGuide.bar(xValues_geneGuide, yValues_geneGuide, color="#1f77b4")

        # Middle right plot
        if yValues_geneAmplicon[0] != 0:
            ax_pie.set_title(
                "Cause for not retaining amplicons",
                fontsize=25,
                fontweight="bold",
                loc="right",
            )

            ax_pie.pie(
                pie_values,
                labels=["" for item in pie_labels],
                autopct="%1.0f%%",
                textprops={"fontsize": 20},
                startangle=90,
            )
            ax_pie.axis("equal")
            ax_pie.legend(pie_labels, loc="best", fontsize=18)

        # Bottom plot
        GoodAmplicons = []
        BadAmplicons = []
        GeneLength = []
        GeneLabel = []
        for gene, amplicons in ampDict.items():
            ampDict_count = len(ampDict[gene])

            Amplicon_Guide_Dict_count = (
                len(Amplicon_Guide_Dict[gene]) if gene in Amplicon_Guide_Dict else 0
            )
            GoodAmplicons.append(Amplicon_Guide_Dict_count)
            BadAmplicons.append(ampDict_count - Amplicon_Guide_Dict_count)
            GeneLength.append(len(FASTA_DICT[gene]))
            GeneLabel.append(gene)

        sortedData = sorted(zip(GoodAmplicons, BadAmplicons, GeneLength, GeneLabel))
        yValues_GoodAmplicons = [i[0] for i in sortedData]
        yValues_BadAmplicons = [i[1] for i in sortedData]
        yValues_GeneLength = [i[2] for i in sortedData]
        GeneLabel = [i[3] for i in sortedData]

        ax_ampliconGeneLength = ax_ampliconGene.twinx()  # Add second y-axis

        ax_ampliconGene.set_title(
            "Amplicons with and without gRNAs",
            fontsize=25,
            fontweight="bold",
            loc="right",
        )

        ax_ampliconGene.set_xlabel("Genes", fontsize=20)

        ax_ampliconGene.set_ylabel("Number of amplicons", fontsize=20)

        ax_ampliconGene.set_xticklabels(GeneLabel, rotation=60, fontsize=14)

        ax_ampliconGeneLength.set_ylabel("Gene length (bp)", fontsize=20)

        ax_ampliconGene.tick_params(labelsize="large")
        ax_ampliconGeneLength.tick_params(labelsize="large")

        ax_ampliconGene.bar(
            GeneLabel,
            yValues_GoodAmplicons,
            label="Amplicons with gRNAs",
            color="limegreen",
        )

        ax_ampliconGene.bar(
            GeneLabel,
            yValues_BadAmplicons,
            bottom=yValues_GoodAmplicons,
            label="Amplicons without gRNAs",
            color="grey",
        )

        ax_ampliconGeneLength.scatter(
            GeneLabel,
            yValues_GeneLength,
            label="Gene length",
            color="black",
            marker="o",
        )

        lines_1, labels_1 = ax_ampliconGene.get_legend_handles_labels()  # For legend
        (
            lines_2,
            labels_2,
        ) = ax_ampliconGeneLength.get_legend_handles_labels()  # For legend
        lines = lines_1 + lines_2  # For legend
        labels = labels_1 + labels_2  # For legend

        ax_ampliconGene.legend(lines, labels, loc="best", fontsize="x-large")

        plt.savefig(outputFile + "_summary_plot")

    else:
        # Bottom plot
        GeneLabel = []
        GeneLength = []
        NumberOfAmplicons = []
        for gene in LIST_OF_GENES:
            GeneLabel.append(gene)
            GeneLength.append(len(FASTA_DICT[gene]))
            if gene in ampDict:
                NumberOfAmplicons.append(len(ampDict[gene]))
            else:
                NumberOfAmplicons.append(0)

        yValues_NumberOfAmplicons = sorted(NumberOfAmplicons)
        yValues_GeneLength = [
            length
            for (number, length) in sorted(
                zip(NumberOfAmplicons, GeneLength), key=lambda pair: pair[0]
            )
        ]
        GeneLabel = [
            gene
            for (number, gene) in sorted(
                zip(NumberOfAmplicons, GeneLabel), key=lambda pair: pair[0]
            )
        ]

        ax_ampliconGeneLength = ax_ampliconGene.twinx()  # Add second y-axis

        ax_ampliconGene.set_title(
            "Amplicons designed by Primer3", fontsize=25, fontweight="bold", loc="right"
        )

        ax_ampliconGene.set_xlabel("Genes", fontsize=20)

        ax_ampliconGene.set_ylabel("Number of amplicons", fontsize=20)

        ax_ampliconGene.set_xticklabels(GeneLabel, rotation=60, fontsize=14)

        ax_ampliconGeneLength.set_ylabel("Gene length (bp)", fontsize=20)

        ax_ampliconGene.tick_params(labelsize="large")
        ax_ampliconGeneLength.tick_params(labelsize="large")

        ax_ampliconGene.bar(
            GeneLabel, yValues_NumberOfAmplicons, label="Amplicons", color="limegreen"
        )

        ax_ampliconGeneLength.scatter(
            GeneLabel,
            yValues_GeneLength,
            label="Gene length",
            color="black",
            marker="o",
        )

        lines_1, labels_1 = ax_ampliconGene.get_legend_handles_labels()  # For legend
        (
            lines_2,
            labels_2,
        ) = ax_ampliconGeneLength.get_legend_handles_labels()  # For legend
        lines = lines_1 + lines_2  # For legend
        labels = labels_1 + labels_2  # For legend

        ax_ampliconGene.legend(lines, labels, loc="best", fontsize="x-large")

        plt.savefig(outputFile + "_summary_plot")


# Print the time needed to run the program
def printTime(start_time):
    elapsed_time_seconds = time.time() - start_time
    hours, rem = divmod(elapsed_time_seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    print(
        "Elapsed time: {:0>2}:{:0>2}:{:05.2f}".format(
            int(hours), int(minutes), round(seconds, 2)
        )
    )
    print(
        "--------------------------------------------------------------------------------"
    )
    print("\n")


########################################################################################################################


def main(args: List[str]):
    parsed_args = parse_args(args)

    global VERBOSE
    VERBOSE = parsed_args.verbose

    # Keep genes for which no CDS is available
    global NO_CDS
    NO_CDS = []

    # Write message at the start of the program with some of the settings and write error messages
    printMessage(
        parsed_args.borderLength,
        parsed_args.generateAmplicons,
        parsed_args.numberAmplicons,
        parsed_args.minimumAmpliconLength,
        parsed_args.maximumAmpliconLength,
        parsed_args.numbergRNAs,
        parsed_args.distance,
        parsed_args.gRNAoverlap,
        parsed_args.threshold,
        parsed_args.gRNAfile,
        parsed_args.targetRegion5,
        parsed_args.targetRegion3,
        parsed_args.selectGenes,
    )

    # Turn fasta file in dictionary for easy access
    global FASTA_DICT
    with open(parsed_args.FastaFile, "r") as Fasta_handler:
        FASTA_DICT = {
            record.id: re.sub("[BDHKMRSVWY]", "N", str(record.seq))
            for record in SeqIO.parse(Fasta_handler, "fasta")
        }  # Replace ambiguous nucleotides with N

    # Parse GFF file for GuideDict creation and to add to the final GFF file
    GFFdict = parseGFF(parsed_args.GFFfile)

    # Read the selected genes into a list and remove the ones with lacking info
    global LIST_OF_GENES
    if parsed_args.selectGenes:
        with open(parsed_args.selectGenes, "r") as f:
            LIST_OF_GENES = f.read().splitlines()
            # Check whether all genes in the list are present in the fasta and gff files
            allGenes = list(FASTA_DICT.keys())
            allGenesGFF = list(GFFdict.keys())
            for i, gene in enumerate(LIST_OF_GENES):
                if gene not in allGenes:
                    notInFasta = LIST_OF_GENES.pop(
                        i
                    )  # Remove gene that is not present in the fasta file
                    print(notInFasta + " not present in the fasta file")
                elif gene not in allGenesGFF:
                    notInGFF = LIST_OF_GENES.pop(
                        i
                    )  # Remove gene that is not present in the GFF file
                    print(notInGFF + " not present in the GFF file")
                elif "CDS" not in GFFdict[gene]:
                    if (
                        parsed_args.gRNAfile
                    ):  # CDS is not important when designing without gRNAs
                        noCDSinGFF = LIST_OF_GENES.pop(
                            i
                        )  # remove gene that does not have a CDS feature in the GFF file
                        NO_CDS.append(gene)
                        print(
                            "No CDS/cds feature assigned to {} in the GFF file. Skipped this gene".format(
                                noCDSinGFF
                            )
                        )
                    else:
                        if (
                            parsed_args.restrictedPrimerDesign
                        ):  # CDS is important when the -rpd option is on even without gRNAs
                            noCDSinGFF = LIST_OF_GENES.pop(
                                i
                            )  # remove gene that does not have a CDS feature in the GFF file
                            NO_CDS.append(gene)
                            print(
                                "No CDS/cds feature assigned to {} in the GFF file. Skipped this gene".format(
                                    noCDSinGFF
                                )
                            )
    else:
        LIST_OF_GENES = list(FASTA_DICT.keys())
        allGenesGFF = list(GFFdict.keys())
        for i, gene in enumerate(LIST_OF_GENES):
            if gene not in allGenesGFF:
                notInGFF = LIST_OF_GENES.pop(
                    i
                )  # Remove gene that is not present in the GFF file
                print(notInGFF + " not present in the GFF file")
            elif "CDS" not in GFFdict[gene]:
                noCDSinGFF = LIST_OF_GENES.pop(
                    i
                )  # remove gene that does not have a CDS feature in the GFF file
                print(
                    "No CDS/cds feature assigned to {} in the GFF file. Skipped this gene".format(
                        noCDSinGFF
                    )
                )

    # Make dictionary with amplicons
    if not parsed_args.preSelectedPrimers:
        AmpDict = primer(
            GFFdict,
            parsed_args.generateAmplicons,
            parsed_args.minimumAmpliconLength,
            parsed_args.maximumAmpliconLength,
            parsed_args.misPrimingAllowed,
            parsed_args.restrictPrimerDesign,
            parsed_args.primerMaxLibraryMispriming,
            parsed_args.primerPairMaxLibraryMispriming,
            parsed_args.primerMaxTemplateMispriming,
            parsed_args.primerPairMaxTemplateMispriming,
            parsed_args.homopolymer,
        )
        if not AmpDict:
            print("\nNo amplicons could be designed on any gene")
            print("------------SMAP design exited------------")
            printTime(start_time)
            exit()
    else:
        preSelectedPrimers = parsed_args.preSelectedPrimers
        AmpDict = preSelectedPrimersToDict(preSelectedPrimers)

    # Print only amplicons, no guides
    if not parsed_args.gRNAfile:
        Amplicons = AmpliconOverlap(
            AmpDict, parsed_args.numberAmplicons, parsed_args.ampliconLabel, parsed_args.gRNAlabel, True
        )
        writeGFF(
            Amplicons,
            parsed_args.output,
            parsed_args.borderLength,
            parsed_args.SMAPfiles,
            GFFdict,
            AmpDict,
            False,
            True,
        )
        writeToFile(Amplicons, parsed_args.output, parsed_args.targetSpecificRegion, True)

        if parsed_args.summary:
            makeBarPlot(Amplicons, parsed_args.numberAmplicons, parsed_args.output, AmpDict)

        # Write a GFF file with all amplicons (not only non-overlapping amplicons)
        if parsed_args.allAmplicons:
            # Number from left to right instead of from best to worst
            if parsed_args.ampliconLabel:
                sortedAmpDict = {}
                for gene, amplicons in AmpDict.items():
                    sortedAmps = changeAmpliconNumber(amplicons, gene, True)
                    sortedAmpDict[gene] = sortedAmps
                writeToFile(
                    sortedAmpDict,
                    parsed_args.output + "_allAmplicons",
                    parsed_args.targetSpecificRegion,
                    True,
                )
                writeGFF(
                    sortedAmpDict,
                    parsed_args.output + "_allAmplicons",
                    parsed_args.borderLength,
                    parsed_args.SMAPfiles,
                    GFFdict,
                    AmpDict,
                    False,
                    True,
                )
            else:
                writeToFile(
                    AmpDict,
                    parsed_args.output + "_allAmplicons",
                    parsed_args.targetSpecificRegion,
                    True,
                )
                writeGFF(
                    AmpDict,
                    parsed_args.output + "_allAmplicons",
                    parsed_args.borderLength,
                    parsed_args.SMAPfiles,
                    GFFdict,
                    AmpDict,
                    False,
                    True,
                )

    else:
        # Filter guides and make dictionary with guides
        global TARGET_REGION5
        TARGET_REGION5 = parsed_args.targetRegion5
        global TARGET_REGION3
        TARGET_REGION3 = parsed_args.targetRegion3

        (
            GuideDict,
            exonDict,
            TTTTdict,
            restrictDict,
            totalGuidesDict,
            debugGuideDict,
        ) = FilterGuides(
            parsed_args.gRNAfile,
            AmpDict,
            GFFdict,
            parsed_args.gRNAsource,
            parsed_args.threshold,
            parsed_args.targetSpecificRegion,
            parsed_args.promoter,
            parsed_args.scaffold,
            parsed_args.polyT,
            parsed_args.restrictionSite,
            parsed_args.debug,
        )
        if not GuideDict:
            print("\nNo gRNA on any gene passed the filters")
            if parsed_args.debug:
                writeDebugFileOnly(debugGuideDict, AmpDict, GFFdict, parsed_args.output)
                print("Debug file written")
            print("-----------SMAP design exited-----------")
            printTime(start_time)
            exit()

        # Combine info from GuideDict and AmpDict
        combined_dict = makeCombinedDict(GuideDict, AmpDict)

        # Find guides that could fit within the amplicons by turning the combined dictionary into a dataframe
        df = MakeDataFrame(combined_dict)
        Amplicon_Guide_dict = GuidesInAmplicons(
            df, AmpDict, GuideDict, parsed_args.distance, parsed_args.gRNAoverlap, parsed_args.numbergRNAs
        )

        # Convert the amplicon guide dictionary back to dataframe and sort on number of guides, overlap and average scores
        df = ConvertToDataFrame(Amplicon_Guide_dict)

        # Turn sorted df into dictionary to find non-overlapping amplicons
        overlapDict = makeDict(df)

        # Return the best N non-overlapping amplicons
        Amplicons = AmpliconOverlap(
            overlapDict, parsed_args.numberAmplicons, parsed_args.ampliconLabel, parsed_args.gRNAlabel
        )

        # Write info to file
        writeToFile(
            Amplicons, parsed_args.output, parsed_args.targetSpecificRegion
        )  # An amplicon and guide file with the sequences
        writeGFF(
            Amplicons,
            parsed_args.output,
            parsed_args.borderLength,
            parsed_args.SMAPfiles,
            GFFdict,
            AmpDict,
            debugGuideDict,
        )  # GFF of the output

        # Extra files summarizing the output
        if parsed_args.summary:
            writeSummary(
                AmpDict,
                GuideDict,
                overlapDict,
                exonDict,
                totalGuidesDict,
                parsed_args.numbergRNAs,
                parsed_args.output,
                TTTTdict,
                restrictDict,
            )
            makeBarPlot(
                Amplicons,
                parsed_args.numberAmplicons,
                parsed_args.output,
                AmpDict,
                totalGuidesDict,
                Amplicon_Guide_dict,
                parsed_args.numbergRNAs,
            )

        # Write a GFF file with all amplicons and their guides (not only non-overlapping amplicons)
        if parsed_args.allAmplicons:
            writeAllAmplicons(
                Amplicon_Guide_dict,
                parsed_args.output,
                parsed_args.targetSpecificRegion,
                parsed_args.borderLength,
                parsed_args.SMAPfiles,
                GFFdict,
                AmpDict,
                parsed_args.ampliconLabel,
                parsed_args.gRNAlabel,
            )

    # Measure elapsed time
    printTime(start_time)


if __name__ == "__main__":
    main()
