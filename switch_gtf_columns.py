#!/apps/bio/software/anaconda2/envs/wgspdfreport/bin/python

from sys import argv
import pandas as pd
import numpy as np
import csv


def main():
    gtf_in = argv[1]
    gtf_out = argv[2]
    #pandas_blah(gtf_in)
    csv_func(gtf_in, gtf_out)



def modify_csv(csv):
    returno_dude = []
    for l in csv:
        gene_info = l["geneinfo"].split(";")
        #print(gene_info)
        if len(gene_info) > 3:
            #print(gene_info[1])
            new_id = gene_info[1].replace("gene_symbol", "gene_id", 1)
            new_symbol = gene_info[0].replace("gene_id", "gene_symbol", 1)
            #print("NEW ID: " + new_id + "\n", "NEW_SYMBOL: " + new_symbol + "\n")
            
            new_gene_info = [new_id, new_symbol, gene_info[2], gene_info[3]]
            #new_gene_info = [gene_info[1], gene_info[0], gene_info[2], gene_info[3]] #It specifically wants gene_id first
            ngi_list = ";".join(new_gene_info)
            #print(ngi_list)
            line_dict = {"chr": l["chr"], "flybase": l["flybase"], "type": l["type"], "start": l["start"], "stop": l["stop"], "dot1": l["dot1"], 
                         "direction": l["direction"], "frame": l["frame"], "geneinfo": ngi_list}
            returno_dude.append(line_dict)
            #print(line_dict)
        else:
            new_id = gene_info[1].replace("gene_symbol", "gene_id", 1)
            new_symbol = gene_info[0].replace("gene_id", "gene_symbol", 1)
            
            
            new_gene_info = [new_id, new_symbol] #it specifically wants gene_id first
            ngi_list = ";".join(new_gene_info)
            line_dict = {"chr": l["chr"], "flybase": l["flybase"], "type": l["type"], "start": l["start"], "stop": l["stop"], "dot1": l["dot1"],
                         "direction": l["direction"], "frame": l["frame"], "geneinfo": ngi_list}
            returno_dude.append(line_dict)

    return returno_dude


def csv_func(gtf_in, gtf_out):
    with open(gtf_in, "r") as gtf:
       fieldnames = ["chr", "flybase", "type", "start", "stop", "dot1", "direction", "frame", "geneinfo"] 
       gtf_reader = csv.DictReader(gtf, delimiter='\t', fieldnames=fieldnames)
       table_contents = []
       for i in gtf_reader:
           table_contents.append(i)
       modded_csv = modify_csv(table_contents)
       #print(modded_csv)       
       with open(gtf_out, "w+") as out:
           
           #fieldnames = ["chr", "flybase", "type", "start", "stop", "dot1", "direction", "frame", "geneinfo"]
           #gtf_writer = csv.DictWriter(out, delimiter='\t', fieldnames=fieldnames, escapechar=" ", quoting=csv.QUOTE_NONE)
           for m in modded_csv:
               abbrev_geneinfo = m['geneinfo'][1:]
               out.write(f"{m['chr']}\t{m['flybase']}\t{m['type']}\t{m['start']}\t{m['stop']}\t{m['dot1']}\t{m['direction']}\t{m['frame']}\t{abbrev_geneinfo};" + "\n")
               #print(m)
           #    gtf_writer.writerow({"chr": m["chr"],
           #                         "flybase": m["flybase"],
           #                         "type": m["type"],
           #                         "start": m["start"],
           #                         "stop": m["stop"],
           #                         "dot1": m["dot1"],
           #                         "direction": m["direction"],
           #                         "frame": m["frame"],
           #                         "geneinfo": m['geneinfo'] + ';'})


#not used
def pandas_blah(gtf_in):
    with open(gtf_in, "r") as gtf:
        hnames = ["Chromososme", "FlyBase", "Type", "Start", "Stop", "Dot1", "Direction", "Gene"]
        df = pd.read_csv(gtf, sep="\t", names=hnames)
        #print(df.Gene.str.split(";",expand=True))
        df[["gene_id", "gene_symbol", "transcript_id", "transcript_symbol", "nothing", "nothing2"]] = df.Gene.str.split(";",expand=True)
        column_titles = ["Chromososme", "FlyBase", "Type", "Start", "Stop", "Dot1", "Direction", "gene_symbol", "gene_id" , "transcript_id", "transcript_symbol", "nothing", "nothing2"]
        new_df = df.reindex(columns=column_titles)
        new_df = new_df.drop(["nothing", "nothing2"], axis=1)
        #new_df = new_df.transcript_id.fillna(value=pd.np.nan, inplace=True)
        #new_df = new_df.fillna(value=pd.np.nan, inplace=True)
        new_df['Gene'] = new_df[["gene_id", "gene_symbol", "transcript_id", "transcript_symbol"]].apply(lambda x: ';'.join(x), axis = 1)
        #new_df['Gene'] = new_df[["gene_id", "gene_symbol", "transcript_id" , "transcript_symbol"]].apply(lambda x: x.str.cat(), axis = 1)
        print(new_df)


if __name__ == "__main__":
    main()
