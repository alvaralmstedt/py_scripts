#!/Users/alvaralmstedt/anaconda2/bin/python
# -*- coding: utf-8 -*-

import time
import openpyxl
import argparse
from openpyxl.cell import get_column_letter, column_index_from_string
import numpy as np
np.set_printoptions(threshold=np.inf)

parser = argparse.ArgumentParser(prog='excel_to_vcf.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description="""
This script will attempt to read data from a microsoft excel sheet
and write out data from the selected cells into a minimal VCF file
(v4.1 see http://samtools.github.io/hts-specs/VCFv4.1.pdf).

Some limitations to take into consideration:

1. The variant cells must be formatted as: [REF]>[REF]/[ALT] for correct output.\n
2. Currently there is only support for gene name in the INFO column.

Author: Alvar Almstedt""")

parser.add_argument("excel_table", nargs="?", type=str, help=':Full path to your excel table input file')
parser.add_argument("output", nargs="?", type=str, help=':Specify full output path and filename of the vcf file you want to create')
parser.add_argument("-c", "--chromosome", nargs="?", action='store', type=str, help=':Specify hich excel column the chromosome number is given')
parser.add_argument("-r", "--region", nargs="?", action='store', type=str, help=':Specify which excel column the coordinate of the variant is given')
parser.add_argument("-g", "--gene", nargs="?", action='store', type=str, help=':Specify which excel column contains the gene name')
parser.add_argument("-v", "--variant", nargs="?", action='store', type=str, help=':Specify which excel column contains the variants (format example: T>T/A)')
parser.add_argument("-s", "--sheet", nargs="?", action='store', type=str, help=':Specify sheet name to be used in the excel file')
parser.add_argument("-w", "--rowstart", nargs="?", action='store', type=str, help=':Specify from which row number in the excel file the parsing should start (Default: 1)')
parser.add_argument("-t", "--rowstop", nargs="?", action='store', type=str, help=':Specify to which row number in the excel file the parsing should run (Default: Bottom filled cell)')

args = parser.parse_args()

output = args.output
excel_file = args.excel_table
gene = args.gene
region = args.region
chrom = args.chromosome
variant = args.variant
sheet_name = args.sheet
start = str(int(args.rowstart) - 1)
stop = str(int(args.rowstop) - 1)


def read_excel(excel_file, sheet_name, chrom, variant, gene):
    wb = openpyxl.load_workbook(excel_file)
    try:
        sheet = wb.get_sheet_by_name(str(sheet_name))
    except:
        sheets = wb.get_sheet_names()
        sheet = sheets[0]

    chromosomes = sheet.columns[column_index_from_string(chrom) - 1]
    genes = sheet.columns[column_index_from_string(gene) - 1]
    regions = sheet.columns[column_index_from_string(region) - 1]
    variants = sheet.columns[column_index_from_string(variant) - 1]

    chromlist = make_lists(chromosomes)
    genelist = make_lists(genes)
    regionlist = make_lists(regions)
    variantlist = make_lists(variants)
    references = []
    varts = []
    for i in variant_format(variantlist):
        references.append(i[0])
        varts.append(i[1])
    return np.column_stack((chromlist, references, varts, genelist, regionlist))


def make_lists(columns):
    celllist = []
    for cellObj in columns:
        try:
            celllist.append(str(cellObj.value))
        except UnicodeError:
            try:
                celllist.append(cellObj.value.encode('utf-8'))
            except:
                if str(cellObj.value) is None:
                    celllist.append(str("None"))
    return celllist


def variant_format(variantlist):
    variants = []
    for i in variantlist:
        if ">" in i:
            gtsplit = i.split('>')
            slashsplit = str(gtsplit[1]).split('/')
            variants.append(slashsplit)
        else:
            variants.append(["None", "None"])
    return variants


def write_vcf(inlists, start, stop, output):
    inputs = inlists[int(start):int(stop)+int(start) - 1]
    currenttime = time.strftime('%Y%m%d')
    fileheader = """##fileformat=VCFv4.1
##fileDate=%s
##source=excel_to_vcf.py
##reference=hg19
##INFO=<ID=GI,Number=1,Type=String,Description="Gene Identifier">\n""" % currenttime
    columnheader = "#CHROM" + "\t" + "POS" + "\t" + "ID" + "\t" + "REF" + "\t" + "ALT" + "\t" + "QUAL" + "\t" \
                    + "FILTER" + "\t" + "INFO"
    with open(output, "w+") as out:
        out.write(fileheader)
        out.write(columnheader)
        for i in inputs:
            out.write("\n" + i[0] + "\t" + i[4] + "\t" + "." + "\t" + i[1] + "\t" + i[2] + "\t" + "." + "\t" + "." + "\t" +
                      "GI=" + i[3])

if not start:
    start = int(0)

if not stop:
    listitem = read_excel(excel_file, sheet_name, chrom, gene)
    stop = len(listitem)

write_vcf(read_excel(excel_file, sheet_name, chrom, variant, gene), start, stop, output)