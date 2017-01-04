#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import csv
import vcf

parser = argparse.ArgumentParser()

parser.add_argument("vcf_input", nargs="?", type=str, help=':Full path to your vcf input file')
parser.add_argument("vcf_output", nargs="?", type=str, help=':Specify full output path and filename of the vcf file you want to create')
parser.add_argument("-p", "--program", nargs="?", action='store', type=str, help=':Specify which program created the vcf file in question')

args = parser.parse_args()

input = args.vcf_input
output = args.vcf_output
program = args.program


def read_vcf(input, runtype):
#    vcf_reader = vcf.Reader(open('filepath', 'r'))
    with open(input, "r") as vcf:
        headerlines = []
        datalines = []
        for line in vcf:
            if line.startswith("#"):
                headerlines.append(line)
            else:
                datalines.append(line)

        fieldnames = ["chr", "pos", "source", "ref", "alt", "qual", "filter", "info"]
        filecontents = csv.DictReader(datalines, delimiter='\t', fieldnames=fieldnames)
        vcf_contents = []
        if not runtype:
            return headerlines
        else:
            for i in filecontents:
                vcf_contents.append(i)
            return vcf_contents


def transformer_manta_incomplete(indata, outdata):
    with open(outdata, "w+") as out:
        fieldnames = ["chr", "pos", "source", "ref", "alt", "qual", "filter", "info"]
        writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames)
        for i in read_vcf(output, False):
            out.write(i)
        for i in indata:
            if "<DEL>" in i:
                writer.writerow({"chr": str(i["chr"]),
                                 "pos": str(i["pos"]),
                                 "source": str(["source"]),
                                 "ref": str(["ref"]),
                                 "alt": str(["alt"]),
                                 "qual": str(["qual"]),
                                 "filter": str(["filter"]),
                                 "info": str(["info"])})

            elif "<INS>" in i:
                pass
            else:
                continue
            return

def transformer_manta_dipsomtum(input, output):
    pass


def transformer_canvas(input, output):
    pass


def write_clccompliant():
    pass


def main_run_decider(indata, outdata):
    file_contents = read_vcf(indata, True)
    if "Manta" in file_contents:
        if "<DEL>" or "<INS>" in file_contents:
            transformer_manta_incomplete(indata, outdata)
        else:
            transformer_manta_dipsomtum(indata, outdata)
    elif "Canvas" in file_contents:
        transformer_canvas(indata, outdata)


main_run_decider(input, output)