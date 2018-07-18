#!/usr/bin/env python

import csv
from sys import argv

def bed_table_reader(infile):
    with open(infile, "r") as table:
        fieldnames = ["chr", "start", "stop", "some_number", "a_dot", "gene_id"]
        table_reader = csv.DictReader(table, delimiter='\t', fieldnames=fieldnames)
        table_contents = []
        for i in table_reader:
            table_contents.append(i)
        return table_contents


def treat_data(input_csv):
    data = input_csv
    for row in data[1:]:
        for other_row in data:
            if row == other_row:
                continue
            elif (row["chr"] == other_row["chr"]) and (int(row["start"]) < int(other_row["stop"]) < int(row["stop"])):
                print("if1: changing {} to {}".format(row["start"], other_row["stop"]))
                row["start"] = str(int(other_row["stop"]))
            if (row["chr"] == other_row["chr"]) and (int(row["start"]) < int(other_row["start"]) < int(row["stop"])):
                print("if2: changing {} to {}".format(row["stop"], other_row["stop"]))
                row["stop"] = str(int(other_row["start"]))
    return data


def write_data_to_file(treated_data, table_out):
    with open(table_out, "a+") as outfile:
        fieldnames = ["chr", "start", "stop", "some_number", "a_dot", "gene_id"]
        writer = csv.DictWriter(outfile, delimiter='\t', fieldnames=fieldnames)
        for i in treated_data[1:]:
            writer.writerow(i)

if __name__ == "__main__":
    
    input_file = argv[1]
    output_file = argv[2]
    
    with open(input_file, "r") as read_first_line:
        with open(output_file, "w+") as print_first_line:
            linerino = read_first_line.readline()
            print_first_line.write(linerino)

    write_data_to_file(treat_data(bed_table_reader(input_file)), output_file)

