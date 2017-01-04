#!/usr/bin/python

import csv
from sys import argv

"""
This script will read a fasta file and a gff and cut out the sequence from the fasta specified in the gff start and
stop fields. Important: make sure your fasta headers and gff headers (field 1) can match to each other.

Usage:

get_seqs_from_gff.py <in_sequences.fasta> <in_coordinates.gff> <output_filename.fasta> <field_name>

where field name is the third column in the gff file (gene/CDS/exon/intron etc.)

By: Alvar Almstedt (alvar.almstedt@gmail.com)
"""


def read_fasta(fasta):      # This fucntion reads the fasta input as argument 1 and returns as a dict where header : seq
    file_contents = {}
    data = fasta.split("\n")
    header = None
    for i in data:
        if i.startswith(">"):
            header = str(i)
        else:
            file_contents[header[1:].rstrip()] = i.rstrip()
    return file_contents


def clean_input_fasta(fastafile):   # This function cleans away any possible wrapping from the input fasta
    with open(fastafile, "r+") as infile:
        fixedfasta = ""
        iterator1 = 0
        for line in infile:
            if line.startswith(">") and infile:
                if iterator1 != 0:
                    fixedfasta += "\n"
                fixedfasta += str(line)
                iterator1 = 1
            else:
                fixedfasta += str(line.rstrip())
                iterator1 = 1
        return fixedfasta


def read_gff(gff_in):   # This function reads the gff file input as argument 2 as a list of dicts (see csv module)
    with open(gff_in, "r") as infile:
        fieldnames = ["headername", "method", "type", "start", "stop", "dot1", "plus", "dot2", "notes"]
        gff_reader = csv.DictReader(infile, delimiter='\t', fieldnames=fieldnames)
        file_contents = []
        for i in gff_reader:
            file_contents.append(i)
        return file_contents


def write_fasta_outfile(fasta_in, gff_in, outfile):  # This function parses the gff and fasta and writes out regions from
    first = 0                                        # the fasta within coordinates from the gff "CDS" or "protein_coding_region"
    with open(outfile, "w+") as fasta_out:
        for fasta_keys in fasta_in:
            for gff_line in gff_in:
                if set(gff_line["headername"].split()) & set(fasta_keys.split()):
                    if gff_line["type"] == type_to_cut:
                        start = int(gff_line["start"]) - 1      # minus 1 fixes off by one error
                        stop = int(gff_line["stop"])
                        length = str(int(gff_line["stop"]) - int(gff_line["start"]))
                        if first != 0:
                            fasta_out.write("\n")
                        fasta_out.write(">" + gff_line["headername"] + "_" + gff_line["type"] + "_from_" +
                                        gff_line["start"] + "bp_to_" + gff_line["stop"] + "bp_length_" +
                                        length + "bp" + "\n")
                        first = 1
                        fasta_out.write(fasta_in[fasta_keys][int(start):int(stop)])


def remove_introns(fasta_in, gff_in, outfile):      # under construction. this could be done in a smarter way by putting
    first = 0                                       # by putting the exons in a list or something. im dumb :(
    with open(outfile, "w+") as fasta_out:
        for fasta_keys in fasta_in:
            gene = ""
            gene_first_region = ""
            gene_second_region = ""
            gene_third_region = ""
            gene_fourth_region = ""
            gene_fifth_region = ""
            for gff_line in gff_in:
                if set(gff_line["headername"].split()) & set(fasta_keys.split()):
                    if gff_line["type"] == type_to_cut:
                        gene_start = int(gff_line["start"]) - 1      # minus 1 fixes off by one error
                        gene_stop = int(gff_line["stop"])
                        length = str(int(gff_line["stop"]) - int(gff_line["start"]))
                        gene = fasta_in[fasta_keys][int(gene_start):int(gene_stop)]
                        if first != 0:
                            fasta_out.write("\n")
                        fasta_out.write(">" + gff_line["headername"] + "_" + gff_line["type"] + "_from_" +
                                        gff_line["start"] + "bp_to_" + gff_line["stop"] + "bp_length_" +
                                        length + "bp" + "\n")
                    elif gff_line["type"] == "intron" and not gene_first_region:
                        first_intron_start = int(gff_line["start"]) - 1
                        first_intron_stop = int(gff_line["stop"])
                        gene_first_region = fasta_in[fasta_keys][:int(first_intron_start)]
#                        print "first elif"
                    elif gff_line["type"] == "intron" and gene_first_region and not gene_second_region:
                        second_intron_start = int(gff_line["start"]) - 1
                        second_intron_stop = int(gff_line["stop"])
                        gene_second_region = fasta_in[fasta_keys][first_intron_stop:second_intron_start]
#                        print "second elif"
                    elif gff_line["type"] == "intron" and gene_second_region and not gene_third_region:
                        third_intron_start = int(gff_line["start"]) - 1
                        third_intron_stop = int(gff_line["stop"])
                        gene_third_region = fasta_in[fasta_keys][second_intron_stop:third_intron_start]
#                        print "third elif"
                    elif gff_line["type"] == "intron" and gene_third_region and not gene_fourth_region:
                        fourth_intron_start = int(gff_line["start"]) - 1
                        fourth_intron_stop = int(gff_line["stop"])
                        gene_fourth_region = fasta_in[fasta_keys][third_intron_stop:fourth_intron_start]
                        gene_fifth_region = fasta_in[fasta_keys][fourth_intron_stop:]
#                        print "fifth elif"
                    if gff_line["type"] != "intron" and gff_line["type"] != type_to_cut and first != 0:
                        intron_free_gene = gene_first_region + gene_second_region + gene_third_region + gene_fourth_region + gene_fifth_region
                        fasta_out.write(intron_free_gene)
                        print "last if"
                    else:
                        fasta_out.write(gene)
                        print "no introns"
                    first = 1



in_file_fasta = argv[1]
in_file_gff = argv[2]
output_file_name = argv[3]
type_to_cut = argv[4]
ready_fasta = read_fasta(clean_input_fasta(in_file_fasta))
ready_gff = read_gff(in_file_gff)
remove_introns(ready_fasta, ready_gff, output_file_name)
# write_fasta_outfile(ready_fasta, ready_gff, output_file_name)
