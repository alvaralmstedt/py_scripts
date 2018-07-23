#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sys import argv


def get_all_data(csv_file):
    my_data = pd.read_csv(csv_file, dtype={"Mapping": str})
    return my_data


def get_gene_data(all_data, gene):
    all_data = get_all_data(all_data)
    gene_data = all_data.loc[all_data['Name'] == gene]
    return gene_data


def get_gene_names(all_data):
    all_data = get_all_data(all_data)
    all_names = all_data.Name.drop_duplicates(keep='first')
    #gene_names = pd.DataFrame(all_names.Name.str.split('_',1).tolist(), columns = ['Gene','Transcript_exon'])
    genes_and_transcripts = all_names.str.split("_", 1, expand=True)
    gene_names = []
    for Name in all_names:
        gene_names.append(Name.split("_", 1)[0])
    unique_gene_names = list(set(gene_names))
    print(type(all_data))
    print(type(all_names))
    #print(genes_and_transcripts)
    return genes_and_transcripts, unique_gene_names


def create_scatter_plot(gene, csv_input):
    data_for_plot = get_gene_data(get_all_data(csv_input), gene)
    

if __name__ == "__main__":
    csv_input = argv[1]


    genes_and_transcripts_df, uniq_genes_list = get_gene_names(csv_input)
    my_gene = uniq_genes_list[0]
    create_scatter_plot(my_gene, csv_input)

    #print(genes_and_transcripts_df)
