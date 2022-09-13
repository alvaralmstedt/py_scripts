#!/usr/bin/env python

import pandas as pd
import matplotlib
matplotlib.use("tkagg")
import matplotlib.pyplot as plt
import numpy as np
from sys import exit
from sys import argv
from pandas.plotting import scatter_matrix
from mpldatacursor import datacursor
import argparse
from os import getcwd

# The function tkes the csv files and returns a pandas dataframe with all the data
def get_all_data(csv_file, mappings):
    my_data = pd.read_csv(csv_file, dtype={"Mapping": str})
    fix_coverage = lambda x: x/mappings
    my_data["Coverage"] = my_data["Coverage"].apply(fix_coverage)
    return my_data


# This function takes a the full pandas dataframe and returns only the data from one gene
def get_gene_data(all_data, gene):
    all_data = get_all_data(all_data, mappings)
    gene_data = all_data.loc[all_data['Name'].str.contains(str(gene + "_"))]
    return gene_data


# This function takes the full pandas dataframe and returns a datafram with genes and their transcript and a list with all gene names
def get_gene_names(all_data):
    if not isinstance(all_data, pd.core.frame.DataFrame):
        all_data = get_all_data(all_data, mappings)
    all_names = all_data.Name.drop_duplicates(keep='first')
    #gene_names = pd.DataFrame(all_names.Name.str.split('_',1).tolist(), columns = ['Gene','Transcript_exon'])
    genes_and_transcripts = all_names.str.split("_", 1, expand=True)
    gene_names = []
    for Name in all_names:
        gene_names.append(Name.split("_", 1)[0])
    unique_gene_names = list(set(gene_names))
    return genes_and_transcripts, unique_gene_names

    parser = argparse.ArgumentParser(prog='create_coverage_grapyh.py', formatter_class=argparse.RawDescriptionHelpFormatter,
            description="""This script will read a csv created from the 'Coverage table' output of the CLC tool 'QC for target sequencing'.
            
            
            
            """)
    parser.add_argument("-c", "--csv", nargs="?", type=str, help="Path to the CSV files you want to plot. Required.")
    parser.add_argument("-g", "--gene", nargs="?", type=str, help="Specify the gene for which you want to generate a plot. put 'all' to run all genes. Default: Random.")
    parser.add_argument("-o", "--output", nargs="?", type=str, help="Output folder where the plot images will be saved. If it doesnt exist, we will attempt to create it. Default: cwd")
    parser.add_argument("-m", "--mappings", nargs="?", type=int, help="How many mappings you have merged in CLC before running QC for target sequencing. Default: 1")

# This function takes data and gene and returns which transcripts are in that gene
def get_exons_in_gene(all_data, gene):
    if isinstance(all_data, pd.core.frame.DataFrame):
       pass
    
    g_t, u_g_n = get_gene_names(all_data)
    g_t.columns = ['gene_name', 'exon_name']
    transcripts = g_t.loc[g_t["gene_name"].str.contains(gene)]
    #with pd.option_context('display.max_rows', None, 'display.max_columns', 3):
    #        print(transcripts)
    return transcripts
    

# This function takes the full data and transforms the 'Target region position' of the data into one that
# looks more continuous in the plot
def get_good_targets(data):
    #print(data)
    new_dataframe = pd.DataFrame() 
    current_exon = ''
    current_gene = ''
    current_count = 0
    lines_for_gene = {} 
    for idx, row in data.iterrows():
        target = row["Target region position"]
        current_gene = str(row["Name"].split("_", 1)[0])
        #SET EXON IF EMPTY
        lines_for_gene[current_gene] = 1
        #NEW EXON, SAME GENE
        if current_gene + "_" in current_exon and row["Name"] != current_exon:
            current_exon = row["Name"]
            current_count += 1
            data.at[idx, "Target region position"] = str(current_count)
        #COMPLETELY NEW GENE
        elif current_gene + "_" not in current_exon and row["Name"] != current_exon:
            current_exon = row['Name']
            current_count = 1
            data.at[idx, "Target region position"] = str(current_count)
        #SAME EXON
        elif row["Name"] == current_exon:
            current_count += 1
            data.at[idx, "Target region position"] = str(current_count)
        else:
            continue
            print(current_count)
    return data



