#!/usr/bin/env python

from sys import argv
import csv

input_file = argv[1]
output = argv[2]

with open(input_file, 'r') as inp:
     reader = list(csv.reader(inp, delimiter=";"))
     with open(output, 'w') as out:
         writer = csv.writer(out, quotechar='"', quoting=csv.QUOTE_ALL, delimiter=",")
         for row in reader:
             if len(row) < 1 or "totreads:" in row[1]:
                 writer.writerow(row)
             else:
                 newrow = row[0:1] + [it.upper() for it in row[1:]]
                 writer.writerow(newrow)



#with open(input, "r") as infile, open(output, "w") as outfile:
   #reader = csv.reader(infile)
   #content = infile.readlines()
#   content = [row for row in infile.read()]
#   header = content[0]
   #next(reader, None)  # skip the headers
#   writer = csv.writer(outfile, quotechar='"', quoting=csv.QUOTE_ALL)
#   writer.writerow(header)
#   for row in content[1:]:
       # process each row
#       not_up = [row[0]]
#       upped = [e.upper() for e in row[1:]]
#       writer.writerow(not_up + upped)

