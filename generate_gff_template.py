from sys import argv
import csv


def read_fasta(fasta):
    working_headers = []
    completed_headers = []
    with open(fasta, "r") as in_file:
        for line in in_file:
            each_line = line.split(" ")
            for list_element in each_line:
                if str(list_element).startswith(">"):
                    working_headers.append(list_element.rstrip())
        for each_header in working_headers:
            completed_headers.append(each_header[1:])
    return sorted(completed_headers)


def write_gff(header_list, output_file_name):
    with open(output_file_name, 'w+') as gff_out:
        fieldnames = ["header", "source", "type", "start", "stop", "score", "orientation", "period", "ID"]
        gff_writer = csv.DictWriter(gff_out, delimiter='\t', fieldnames=fieldnames)
        types = ["gene", "CDS", "exon", "intron", "5'-UTR", "3'-UTR"]
        types_iterator = 0
        lines_per_type = 6      # number of lines per contig
        for header in header_list:
            for i in range(lines_per_type):
                gff_writer.writerow({"header": str(header),
                                     "source": "manual",
                                     "type": str(types[types_iterator]),
                                     "start": "0",
                                     "stop": "0",
                                     "score": ".",
                                     "orientation": str(orienter(header)),
                                     "period": ".",
                                     "ID": "ID=%s;Parent=%s;" %
                                           (str(header) + "_" + str(types[types_iterator]), header)})
                if types_iterator < 5:
                    types_iterator += 1
                else:
                    types_iterator = 0


def orienter(header):
    if str(header).endswith("_revcomp"):
        return "-"
    return "+"

fasta_file = argv[1]
outfile_name = argv[2]

write_gff(read_fasta(fasta_file), outfile_name)
