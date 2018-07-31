#!/usr/bin/env python

import pandas as pd
import matplotlib
matplotlib.use("tkagg")
import matplotlib.pyplot as plt
import numpy as np
from sys import argv
from pandas.plotting import scatter_matrix
from mpldatacursor import datacursor
import argparse

# The function tkes the csv files and returns a pandas dataframe with all the data
def get_all_data(csv_file, mappings):
    my_data = pd.read_csv(csv_file, dtype={"Mapping": str})
    fix_coverage = lambda x: x/mappings
    my_data["Coverage"] = my_data["Coverage"].apply(fix_coverage)
    return my_data


# This function takes a the full pandas dataframe and returns only the data from one gene
def get_gene_data(all_data, gene):
    all_data = get_all_data(all_data, mappings)
    gene_data = all_data.loc[all_data['Name'].str.contains(str(gene))]
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
        if current_gene in current_exon and row["Name"] != current_exon:
            current_exon = row["Name"]
            current_count += 1
            data.at[idx, "Target region position"] = str(current_count)
        #COMPLETELY NEW GENE
        elif current_gene not in current_exon and row["Name"] != current_exon:
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
def create_scatter_plot(gene, csv_input):
    data_for_plot = get_gene_data(csv_input, gene)
    #print(data_for_plot)
    modded_data = get_good_targets(data_for_plot) 
    data_for_plot = modded_data
    transcripts = get_exons_in_gene(csv_input, gene)
    #print(transcripts)
    dfp_evens = pd.DataFrame()
    dfp_odds = pd.DataFrame()
    for tr in transcripts["exon_name"]:
        exon = str(tr)
        #print(exon)
        exon_number = int(exon.split("_")[-1])
        #print("exon_num: ", exon_number)
        even_exon = exon_number % 2 == 0
        if even_exon:
            even_exon = data_for_plot.loc[data_for_plot["Name"].str.contains(str(exon))]
            #print("inside even")
            #print(even_exon)
            dfp_evens = dfp_evens.append(even_exon)
            #dfp_evens[exon] = data_for_plot.loc["Name"].str.contains(exon)
        else:
            odd_exon = data_for_plot.loc[data_for_plot["Name"].str.contains(str(exon))]
            dfp_odds = dfp_odds.append(odd_exon)

    print(dfp_evens)
    #dfp1_plot = dfp_evens.plot(x="Reference position", y="Coverage", kind='scatter', color='black', label="even_numbered_exons")
    #dfp1_plot = dfp_evens.plot(x="Target region position",  y="Coverage", kind='scatter', color='black', s=5, marker='s')
    #datacursor(hover=True, point_labels=dfp_evens["Name"])
    #dfp_odds.plot(x="Reference position", y="Coverage", kind='scatter', color='b', label="odd_numbered_exons", ax=dfp1_plot)
    #dfp_odds.plot(x="Reference position", y="Coverage", kind='scatter', color='b', label="odd_numbered_exons", ax=dfp1_plot)
    
    #dfp_odds.plot(x="Target region position", y="Coverage", kind='scatter', color='b', s=5, ax=dfp1_plot, marker="o")
    #data_for_plot.plot(x="Target region position", y="Coverage", kind='scatter', color='y', s=5, ax=dfp1_plot, marker="o")
   
    if_exists = []
    colors = ["r", "g", "b", "k", "y", "m"]
    color_selector = 0
    checker = False
    for i in data_for_plot.index:
        val = data_for_plot.get_value(i, "Name")
        if val not in if_exists:
            if not checker:
                initial_plot = data_for_plot[data_for_plot["Name"] == str(val)]
                initial_plot = initial_plot.plot(x="Target region position", y="Coverage", label=val, kind='scatter', color='orange', s=5, marker="o", yticks=range(0, 10000, 100))
                checker = True
            else:
                my_dataframe = data_for_plot[data_for_plot["Name"] == str(val)]
                my_dataframe.plot(x="Target region position", y="Coverage", label=val, kind='scatter', color=str(colors[color_selector]), s=5, ax=initial_plot, marker="o")
            if color_selector < 5:
                color_selector += 1
            else:
                color_selector = 0
        if_exists.append(val)
        
    #iold_exon = False
    #exon_plots = {}
    #for idx, row in data_for_plot.iterrows():
    #    exon_name = row["Name"]
    #    if exon_name != old_exon:
    #        exon_line = data_for_plot.loc[data_for_plot["Name"].str.contains(str(exon_name))]
    #        #print(exon_plots[exon_name])
    #        if not exon_name in exon_plots:
    #            import pdb; pdb.set_trace()
    #            exon_plots = {str(exon_name):pd.DataFrame()}
    #        exon_plots[exon_name].append(exon_line)
    #        #label_plots.plot(x="Target region position", y="Coverage", label=exon_name, kind='scatter', color='b', s=5, ax=dfp1_plot, marker="o")
    #    old_exon = exon_name
    
    #for exons in exon_plots:
    #    exons.plot(x="Target region position", y="Coverage", label=f"{exons}", kind='scatter', color='b', s=5, ax=dfp1_plot, marker="o")
    
    maximums = {}
    for i in data_for_plot.index:
        name_val = data_for_plot.get_value(i, "Name")
        num_val = data_for_plot.get_value(i, "Target region position")
        maximums[name_val] = num_val
    max_list = list(maximums.values())
    max_list.insert(0, 0)
    print(max_list)
    initial_plot.set_xticks(np.asarray(max_list))

    #ax = data_for_plot.plot.scatter(x='Target region position', y='Coverage', alpha=0.5)
    #for i, txt in enumerate(data_for_plot.Name):
    #        ax.annotate(txt, (data_for_plot.x.iat[i],data_for_plot.y.iat[i]))

    #ax = data_for_plot.set_index('')
    #label_point_orig(dfp1_plot.x, dfp1_plot.y, data_for_plot.Name, plt)


    datacursor(hover=True)
    #data_for_plot.plot("Reference position", "Coverage", kind='scatter', color='black')
    #scatter_matrix(data_for_plot)
    #data_for_plot[["Reference position", "Coverage"]].hist.plot()
    plot_title = data_for_plot.iat[1,2].split("_", 1)[0]
    plt.suptitle(plot_title, fontsize=30)
    lgnd = plt.legend(fontsize=12)
    for handles in lgnd.legendHandles:
        handles._sizes = [150]
    #plt.plot()
    
    plt.grid()
    plt.show()

def create_scatter_plot_labels():
    pass

if __name__ == "__main__":
    csv_input = argv[1]
    mappings = 1
    mappings = int(argv[3])

    genes_and_transcripts_df, uniq_genes_list = get_gene_names(csv_input)
    my_gene = uniq_genes_list[0]
    my_gene = argv[2]
    create_scatter_plot(my_gene, csv_input)

    #print(genes_and_transcripts_df)
