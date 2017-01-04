#!/usr/bin/python

import csv
import argparse
import re

"""

Parses a tab-separated table and rearranges the fields to be in another order

"""

parser = argparse.ArgumentParser()

parser.add_argument("bed_table", nargs="?", type=str, help='path to your bed table input')
parser.add_argument("gtf_table", nargs="?", type=str, help='path to your gtf table input')
parser.add_argument("output", nargs="?", type=str, help='specify output path, else cwd')
parser.add_argument("-b", "--bedout", action="store_true", help='signifies bed file output')
parser.add_argument("-g", "--gtfout", action="store_true", help='signifies gtf output')
parser.add_argument("-n", "--nameswitch", action="store_true", help='signifies that you want to take the gene name from the gtf file')
parser.add_argument("-a", "--nameappend", action="store_true", help='signifies that you want to append the gene name')

args = parser.parse_args()

output = args.output
bed_out = args.bedout
gtf_out = args.gtfout
bed_in = str(args.bed_table)
gtf_in = str(args.gtf_table)
name_switch = args.nameswitch
name_append = args.nameappend

def bed_table_reader(infile):
    with open(infile, "r") as table:
        fieldnames = ["#bin", "name", "chrom", "strand", "txStart", "txEnd", "cdsStart", "cdsEnd", "exonCount",
                      "exonStarts", "exonEnds", "score", "name2", "cdsStartStat", "cdsEndStat", "exonFrames"]
        table_reader = csv.DictReader(table, delimiter='\t', fieldnames=fieldnames)
        table_contents = []
        for i in table_reader:
            table_contents.append(i)
        return table_contents


def gtf_table_reader(infile):
    with open(infile, "r") as table:
        fieldnames = ["chrom", "chromStart", "chromEnd", "name", "score", "strand", "thickStart", "thickEnd", "itemRgb",
                      "blockCount", "blockSizes", "blockStarts"]
        table_reader = csv.DictReader(table, delimiter='\t', fieldnames=fieldnames)
        table_contents = []
        for i in table_reader:
            table_contents.append(i)
        return table_contents


def modify_gtf_table(in_table, out_table):
    with open(out_table, "w+") as out:
        fieldnames = ["#bin", "name2", "chrom", "strand", "txStart", "txEnd", "cdsStart", "cdsEnd", "exonCount",
                      "exonStarts", "exonEnds", "score", "name", "cdsStartStat", "cdsEndStat", "exonFrames"]
        table_writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames)
        for i in in_table:
            table_writer.writerow({"#bin": str(i["#bin"]),
                                   "name": str(i["name"]),
                                   "name2": str(i["name2"]),
                                   "chrom": str(i["chrom"]),
                                   "strand": str(i["strand"]),
                                   "txStart": str(i["txStart"]),
                                   "txEnd": str(i["txEnd"]),
                                   "cdsStart": str(i["cdsStart"]),
                                   "cdsEnd": str(i["cdsEnd"]),
                                   "exonCount": str(i["exonCount"]),
                                   "exonStarts": str(i["exonStarts"]),
                                   "exonEnds": str(i["exonEnds"]),
                                   "score": str(i["score"]),
                                   "cdsStartStat": str(i["cdsStartStat"]),
                                   "cdsEndStat": str(i["cdsEndStat"]),
                                   "exonFrames": str(i["exonFrames"])})


def modify_bed_table(in_table_bed, out_table):
    with open(out_table, "w+") as out:
        fieldnames = ["chrom", "chromStart", "chromEnd", "name", "score", "strand", "thickStart", "thickEnd", "itemRgb",
                      "blockCount", "blockSizes", "blockStarts"]
        table_writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames)
        for i in in_table_bed:
            table_writer.writerow({"chrom": str(i["chrom"]),
                                   "chromStart": str(i["chromStart"]),
                                   "chromEnd": str(i["chromEnd"]),
                                   "name": str(i["name"]),      # This needs to be name2 from the gtf file
                                   "score": str(i["score"]),
                                   "strand": str(i["strand"]),
                                   "thickStart": str(i["thickStart"]),
                                   "thickEnd": str(i["thickEnd"]),
                                   "itemRgb": str(i["itemRgb"]),
                                   "blockCount": str(i["blockCount"]),
                                   "blockSizes": str(i["blockSizes"]),
                                   "blockStarts": str(i["blockStarts"])})


def nameswitch_bed_table(in_table_bed, out_table):
    with open(out_table, "w+") as out:
        fieldnames = ["chrom", "chromStart", "chromEnd", "name", "score", "strand", "thickStart", "thickEnd", "itemRgb",
                      "blockCount", "blockSizes", "blockStarts"]
        table_writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames)
#        iterator_1 = 0
        for i in in_table_bed:
            table_writer.writerow({"chrom": str(i["chrom"]),
                                   "chromStart": str(i["chromStart"]),
                                   "chromEnd": str(i["chromEnd"]),
                                   "name": str(i["name"]),
                                   "score": str(i["score"]),
                                   "strand": str(i["strand"]),
                                   "thickStart": str(i["thickStart"]),
                                   "thickEnd": str(i["thickEnd"]),
                                   "itemRgb": str(i["itemRgb"]),
                                   "blockCount": str(i["blockCount"]),
                                   "blockSizes": str(i["blockSizes"]),
                                   "blockStarts": str(i["blockStarts"])})


def append_gene_name(bed_file, gtf_file, outfile):
    with open(outfile, "w+") as out:
        with open(gtf_file, "r") as gtf:
            with open(bed_file, "r") as bed:
                bed_dict = {}
                for bline in bed:
                    bed_line = bline.split("\t")
                    bed_dict[bed_line[1]] = bed_line[12]
                for gline in gtf:
                    match = re.search( r'.*gene_id "(.*)"; transcript_id.*', gline)
                    if match:
                        out.write(gline.rstrip() + " Name " + str(bed_dict[match.group(1)]) + ";\n")


if name_switch:
    nameswitch_bed_table(bed_table_reader(bed_in), output)
elif bed_out:
    modify_bed_table(bed_table_reader(bed_in), bed_out)
elif gtf_out:
    modify_gtf_table(gtf_table_reader(gtf_in), gtf_out)
elif name_append:
    append_gene_name(bed_in, gtf_in, output)
else:
    print("Something went wrong. Look over your inputs, buddy :)")
