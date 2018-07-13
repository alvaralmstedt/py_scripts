#!/usr/bin/env python

# How to run:
# 10x_rename_files.py <folder containing fastqs>
# Check output to see that the files have been renamed correctly.

import os
from sys import argv
import re
import glob

path = argv[1]

file_list = []
name_list = []
iterator = 0

for filename in sorted(glob.glob(os.path.join(path, "*.fastq.gz"))):

    directory = os.path.dirname(filename)
    samplename = os.path.basename(directory)

    # Split up the names of input files with underscores, full stops and hypens as delimiters
    sn = re.split("_|\.|-", os.path.basename(filename))
    for i in reversed(sn):
        if len(i) == 1 and i == "1" or i == "2":
            fwrev = i
            print("STHLM-style names detected \n fwrev = %s" % fwrev)
            break
        elif len(i) == 2 and i[0] == "R":
            fwrev = i[1]
            print("CLC-style names detected \n fwrev = %s" % fwrev)
            break
    if not fwrev:
        raise Exception

    # Set new filename
    new_name = samplename + "_" + "S1" + "_" + "L00" + sn[3][0] + "_" + "R" + fwrev + "_" + "001.fastq.gz"

    # If the name is a duplicate, increase the lane number
    lane = 1
    lane_static = "L00"
    while new_name in file_list:
        if len(lane_static + str(lane)) > 4:
            lane_static = lane_static.replace(lane_static[1], "", 1)
        new_name = samplename + "_" + "S1" + "_" + lane_static + str(lane) + "_" + "R" + fwrev + "_" + "001.fastq.gz"
        lane += 1

    # Never used but will throw an error if the filename somehow already exists
    if new_name in file_list:
        print("New name = " + new_name)
        print("\n")
        print("file_list= " + str(file_list))
        exit()

    # Append the chosen name to a list that is used to prevent duplicates
    file_list.append(new_name)

    # Print to screen so that user can double-check that it looks right
    print(os.path.basename(filename))
    print("... has been renamed to ...")
    print(new_name)
    print("\n".rstrip())

    # Rename the file
    os.rename(filename, os.path.join(directory, new_name))

    iterator += 1

print(samplename + " contents successfully renamed!")