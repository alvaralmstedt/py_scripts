#!/usr/local/opt/bin/python

from sys import argv

"""
Quick script to work around grep issue.
"""


def get_forward(headers, sequences, output):
    with open(headers, "r") as head:
        with open(sequences, "r") as seq:
            with open(output, "w+") as out:
                header_content = head.readlines()
                seq_content = seq.readlines()
                next_line = False
                for line in header_content:
                    if line in seq_content:
                        out.write(line)
                        next_line = True
                        continue
                    if next_line:
                        out.write(line)
                        next_line = False

get_forward(argv[1], argv[2], argv[3])

