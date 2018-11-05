#!/usr/bin/env python

from sys import argv
import csv


def read_bed(bed_in):
    with open(bed_in, "r") as bed:
        fieldnames = ["chromosome", "start1", "stop1", "name", "thousand", "direction", "start2", "stop2", "commas1",
                      "two", "commas2_offsets", "commas3"]
        bed_reader = csv.DictReader(bed, delimiter='\t', fieldnames=fieldnames)
        bed_contents = []
        for i in bed_reader:
            bed_contents.append(i)
        return bed_contents


def write_probes(bed_in, bed_out):
    with open(bed_out, "w+") as out:
        fieldnames = ["chromosome", "start1", "stop1", "start2", "stop2", "name"]
        table_writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames)
        iterator = 0
        for i in bed_in:
            if iterator >= 1:
                table_writer.writerow({"chromosome": str(i["chromosome"]),
                                       "start1": str(i["start1"]),
                                       "stop1": str(int(i["start1"]) + int(i["commas2_offsets"].split(',')[0])),
                                       "start2": str(i["stop1"]),
                                       "stop2": str(int(i["stop1"]) - int(i["commas2_offsets"].split(',')[1])),
                                       "name": str(i["name"])})
            iterator += 1

bed_in = argv[1]
bed_out = argv[2]

write_probes(read_bed(bed_in), bed_out)