#!/usr/bin/env python

import os
import argparse
import datetime
import vcf
import subprocess
import logging

class BadBamFileError(Exception):
    pass
class PeriodsInVcfError(Exception):
    pass


def precheck_inputs(bam, vcf, igvuser, outpath, runtype):
    if not bam.endwith(".bam"):
        raise BadBamFileError(f"The bam file supplied does not look like a bam file: {bam}")
    vcf_reader = vcf.Reader(open(vcf, 'r'))
    for record in vcf_reader:
        if record.FILTER == None:
            raise PeriodsInVcfError(f"This vcf: {vcf} uses periods for pass values instead of PASS. We don't want that.")
    igvusers = os.listdir("/seqstore/webfolders/igv/users")
    valid_user = False
    for userfiles in igvusers:
        if igvuser in userfiles:
            valid_user = True
    if valid_user == False:
        raise IgvUserDoesNotExistError(f"The user '{igvuser}' does not seem to have an xml present on seqstore")
    if os.path.isdir(outpath):
        info.logging(f"The output path you have supplied: {outpath} does not yet exist. It will be created by canvas")

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
    ploidy_file = determine_sex(vcf)

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


# This will determine the sex of the sample by looking if there are eny entries in the Y-chromosome in the normal vcf
def determine_sex(vcf_normal):
    vcf_reader = vcf.Reader(open(vcf_normal, 'r'))
    for record in vcf_reader:
        if "Y" in record.CHROM:
            logging.info("The sex was determined to be MALE")
            return "/apps/bio/software/canvas/male_hg19.vcf"
    logging.info("The sex was determined to be FEMALE")
    return "/apps/bio/software/canvas/female_hg19.vcf"



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
    logging.info(f"The input arguments were set to: runtype={runtype} bam={bam_file}, normal vcf={normal_vcf}, IGV user={igv_user}, output path={output_path}")

    ports = [8008, 80]

    precheck_inputs(bam_file, normal_vcf, igv_user, output_path, runtype)