# This fuction will create a matplotlib scatterplot with coverage numbers from one of the genes
def create_scatter_plot(gene, csv_input, output):
    data_for_plot = get_gene_data(csv_input, gene)
    #print(data_for_plot)
    modded_data = get_good_targets(data_for_plot) 
    data_for_plot = modded_data
    transcripts = get_exons_in_gene(csv_input, gene)
    dfp_evens = pd.DataFrame()
    dfp_odds = pd.DataFrame()
    for tr in transcripts["exon_name"]:
        exon = str(tr)
        exon_number = int(exon.split("_")[-1])
        even_exon = exon_number % 2 == 0
        if even_exon:
            even_exon = data_for_plot.loc[data_for_plot["Name"].str.contains(str(exon))]
            #print(even_exon)
            dfp_evens = dfp_evens.append(even_exon)
        else:
            odd_exon = data_for_plot.loc[data_for_plot["Name"].str.contains(str(exon))]
            dfp_odds = dfp_odds.append(odd_exon)

    #print(dfp_evens)
   
    if_exists = []
    colors = ["r", "g", "b", "k", "y", "m"]
    color_selector = 0
    checker = False
    for i in data_for_plot.index:
        val = data_for_plot.get_value(i, "Name")
        if val not in if_exists:
            if not checker:
                initial_plot = data_for_plot[data_for_plot["Name"] == str(val)]
                initial_plot = initial_plot.plot(x="Target region position", y="Coverage", label=val, kind='scatter', color='orange', s=5, marker="o", figsize=(40, 15))
                checker = True
            else:
                my_dataframe = data_for_plot[data_for_plot["Name"] == str(val)]
                my_dataframe.plot(x="Target region position", y="Coverage", label=val, kind='scatter', color=str(colors[color_selector]), s=5, ax=initial_plot, marker="o")
            if color_selector < 5:
                color_selector += 1
            else:
                color_selector = 0
        if_exists.append(val)
        
    maximums = {}
    for i in data_for_plot.index:
        name_val = data_for_plot.get_value(i, "Name")
        num_val = data_for_plot.get_value(i, "Target region position")
        maximums[name_val] = num_val
    max_list = list(maximums.values())
    max_list.insert(0, 0)
    #print(max_list)
    max_y_for_plot = max(data_for_plot["Coverage"])
    major_ticks = np.arange(0, int(max_y_for_plot) + 100, 500)
    minor_ticks = np.arange(0, int(max_y_for_plot) + 100, 100)
    try:
        initial_plot.set_yticks(major_ticks)
        initial_plot.set_yticks(minor_ticks, minor=True)
        initial_plot.set_xticks(np.asarray(max_list))
    except UnboundLocalError:
        print(f"ERROR: Please make sure that the gene {gene} is in the CSV-file you have provided")
        exit(1)
    datacursor(hover=True)
    plot_title = data_for_plot.iat[1,2].split("_", 1)[0]
    plt.suptitle(plot_title, fontsize=30)
    #lgnd = plt.legend(fontsize=12, bbox_to_anchor=(0.5, 1.2), ncol=10, loc='upper center')
    lgnd = plt.legend(fontsize=12, bbox_to_anchor=(0.5, -0.05),  loc='upper center', ncol=5, fancybox=True, shadow=True)
    for handles in lgnd.legendHandles:
        handles._sizes = [150]
    plt.grid(which='major', alpha=0.7)
    plt.grid(which='minor', alpha=0.2)
    if not output:
        plt.show(bbox_extra_artists=(lgnd,), bbox_inches='tight')
    else:
        try:
            plt.savefig(f'{output}/{gene}.png', figsize=(2000, 2000), bbox_artists=(lgnd,), bbox_inches='tight')
        except:
            cwd = getcwd()
            plt.savefig(f'{cwd}/{gene}.png')
    plt.close()

def create_scatter_plot_labels():
    pass

if __name__ == "__main__":
    csv_input = argv[1]
    mappings = 1
    #mappings = int(argv[3])

    parser = argparse.ArgumentParser(prog='create_coverage_grapyh.py', formatter_class=argparse.RawDescriptionHelpFormatter,
            description="""This script will read a csv created from the 'Coverage table' output of the CLC tool 'QC for target sequencing'.
            
            
            
            """)
    parser.add_argument("-c", "--csv", nargs="?", type=str, help="Path to the CSV files you want to plot. Required.")
    parser.add_argument("-g", "--gene", nargs="?", type=str, help="Specify the gene for which you want to generate a plot. put 'all' to run all genes. Default: Random.")
    parser.add_argument("-o", "--output", nargs="?", type=str, help="Output folder where the plot images will be saved. If it doesnt exist, we will attempt to create it. Default: cwd")
    parser.add_argument("-m", "--mappings", nargs="?", type=int, help="How many mappings you have merged in CLC before running QC for target sequencing. Default: 1")

    args = parser.parse_args()

    mappings = args.mappings
    csv_input = args.csv
    output = args.output
    if output:
        plt.ioff()
    genes_and_transcripts_df, uniq_genes_list = get_gene_names(csv_input)
    my_gene = uniq_genes_list[0]
    #my_gene = argv[2]
    my_gene = args.gene
    if my_gene.lower() == "all":
        response = input(f"Are you sure you want to create plots for all genes in the folder '{output}'? It will take a while. (type 'yes' to confirm): ")
        if response.lower() == "yes":
            for every_gene in uniq_genes_list:
                print(f'Creating plot for {every_gene} in directory: {output}')
                create_scatter_plot(every_gene, csv_input, output)
        else:
            print("Thank you and goodbye!")
            exit()
    else:
        create_scatter_plot(my_gene, csv_input, output)

    #print(genes_and_transcripts_df)
