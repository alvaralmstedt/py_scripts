#!/usr/bin/python

from sys import argv
import csv

"""
Converts minimal (3 field) tab separated BED files into minimal (9 field) tab separated GFF files.
Usage: blast_to_gff.py <BED-infile> <GFF-outfile>
By: Alvar Almstedt
"""

class Table(object):

    def __init__(self, input_file_name, output_file_name):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name

    def read_result(self):

        with open(self.input_file_name, 'r') as in_file:
            fieldnames = ["header", "start", "stop"]
            blast_reader = csv.DictReader(in_file, delimiter='\t', fieldnames=fieldnames)
            file_contents=[]
            for i in blast_reader:
                file_contents.append(i)
            return file_contents

    def write_gff(self):

        with open(self.output_file_name, 'w+') as gff_out:
            fieldnames = ["header", "blastresult", "hit", "start", "stop", "score", "orientation", "period", "ID"]
            read_results = self.read_result()
            gff_writer = csv.DictWriter(gff_out, delimiter='\t', fieldnames=fieldnames)
            for i in read_results:
                gff_writer.writerow({"header": str(i["header"]), "blastresult": "blast_result", "hit": "hit",
                                     "start": str(i["start"]), "stop": str(i["stop"]), "score": "0",
                                     "orientation": self.orientation(i["start"], i["stop"]),
                                     "period": ".", "ID": "ID=%s" % i["header"]})

    def orientation(self, start, end):
        if start < end:
            return "+"
        return "-"

if __name__ == "__main__":
    infile = argv[1]
    outfile = argv[2]
    listprint = Table(infile, outfile)
    listprint.read_result()
    listprint.write_gff()