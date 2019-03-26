#!/usr/bin/env python

import argparse
import csv
import vcf
from multiprocessing import Pool
from multiprocessing import cpu_count
from Bio import SeqIO
import logging
import datetime

def read_vcf_new(infile):
    alts = []
    
    vcf_reader = vcf.Reader(open(infile, 'r'))
    #for rec in vcf_reader:
    #    alts.append(rec)
    return vcf_reader

def read_vcf_old(inp, runtype):
#    vcf_reader = vcf.Reader(open('filepath', 'r'))
    print(runtype)
    with open(inp, "rb") as vcf:
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

def mod_canvas_vcf(vcf):
    cpus = int(cpu_count() - 2)
    logging.info(f"using {cpus} cpus")
    p = Pool(cpus)
    refposlist = []
    #fasta = "/medstore/External_References/hs37d5/hs37d5.fa"
    #chrom_seqio = SeqIO.to_dict(SeqIO.parse(fasta, "fasta"))  
    vcf2 = vcf
    for rec in vcf2:        
        ref_pos = (str(rec.CHROM), str(rec.POS))
        refposlist.append(ref_pos)

    #print(refposlist)
    results = p.map(get_ref_base_from_pos, refposlist)
    refbases = {}
    print("final1")
    for d in results:
        refbases.update(d)
    print(refbases)
    print("final2")
    for record in vcf:
        print("final3")
        chrom = record.CHROM
        pos = record.POS
        cn = record.samples[0].data[3]
        mcc = record.samples[0].data[4]
        record.REF = refbases[f"{chrom}:{pos}"]
        
        try:
            chrom = int(chrom)
            print(chrom)
        except Exception:            
            print(Exception, chrom)
        #print(cn, mcc)
        #print(record.samples[0].data)
        if cn == 0 and type(chrom) == int:
            print(chrom, record.POS, record.ALT, "<DEL:HOM>")
            record.ALT = "<DEL:HOM>"
            print(chrom, record.POS, record.ALT, "<DEL:HOM>")
        elif cn == 0:
            print("<DEL:HEMI>", record.POS, type(chrom))
            record.ALT = "<DEL:HEMI>"
        elif cn == 1:
            print("<DEL>", record.POS)
            record.ALT = "<DEL>"
        elif cn == 2 and mcc == 2:
            print("<LOH>", record.POS)
            record.ALT = "<LOH>"
        elif cn >= 3:
            print("<DUP>", record.POS, type(record.POS), record.REF, type(record.REF))
            record.ALT = "<DUP>"
            print("ref_pos:", ref_pos)
            print(p.map_async(get_ref_base_from_pos, ref_pos))
        else:
            print("REF", record.POS)
            record.ALT = "<NORMAL>"
    #print(p.starmap(get_ref_base_from_pos, refposlist))
    print("final4")

def get_ref_base_from_pos(chrom_pos_tup):
    fasta = "/medstore/External_References/hs37d5/hs37d5.fa"
    chrom = chrom_pos_tup[0]
    refpos = chrom_pos_tup[1]
    #with open(fasta, 'r') as fasta:
    #for seq_record in SeqIO.parse(fasta, "fasta"):
    #    print(seq_record.id)
    chrom_dict = SeqIO.index(fasta, "fasta")
    #chrom_dict = chrom_pos_tup[2]
    refbaseseqio = chrom_dict[chrom][int(refpos) - 1 :int(refpos)]
    logging.info(f"Variant reference position on chr {chrom} at position {refpos} was determined to be {str(refbaseseqio.seq)}")
    return {f"{chrom}:{refpos}": str(refbaseseqio.seq)}

def print_vcf(vcf, rectype):
    print(rectype)
    try:
        for record in vcf:
            exec(f"print(record.{rectype})")
    except:
        exec(f"({vcf}.{rectype})")



def write_vcf():
    pass


def transformer_canvas(indata, outdata):
    with open(outdata, "ab") as out:
        fieldnames = ["chr", "pos", "source", "ref", "alt", "qual", "filter", "info", "format", "sample"]
        writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames, lineterminator='\n')
        for i in indata:
            print(str(i["alt"]))
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


def determine_input(indata):
    with open(indata, "r") as vcfin:
        top = [next(vcfin) for x in range(100)]
        for line in top:
            if line.startswith("##source="):
                if "Canvas" in line:
                    return "Canvas"
                elif "Manta" in line:
                    return "Manta"
                else:
                    return None

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("vcf_input", nargs="?", type=str, help=':Full path to your vcf input file')
    parser.add_argument("vcf_output", nargs="?", type=str, help=':Specify full output path and filename of the vcf file you want to create')
    parser.add_argument("-p", "--program", nargs="?", action='store', type=str, help=':Specify which program created the vcf file in question')
    parser.add_argument("-r", "--record", nargs="?", action='store', type=str, help=':Specify which record ya wanna see')

    args = parser.parse_args()
    
    #logging.getLogger().addHandler(logging.StreamHandler())
    logging.getLogger().setLevel(logging.INFO)
    inp = args.vcf_input
    outp = args.vcf_output
    rec = args.record

    source_program = determine_input(inp)
    print(source_program)

    if source_program == "Canvas":
        #print_vcf(read_vcf_new(inp), rec)
        mod_canvas_vcf(read_vcf_new(inp))
    elif source_program == "Manta":
        print("Manta not yet implemented ... sorry")


if __name__ == "__main__":
    main()
