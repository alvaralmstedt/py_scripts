#!/usr/bin/env python

import os
import argparse
import datetime
import vcf
import subprocess
import logging

def precheck_inputs():



def igv_modification(user, user_xml_path, infile, port):
    """
    Adds entries for seg files to user IGV xml list.
    """
    with open(user_xml_path, "r+") as userfile:
        lines_of_file = userfile.readlines()
        bam = os.path.basename(infile)
        lines_of_file.insert(-2,
                             '\t\t<Resource name="%s" path="http://seqstore.sahlgrenska.gu.se:%s/igv/data/%s/%s" />\n' % (
                                 bam, port, user, bam))
        userfile.seek(0)
        userfile.truncate()
        userfile.writelines(lines_of_file)

def main_canvas(bam, vcf, outpath, runtype):
    
    my_env = os.environ.copy()
    canvas_dll = "/apps/bio/software/canvas/1.38.0.1554/Canvas.dll"
    filter13 = "medstore/External_References/Canvas_CLC_HG19_Dataset/custom/Homo_sapiens/UCSC/hg19/Sequence/WholeGenomeFasta/filter13.bed"
    
    if runtype.upper() == "TN" or runtype.upper() == "SOMATIC-WGS":
        run_type = "Somatic-WGS"
        logging.info(f"Canvas sample is being run as: {run_type}")
    elif runtype.upper() == "GERMLINE" or runtype.upper() == "SMALLPEDIGREE-WGS":
        run_type = "SmallPedigree-WGS"
        logging.info(f"Canvas sample is being run as: {run_type}")
    
    args = ["dotnet", canvas_dll, ]
    subprocess.call(args, shell=False, env=my_env)


def create_seg():
    pass

if __name__ == "__main__":

    timestring = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")

    parser = argparse.ArgumentParser()

    parser.add_argument("-b", "--bam", action="store", nargs="?", help="main bam file to be analysed")
    parser.add_argument("-n", "--normal_vcf", action='store', nargs="?", help="vcf for the normal sample")
    parser.add_argument("-u", "--user", action='store', nargs='?', help="user which will be used for igv on seqstore")
    parser.add_argument("-o", "--output", action="store", nargs="?", help="this is the main directory where the canvas output will end up")
    parser.add_argument("-t", "--runtype", action="store", nargs=1, help="this will be which typ of analysis you want to run, either germline or TN")
    args = parser.parse_args()
    
    bam_file = args.bam
    normal_vcf = args.normal_vcf
    igv_user = args.user
    output_path = args.output
    runtype = runtype.args
    logging.info(f"The input arguments were set to: bam={bam_file}, normal vcf={normal_vcf}, IGV user={igv_user}, output path={output_path}")
