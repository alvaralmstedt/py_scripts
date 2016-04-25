#!/usr/bin/python

from sys import argv
import csv

"""
Usage:
bed_field_changer.py <full path to infile> <full path to outfile> <bases to be subtracted from start> <bases to be added to stop>
"""

def bed_table_reader(infile):
    with open(infile, "r") as table:
        fieldnames = ["chromosome", "start", "stop"]
        table_reader = csv.DictReader(table, delimiter='\t', fieldnames=fieldnames)
        table_contents = []
        for i in table_reader:
            table_contents.append(i)
        return table_contents


def bed_table_changer(table_in, table_out, changestart, changestop):
    with open(table_out, "w+") as out:
        fieldnames = ["chromosome", "start", "stop"]
        table_writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames)
        iterator = 0
        for i in table_in:
            if iterator >= 1:
                table_writer.writerow({"chromosome": str(i["chromosome"]),
                                       "start": str(int(i["start"]) - int(changestart)),
                                       "stop": str(int(i["stop"]) + int(changestop))})
            iterator += 1

input_file = argv[1]
output_file = argv[2]
start_change = argv[3]
stop_change = argv[4]

bed_table_changer(bed_table_reader(input_file), output_file, start_change, stop_change)