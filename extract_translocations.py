#!/usr/bin/env python

from sys import argv
import csv


def svbay_input_reader(infile):
    with open(infile, "r") as table:
        fieldnames = ["chrom1", "bp_pos1", "chrom2", "bp_pos2", "length", "num_elements", "probability", "type_sv",
                      "direction1", "direction2"]
        table_reader = csv.DictReader(table, delimiter='\t', fieldnames=fieldnames)
        table_contents = []
        for i in table_reader:
            table_contents.append(i)
        return table_contents


def extractor(table_in, table_out):
    with open(table_out, "w+") as out:
        fieldnames = ["chrom1", "bp_pos1", "chrom2", "bp_pos2", "length", "num_elements", "probability", "type_sv",
                      "direction1", "direction2"]
        table_writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames)
        iterator = 0
        for i in table_in:
            if iterator >= 1:
                if i["chrom1"] != i["chrom2"] and i["direction1"]:
                    table_writer.writerow({"chrom1": str(i["chrom1"]),
                                           "bp_pos1": str(i["bp_pos1"]),
                                           "chrom2": str(i["chrom2"]),
                                           "bp_pos2": str(i["bp_pos2"]),
                                           "length": str(i["length"]),
                                           "num_elements": str(i["num_elements"]),
                                           "probability": str(i["probability"]),
                                           "type_sv": str(i["type_sv"]),
                                           "direction1": str(i["direction1"]),
                                           "direction2": str(i["direction2"])
                                           })
            iterator += 1

input_file = argv[1]
output_file = argv[2]

extractor(svbay_input_reader(input_file), output_file)