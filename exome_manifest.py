#!/usr/bin/env python

from sys import argv
import csv


def read_bed(bed_in):
    with open(bed_in, "rb") as bed:
        fieldnames = ["chromosome", "start", "stop", "name", "zero", "period"]
        bed_reader = csv.DictReader(bed, delimiter='\t', fieldnames=fieldnames)
        bed_contents = []
        for i in bed_reader:
            bed_contents.append(i)

        return bed_contents


def write_manifest(bed_in, manifest_out):
    with open(manifest_out, "wb") as out:
        fieldnames = ["name", "chromosome", "start", "stop", "UPL", "DPL"]
        table_writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames, lineterminator='\n')
        iterator = 0
        out.write("#Nextera Rapid Capture Exome targeted regions manifest" + "\n")
        out.write("[Header]" + "\n")
        out.write("Manifest Version\t1" + "\n")
        out.write("ReferenceGenome Homo_sapiens\UCSC\hg19\Sequence\WholeGenomeFASTA" + "\n")
        out.write("\n")
        out.write("[Regions]" + "\n")
        out.write("\t".join(["Name",
                             "Chromosome",
                             "Start",
                             "End",
                             "Upstream Probe Length",
                             "Downstream Probe Length"]) + "\n")
        for i in bed_in:
            # if iterator >= 1:
                #import pdb; pdb.set_trace()
            table_writer.writerow({"name": str(i["name"]) + str(iterator),
                                   "chromosome": str(i["chromosome"]),
                                   "start": str(i["start"]),
                                   "stop": str(i["stop"]),
                                   "UPL": str(i["zero"]),
                                   "DPL": str(i["zero"])})
            iterator += 1

bed_in = argv[1]
manifest_out = argv[2]

write_manifest(read_bed(bed_in), manifest_out)