#!/usr/bin/env python

import os
import argparse
import datetime
import vcf
import subprocess
import logging
import shutil
import sys
import math

class BadBamFileError(Exception):
    pass
class PeriodsInVcfError(Exception):
    pass

# Initial check to make sure the inputs are ok
def precheck_inputs(bam, vcf_file, igvuser, outpath, runtype):
    if not bam.endswith(".bam"):
        raise BadBamFileError(f"The bam file supplied does not look like a bam file: {bam}")
    logging.info(f"Bamfile: {bam} looks ok")
    vcf_reader = vcf.Reader(open(vcf_file, 'r'))
    for record in vcf_reader:
        if record.FILTER == None:
            logging.info(f"This vcf: {vcf_file} uses periods for pass values instead of PASS. We dont want that. trying to fix ...")
            vcf_file = fix_vcf(vcf_file, outpath)
            break
            #raise PeriodsInVcfError(f"This vcf: {vcf_file} uses periods for pass values instead of PASS. We don't want that.")
    logging.info(f"vcf-file: {vcf_file} looks ok")
    igvusers = os.listdir("/seqstore/webfolders/igv/users")
    valid_user = False
    if not igvuser == None:
        for userfiles in igvusers:
            if igvuser in userfiles:
                valid_user = True
        if valid_user == False:           
            raise IgvUserDoesNotExistError(f"The user '{igvuser}' does not seem to have an xml present on seqstore")
        logging.info(f"The igv user: {igvuser} seems ok")
    else:
        logging.info("No IGV user was given. Nothing will be exported.")
    if not os.path.isdir(outpath):
        logging.info(f"The output path you have supplied: {outpath} does not yet exist. It will be created by canvas during the run.")
    return vcf_file

# Fixes the vcf file if it is required
def fix_vcf(vcf_path, outpath):
    my_env = os.environ.copy()
    #bcftools = "/apps/bio/software/bcftools/1.9/bin/bcftools"
    vcftools = "/apps/bio/apps/vcftools/0.1.12a/bin/vcftools"
    destination = outpath + "/fixed_vcf"
    if not os.path.isdir(destination):
        os.makedirs(destination)
    working_vcf_1 = os.path.basename(vcf_path.rsplit(".", 1)[0])
    vcftools_args = [vcftools, "--vcf", vcf_path, "--remove-indels", "--recode", "--out", destination + "/" + working_vcf_1]
    final_vcf = destination + "/" + working_vcf_1 + ".recode.vcf"
    #final_vcf = working_vcf_1.rsplit(".", 1)[0] + "_fixed.vcf"
    #bcftools_args = f"{bcftools} filter -i 'FILTER=\"PASS\"' {destination + '/' +working_vcf_1 + '.recode.vcf'} >> {destination + '/' + final_vcf}"
    #logging.info(f"Arguments for bcftools: {bcftools_args}")
    subprocess.call(vcftools_args, shell=False, env=my_env)
    sed_args = ["sed", "-i", "s/\t\.\t\.\t/\tPASS\t\.\t/g", final_vcf]
    logging.info(f"running sed on {final_vcf} in order to replace periods with PASS")
    subprocess.call(sed_args, shell=False, env=my_env)
    #subprocess.call(bcftools_args, shell=True)
    return final_vcf


# Modifies the igv xml files to include the new segfiles 
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

# Main function that will run canvas
def main_canvas(bam, vcf, outpath, runtype):
    
    my_env = os.environ.copy()
    my_env["PATH"] = my_env["PATH"] + ":/opt/rh/rh-dotnet20/root/usr/bin"
    canvas_dll = "/apps/bio/software/canvas/1.38.0.1554/Canvas.dll"
    filter13 = "/medstore/External_References/Canvas_CLC_HG19_Dataset/custom/Homo_sapiens/UCSC/hg19/Sequence/WholeGenomeFasta/filter13.bed"
    reference = "/medstore/External_References/Canvas_CLC_HG19_Dataset/custom/Homo_sapiens/UCSC/hg19/Sequence/WholeGenomeFasta/kmer2.fa"
    genome_dir ="/medstore/External_References/Canvas_CLC_HG19_Dataset/custom/Homo_sapiens/UCSC/hg19/Sequence/WholeGenomeFasta/"
    sample_name = os.path.basename(vcf).rsplit(".", 1)[0]
    ploidy_file = determine_sex(vcf)

    if runtype.upper() == "TN" or runtype.upper() == "SOMATIC-WGS":
        run_type = "Somatic-WGS"
        logging.info(f"Canvas sample is being run as: {run_type}")
        args_TN = ["dotnet", canvas_dll, run_type, "-b", bam, "--sample-b-allele-vcf=" + vcf, "-o",
                   outpath, "--reference=" + reference, "-g", genome_dir, "-f", filter13, "--sample-name=" + sample_name,
                   "--ploidy-vcf=" + ploidy_file]
        subprocess.call(args_TN, shell=False, env=my_env)
        logging.info(f"Canvas has finished running on sample {sample_name}")

    elif runtype.upper() == "GERMLINE" or runtype.upper() == "SMALLPEDIGREE-WGS":
        run_type = "SmallPedigree-WGS"
        logging.info(f"Canvas sample is being run as: {run_type}")
        args_SP = ["dotnet", canvas_dll, run_type, "-b", bam, "--sample-b-allele-vcf=" + vcf, "-o",
                   outpath, "--reference=" + reference, "-g", genome_dir, "-f", filter13, "--sample-name=" + sample_name]
        subprocess.call(args_SP, shell=False, env=my_env)
        logging.info(f"Canvas has finished running on sample {sample_name}")


