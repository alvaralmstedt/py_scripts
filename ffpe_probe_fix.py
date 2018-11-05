#!/usr/bin/env python

from sys import argv
import csv


def read_bed(bed_in):
    with open(bed_in, "r") as bed:
        fieldnames = ["TRN", "TRID", "TID", "species", "BID", "chromosome", "start", "stop", "STRS",
                      "ULSOseq", "ULSOhits", "DLSOseq", "DLSOhits", "strand", "designer", "designscore", "EARS",
                      "ISNPmask", "labels"]
        bed_reader = csv.DictReader(bed, delimiter='\t', fieldnames=fieldnames)
        bed_contents = []
        targets = []
        switch = False
        for i in bed_reader:
            bed_contents.append(i)
            if i["TRN"] == "[Targets]":
                switch = True
            if switch:
                targets.append(i)
        return bed_contents, targets


def write_probes(bed_in_full, targets, bed_out, targets_out):
    with open(bed_out, "w+") as out:
        fieldnames = ["chromosome", "start1", "stop1", "start2", "stop2", "strand", "name"]
        table_writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames)
        iterator = 0
        for i in bed_in_full:
            if iterator >= 10:
                #print(i["ULSOseq"])
                try:
                    table_writer.writerow({"chromosome": str(i["chromosome"]),
                                           "start1": str(int(i["start"]) - int(len(str(i["ULSOseq"])) - 6)),
                                           "stop1": str(int(i["start"])),
                                           "start2": str(int(i["stop"]) + int(len(str(i["DLSOseq"])) - 6)),
                                           "stop2": str(int(i["stop"])),
                                           "strand": str(i["strand"]),
                                           "name": str(i["TRN"])})
                except Exception:
                    continue
            iterator += 1

    with open(targets_out, "w+") as out:
        fieldnames = ["chromosome", "start1", "stop1", "start2", "stop2", "strand", "name", "sequence"]
        table_writer_2 = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames)
        iterator_2 = 0
        for i in targets:
            try:
                probe_length = ((int(i["chromosome"]) - int(i["BID"]) - len(str(i["stop"]))) / 2)
                print(int(i["chromosome"]), int(i["BID"]), (int(i["chromosome"]) - int(i["BID"]) - len(str(i["stop"]))) / 2, probe_length)
                table_writer_2.writerow({"chromosome": str(i["species"]),
                                         "start1": str(int(i["BID"])),
                                         "stop1": str(int(i["BID"]) + int(probe_length)),
                                         "start2": str(int(i["chromosome"])),
                                         "stop2": str(int(i["chromosome"]) - int(probe_length)),
                                         "strand": str(i["start"]),
                                         "sequence": str(i["stop"])})
            except Exception:
                continue


bed_in = argv[1]
bed_out = argv[2]
targets_out = argv[3]
write_probes(read_bed(bed_in)[0], read_bed(bed_in)[1], bed_out, targets_out)