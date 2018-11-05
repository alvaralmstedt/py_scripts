#!/usr/bin/env python

import argv
import csv


def fix_exponent(infile, outfile):
    with open(infile, "r") as csv_in:
        csv_reader = csv.reader(csv_in, delimiter=',')


infile = argv[1]
outfile = argv[2]
