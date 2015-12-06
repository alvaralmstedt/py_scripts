#!/usr/bin/python

"""
Usage: fasta_capitals.py fastafile.fasta [C/L] > result.fasta
"""

from sys import argv
from string import maketrans

filename = argv[1]
action = argv[2]

def capitals(fil):

    transfrom = "abcdefghijklmnopqrstuvxyz"
    transto = "ABCDEFGHIJKLMNOPQRSTUVXYZ"
    transtab = maketrans(transfrom, transto)

    with open(fil) as inputfile:
        for line in inputfile:
            if line.startswith(">"):
                print line.rstrip()
            else:
                print line.translate(transtab).rstrip()

def lowercase(fil):

    transfrom = "ABCDEFGHIJKLMNOPQRSTUVXYZ"
    transto = "abcdefghijklmnopqrstuvxyz"
    transtab = maketrans(transfrom, transto)

    with open(fil) as inputfile:
        for line in inputfile:
            if line.startswith(">"):
                print line.rstrip()
            else:
                print line.translate(transtab).rstrip()

if str(action) == "c" or str(action) == "C":
    capitals(filename)
elif str(action) == "l" or str(action) == "L":
    lowercase(filename)
else:
    print "Please input 'C' or 'L' as argument 2 in order to make all nt/aa into capitals or lowercase, respectively "