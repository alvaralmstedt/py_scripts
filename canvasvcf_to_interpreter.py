#!/usr/bin/env python

import argparse
import csv
import vcf
from multiprocessing import Pool
from multiprocessing import cpu_count
from Bio import SeqIO
import logging
import datetime


# Reads the vcf file
def read_vcf_new(infile):
    alts = []
    
    vcf_reader = vcf.Reader(open(infile, 'r'))
    return vcf_reader

# This fucntion actually modifies the vcf to be compliate with Alissa Interpret. 
# It has to do some awkward stuff but eh... it works
def mod_canvas_vcf(vcf):
    #cpus = int(cpu_count() - 2)
    #logging.info(f"using {cpus} cpus")
    #p = Pool(cpus)
    refposlist = []
    fasta = "/medstore/External_References/hs37d5/hs37d5.fa"
    chrom_dict = SeqIO.to_dict(SeqIO.parse(fasta, "fasta"))  
    vcf_list = list(vcf)
    for rec in vcf_list:        
        ref_pos = (str(rec.CHROM), str(rec.POS))
        refposlist.append(ref_pos)

    #results = p.map(get_ref_base_from_pos, refposlist)
    results = []
    for tup in refposlist: 
        presults = chrom_dict[tup[0]][int(tup[1]) - 1 : int(tup[1])]
        results.append({f"{tup[0]}:{tup[1]}": str(presults.seq)})
    
    refbases = {}
    for d in results:
        refbases.update(d)
   
    # This for loop will modify the actual variant lines in the vcf file
    for record in vcf_list:
        #print(vcf.alts, "\n")
        chrom = record.CHROM
        pos = record.POS
        cn = record.samples[0].data[3]
        mcc = record.samples[0].data[4]
        record.REF = refbases[f"{chrom}:{pos}"]
        
        try:
            chrom = int(chrom)
        except Exception:            
            pass
        if cn == 0 and type(chrom) == int:
            #print(chrom, record.POS, record.REF, record.ALT, "<DEL:HOM>")
            record.ALT[0] = "<DEL:HOM>"            
            #print(chrom, record.POS, record.REF, record.ALT, "<DEL:HOM>")
        elif cn == 0:
            #print("<DEL:HEMI>", record.POS, record.REF, type(chrom))
            record.ALT[0] = "<DEL:HEMI>"
        elif cn == 1:
            record.ALT[0] = "<DEL>"
            #print(chrom, record.POS, record.REF, record.ALT)
        elif cn == 2 and mcc == 2:
            #print(chrom, record.POS)
            record.ALT[0] = "<LOH>"
        elif cn >= 3:
            #print("<DUP>", record.POS, type(record.POS), record.REF, type(record.REF))
            record.ALT[0] = "<DUP>"
        else:
            #print("REF", record.POS)
            # It seems like Alissa doesnt like <NORMAL> even though thats the suggestion from their docs ..
            record.ALT[0] = "<NORMAL>"
        logging.info(f"Variant at chromosome {chrom} pos {record.POS} has reference base '{record.REF}' and is set to type {record.ALT}")
    return vcf_list


# Not used. Was pretty cool though lol
def get_ref_base_from_pos(chrom_pos_tup):
    fasta = "/medstore/External_References/hs37d5/hs37d5.fa"
    chrom = chrom_pos_tup[0]
    refpos = chrom_pos_tup[1]
    chrom_dict = SeqIO.index(fasta, "fasta")
    refbaseseqio = chrom_dict[chrom][int(refpos) - 1 :int(refpos)]
    logging.info(f"Variant reference position on chr {chrom} at position {refpos} was determined to be {str(refbaseseqio.seq)}")
    return {f"{chrom}:{refpos}": str(refbaseseqio.seq)}


# Also not used. Was used for testing
def print_vcf(vcf, rectype):
    print(rectype)
    try:
        for record in vcf:
            exec(f"print(record.{rectype})")
    except:
        exec(f"({vcf}.{rectype})")


# Writes the modified vcf
def write_vcf(fixed_vcf, output, template):
    fixed_vcf = iter(fixed_vcf)
    
    # This will modify the header values for ALT
    template.alts["DUP"] = ["<DUP>", template.alts["DUP"][1]]
    CN0copy = "<DEL>"
    CN0desc = "Deletion has happened (copy)"
    template.alts["CN0"] = [CN0copy, CN0desc]
    CN2copy = "<NORMAL>"
    CN2desc = "Copy number 2. Reference"
    template.alts["CN2"] = [CN2copy, CN2desc]
    CN3copy = "<DEL:HEMI>"
    CN3desc = "Hemizygous deletion"
    template.alts["CN3"] = [CN3copy, CN3desc]
    CN4copy = "<LOH>"
    CN4desc = "Loss of Heterozygosity"
    template.alts["CN4"] = [CN4copy, CN4desc]
    CN5copy = "<DEL:HOM>"
    CN5desc = "Homozygous deletion"
    template.alts["CN5"] = [CN5copy, CN5desc]
    
    writer = vcf.Writer(open(output, "w"), template)
    for rec in fixed_vcf:
        #print(rec)
        writer.write_record(rec)


# Checks the header of the vcf to determine its origin
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
    parser.add_argument("-r", "--record", nargs="?", action='store', type=str, help=':Specify which record ya wanna see. Only used for testing')

    args = parser.parse_args()
    
    logging.getLogger().setLevel(logging.INFO)
    inp = args.vcf_input
    outp = args.vcf_output
    rec = args.record

    source_program = determine_input(inp)
    print(source_program)

    if source_program == "Canvas":
        fixed_pyvcf = mod_canvas_vcf(read_vcf_new(inp))
        write_vcf(fixed_pyvcf, outp, read_vcf_new(inp))
    elif source_program == "Manta":
        print("Manta not yet implemented ... sorry")


if __name__ == "__main__":
    main()
