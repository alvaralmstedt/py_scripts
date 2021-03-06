#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import csv
import re
#import vcf

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
    print runtype
    with open(input, "rb") as vcf:
        headerlines = []
        datalines = []
        for line in vcf:
            if line.startswith("#"):
                headerlines.append(line)
            else:
                datalines.append(line)

        fieldnames = ["chr", "pos", "source", "ref", "alt", "qual", "filter", "info", "format", "sample"]
        filecontents = csv.DictReader(datalines, delimiter='\t', fieldnames=fieldnames)
        vcf_contents = []
        if not runtype:
            return headerlines
        else:
            for i in filecontents:
                vcf_contents.append(i)
            return vcf_contents


def transformer_manta_incomplete(indata, outdata):
    with open(outdata, "ab") as out:
        for i in read_vcf(input, False):
            out.write(i)
        fieldnames = ["chr", "pos", "source", "ref", "alt", "qual", "filter", "info", "format", "sample"]
        writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames, lineterminator='\n')
        for i in indata:
 #           print(i)

            if i["alt"] == "<DEL>":
                del_len = re.search(r'.*;SVLEN=-(?s)(.[0-9]+).*', str(i["info"]))
 #               print(del_len.group(1))
                writer.writerow({"chr": str(i["chr"]),
                                 "pos": str(i["pos"]),
                                 "source": str(i["source"]),
                                 "ref": str(i["ref"]) + str("N" * (int(del_len.group(1)) - int(1))),
                                 "alt": str(i["ref"]),
                                 "qual": str(i["qual"]),
                                 "filter": str(i["filter"]),
                                 "info": str(i["info"]),
                                 "format": str(i["format"]),
                                 "sample": str(i["sample"])})
            elif i["alt"] == "<INS>":
                ins_seq1 = re.search(r'.*LEFT_SVINSSEQ=(?s)(.*);RIGHT_SVINSSEQ=.*', str(i["info"]))
                ins_seq2 = re.search(r'.*;RIGHT_SVINSSEQ=(?s)(.*).*', str(i["info"]))
                writer.writerow({"chr": str(i["chr"]),
                                 "pos": str(i["pos"]),
                                 "source": str(i["source"]),
                                 "ref": str(i["ref"]),
                                 "alt": str(i["ref"]) + str(ins_seq1.group(1) + "N"*10 + ins_seq2.group(1)),
                                 "qual": str(i["qual"]),
                                 "filter": str(i["filter"]),
                                 "info": str(i["info"]),
                                 "format": str(i["format"]),
                                 "sample": str(i["sample"])})
            else:
                print("continuing")
                continue
  #          return

def transformer_manta_dipsomtum(indata, outdata):
    with open(outdata, "ab") as out:
        fieldnames = ["chr", "pos", "source", "ref", "alt", "qual", "filter", "info", "format", "sample"]
        writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames, lineterminator='\n')
        for i in indata:
 #           print("pinne")
            if not "<INS>" in str(i["alt"]) and not "<DEL>" in str(i["alt"]):
 #               print "inne"
                writer.writerow({"chr": str(i["chr"]),
                                 "pos": str(i["pos"]),
                                 "source": str(i["source"]),
                                 "ref": str(i["ref"]),
                                 "alt": str(i["alt"]),
                                 "qual": str(i["qual"]),
                                 "filter": str(i["filter"]),
                                 "info": str(i["info"]),
                                 "format": str(i["format"]),
                                 "sample": str(i["sample"])})


def transformer_canvas(indata, outdata):
    with open(outdata, "ab") as out:
        fieldnames = ["chr", "pos", "source", "ref", "alt", "qual", "filter", "info", "format", "sample"]
        writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames, lineterminator='\n')
        for i in indata:
            print str(i["alt"])
            if i["alt"] == "<CNV>":
                cnv_len = re.search(r'.*CNVLEN=(?s)(.*).*', str(i["info"]))
                writer.writerow({"chr": str(i["chr"]),
                                 "pos": str(i["pos"]),
                                 "source": str(i["source"]),
                                 "ref": str(i["ref"]),
                                 "alt": str(i["ref"]) + str("N" * (int(cnv_len.group(1)) - int(1))),
                                 "qual": str(i["qual"]),
                                 "filter": str(i["filter"]),
                                 "info": str(i["info"]),
                                 "format": str(i["format"]),
                                 "sample": str(i["sample"])})




def write_clccompliant():
    pass


def main_run_decider(indata, outdata):
    file_contents = read_vcf(indata, True)
#    print(file_contents)
    source=[]
    alt=[]
    for i in file_contents:
 #       print i
        source.append(i['source'])
        alt.append(i['alt'])
 #   print source
    if any("Manta" in s for s in source):
        print("hej")
        if any("<DEL>" or "<INS>" in s for s in alt):
            print("svej")
            transformer_manta_incomplete(file_contents, outdata)
            transformer_manta_dipsomtum(file_contents, outdata)
    elif any("Canvas" in s for s in source):
        if any("<CNV>" in s for s in alt):
            transformer_canvas(file_contents, outdata)

if __name__ == "__main__":
    main_run_decider(input, output)

