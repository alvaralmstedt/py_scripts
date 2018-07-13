#!/usr/bin/python

from sys import argv
import csv

"""
Changes the illumina trusight amplicon bed file to a more simple format interpretable by CLC

Usage:
amplicon_bed_changer.py <full path to infile> <full path to outfile>
"""


def bed_table_reader(infile):
    with open(infile, "r") as table:
        fieldnames = ["chromosome", "start", "stop", "gene", "score", "direction", "start2", "stop2", "increments",
                      "two", "increments2", "increments3"]
        table_reader = csv.DictReader(table, delimiter='\t', fieldnames=fieldnames)
        table_contents = []
        for i in table_reader:
            table_contents.append(i)
        return table_contents


def bed_table_changer(table_in, table_out):
    with open(table_out, "w+") as out:
        fieldnames = ["chromosome", "start", "stop", "gene", "score", "direction", "start2", "stop2", "increments",
                      "two", "increments2", "increments3"]
        table_writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames)
        iterator = 0
        for i in table_in:
            if iterator >= 1:
                table_writer.writerow({"chromosome": str(i["chromosome"]),
                                       "start": str(int(i["start"])),
                                       "stop": str(int(i["stop"])),
                                       "gene": str(i["gene"])})

            iterator += 1

input_file = argv[1]
output_file = argv[2]

bed_table_changer(bed_table_reader(input_file), output_file)