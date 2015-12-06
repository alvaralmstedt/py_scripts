#!/usr/bin/python

"""
Usage: fasta_capitals.py fastafile.fasta [C/L] > result.fasta
"""

from sys import argv
from string import maketrans

argv[1] = filename
argv[2] = action

def capitals(fil):

    transfrom = "abcdefghijklmnopqrstuvxyz"
    transto = "ABCDEFGHIJKLMNOPQRSTUVXYZ"
    transtab = maketrans(transfrom, transto)

    with open(fil) as inputfile:
        for line in inputfile:
            if line.startswith(">"):
                print line
            else:
                print line.translate(transtab)

def lowercase(fil):
    transfrom = "ABCDEFGHIJKLMNOPQRSTUVXYZ"
    transto = "abcdefghijklmnopqrstuvxyz"
    transtab = maketrans(transfrom, transto)

    with open(fil) as inputfile:
        for line in inputfile:
            if line.startswith(">"):
                print line
            else:
                print line.translate(transtab)

if str(action) == "c" or str(action) == "C":
    capitals(filename)
elif str(action) == "l" or str(action) == "L":
    lowercase(filename)
else:
    print "Please input 'C' or 'L' as argument 2 in order to make all nt/aa into capitals or lowercase, respectively "