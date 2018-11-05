#!/usr/bin/env python

import os
import argparse
import vcf
import glob
import operator
import math


# Get files to be searched for artifacts and save each varaint as vcf object
def get_infiles(vcf_path):
    vcf_path = glob.glob(os.path.join(vcf_path, "*"))
    vcf_list = []
    for each_file in vcf_path:
        with open(each_file, "r") as vcf_file:
            vcf_reader = vcf.Reader(vcf_file)
            for i in vcf_reader:
                vcf_list.append(i)
    return vcf_list


# Get new vcf file to be filtered
# def get_file_to_filter(vcf_path):
    # with open vcf_pa
    # pass


# Parse all the variants and save chromosome, pos, ref and alt in tuples as string with number of occurrences linked
def parse_vcf(inlist):
    duplicate_entries = {}
    for entry in inlist:
        relevant_line = [entry.CHROM, entry.POS, entry.REF, entry.ALT]
        duplicate_entries[str(relevant_line)] = 0
        for other_lines in inlist:
            if relevant_line == [other_lines.CHROM, other_lines.POS, other_lines.REF, other_lines.ALT]:
                duplicate_entries[str(relevant_line)] += 1
    sorted_duplicates = sorted(duplicate_entries.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_duplicates


# Select the variants with top 10% occurrence over all files input
def select_top_ten_percent(sorted_duplicates):
    number_of_files = max(sorted_duplicates, key=lambda x: x[1])[1]
    morethan = number_of_files * 0.9
    morethan = int(math.ceil(morethan))
    toptenp = []
    for line in sorted_duplicates:
        if int(line[1]) >= morethan:
            print(line)
            toptenp.append(line)
    return toptenp


# Save the artifact list
def write_vcf_artifacts(indata, outfile):
    with open(outfile, 'w+') as out:
        for line in indata:
            out.write(str(line) + "\n")


# Use the artifact list to filter the current vcf file
def filter_a_file(artifact_filter, to_be_filtered):
    tup_tbf = parse_vcf(get_infiles(to_be_filtered))
    full_infile = get_infiles(to_be_filtered)
    filtered_input = filter(lambda x: x not in set(artifact_filter), tup_tbf)
    for i in full_infile:
        for j in filtered_input:
            if j.CHROM == i.CHROM and j.POS == i.POS:
                print(i)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', nargs='?', help='Input folder', type=str, required=True)
    parser.add_argument('-o', '--output', nargs='?', help='Output file', type=str, required=True)
    parser.add_argument('-i', '--filter', nargs='?', help='file to be used as filter', type=str, required=False)
    parser.add_argument('-t', '--tbf', nargs='?', help='file to be filtered', type=str, required=False)

    args = parser.parse_args()
    vcf_folder = args.folder
    output = args.output
    the_filter = args.filter
    tbf = args.tbf

    print(vcf_folder)
    # write_vcf_artifacts(select_top_ten_percent(parse_vcf(get_infiles(vcf_folder))), output)
    filter_a_file(the_filter, tbf)