def create_seg(rundir, timestring):
   with open(f"{rundir}/CNV.CoverageAndVariantFrequency.txt", "r") as INFILE:
    with open(f"{rundir}/{timestring}_CNV_observed.seg", "w+") as OUTFILE:
        OUTFILE.write("#track graphType=points maxHeightPixels=300:300:300 color=0,0,0 altColor=0,0,0\n")
        OUTFILE.write("Sample\tChromosome\tStart\tEnd\tCNV_Observed\n")
        with open(f"{rundir}/{timestring}_CNV_called.seg", "w+") as OUTFILE2:
            OUTFILE2.write("#track graphType=points maxHeightPixels=300:300:300 color=0,0,220 altColor=220,0,0\n")
            OUTFILE2.write("Sample\tChromosome\tStart\tEnd\tCNV_Called\n")
            for line in INFILE:
                array_2 = line.split("\t")
                #print("array_2: ", array_2)
                length = len(array_2)
                cnv = 0
                ncov = 0

                try:
                    cnv = float(array_2[3])
                    ncov = float(array_2[6])
                    #print("cnv: ", cnv)
                    #print("ncov: ", ncov)
                except (IndexError, ValueError) as e:
                    #print("Exception: ", e)
                    continue

                if ncov > 0 and cnv > 0:
                    #print("PASSED")
                    cnvlog = math.log(cnv, 2)
                    covlog = math.log(ncov, 2)
                    if not array_2[0] == "X" or not array_2[0] == "Y":
                        cnvlog -= 1
                        covlog -= 1

                    OUTFILE.write("Observed_CNVs\t%s\t%s\t%s\t%s\n" % (array_2[0], array_2[1], array_2[2], covlog))
                    OUTFILE2.write("Called_CNVs\t%s\t%s\t%s\t%s\n" % (array_2[0], array_2[1], array_2[2], cnvlog)) 
    return [f"{rundir}/{timestring}_CNV_observed.seg", f"{rundir}/{timestring}_CNV_called.seg"]

# This will determine the sex of the sample by looking if there are more than 10 000 entries in the Y-chromosome in the normal vcf
# Needs to be improved. not optimal
def determine_sex(vcf_normal):
    vcf_reader = vcf.Reader(open(vcf_normal, 'r'))
    y_var_counter = 0
    for record in vcf_reader:
        if "Y" in record.CHROM:
            y_var_counter += 1
            # logging.info("The sex was determined to be MALE")
            # return "/apps/bio/software/canvas/male_hg19.vcf"
    if y_var_counter > 10000:
        logging.info(f"The sex was determined to be MALE due to {y_var_counter} variants found in the Y-chromosome")
        return "/apps/bio/software/canvas/male_hg19.vcf"
    logging.info(f"The sex was determined to be FEMALE due to {y_var_counter} variants found in the Y-chromosome")
    return "/apps/bio/software/canvas/female_hg19.vcf"


def igv_func(user, filelist):
    igv_data_folder = f"/seqstore/webfolders/igv/data/{user}"
    igv_xml_folder = f"/seqstore/webfolders/igv/users"
    for segfile in filelist:
        shutil.copy(segfile, igv_data_folder)
        igv_modification(user, igv_xml_folder + f"/{user}_igv.xml", segfile, "8008")
        igv_modification(user, igv_xml_folder + f"/{user}_igv_su.xml", segfile, "80")

# UNDER CONSTRUCTION probably not needed
#def determine_username(bam):
#    user_list = {"susanne.fransson": "WNB", "carola.oldfors": "GSU", "alvar.almstedt":}
#    for usernames in user_list.keys():
#        if "WBN" in user_list[usernames]:
#            return usernames

if __name__ == "__main__":

    #logging.basicConfig(stream=sys.stdout,
    #                    level=logging.INFO,
    #                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    timestring = datetime.datetime.now().strftime("%Y%m%d_%H_%M")

    parser = argparse.ArgumentParser()

    parser.add_argument("-b", "--bam", action="store", nargs="?", help="main bam file to be analysed")
    parser.add_argument("-n", "--normal_vcf", action='store', nargs="?", help="vcf for the normal sample")
    parser.add_argument("-u", "--user", action='store', nargs='?', help="user which will be used for igv on seqstore")
    parser.add_argument("-o", "--output", action="store", nargs="?", help="this is the main directory where the canvas output will end up")
    parser.add_argument("-t", "--runtype", action="store", nargs="?", help="this will be which typ of analysis you want to run, either germline or TN")
    args = parser.parse_args()
    
    bam_file = args.bam
    normal_vcf = args.normal_vcf
    igv_user = args.user
    output_path = args.output
    runtype = args.runtype
    
# UNDER CONSTRUCTION probably not needed
#    if igv_user.upper() == "AUTO" or igv_user == "" or not igv_user:
#        igv_user = determine_username(bam_file)

    #ports = [8008, 80]

    log_path = "/home/xalmal/logs"
    log_fname = f"canvas.{timestring}"
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler("{0}/{1}.log".format(log_path, log_fname)),
                        logging.StreamHandler()])

    
    logging.info(f"The input arguments were set to: runtype={runtype} bam={bam_file}, normal vcf={normal_vcf}, IGV user={igv_user}, output path={output_path}")

    normal_vcf = precheck_inputs(bam_file, normal_vcf, igv_user, output_path, runtype)
    main_canvas(bam_file, normal_vcf, output_path, runtype)
    
    if len(igv_user) > 1:
        igv_func(igv_user, create_seg(output_path, timestring))
    
    # segs = create_seg(output_path)
    #for segfile in segs:
    #    for port in ports:
    #        igv_modification()
