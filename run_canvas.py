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

# Initial check to make sure the inputs are ok
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
        info.logging(f"The output path you have supplied: {outpath} does not yet exist. It will be created by canvas during the run.")

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
    filter13 = "medstore/External_References/Canvas_CLC_HG19_Dataset/custom/Homo_sapiens/UCSC/hg19/Sequence/WholeGenomeFasta/filter13.bed"
    reference = "/medstore/External_References/Canvas_CLC_HG19_Dataset/custom/Homo_sapiens/UCSC/hg19/Sequence/WholeGenomeFasta/kmer2.fa"
    genome_dir = "/medstore/External_References/Canvas_CLC_HG19_Dataset/custom/Homo_sapiens/UCSC/hg19/Sequence/WholeGenomeFasta/"
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


def create_seg(rundir):
   with open(f"{rundir}/CNV.CoverageAndVariantFrequency.txt", "r") as INFILE:
    with open(f"{rundir}/CNV_observed.seg", "w+") as OUTFILE:
        OUTFILE.write("#track graphType=points maxHeightPixels=300:300:300 color=0,220,0 altColor=220,0,0\n")
        OUTFILE.write("Sample\tChromosome\tStart\tEnd\tCNV_Observed\n")
        with open(f"{rundir}/CNV_called.seg", "w+") as OUTFILE2:
            OUTFILE2.write("#track graphType=points maxHeightPixels=300:300:300 color=0,220,0 altColor=220,0,0\n")
            OUTFILE2.write("Sample\tChromosome\tStart\tEnd\tCNV_Called\n")
            for line in INFILE:
                array_2 = line.split("\t")
                print("array_2: ", array_2)
                length = len(array_2)
                cnv = 0
                ncov = 0

                try:
                    cnv = float(array_2[3])
                    ncov = float(array_2[6])
                    print("cnv: ", cnv)
                    print("ncov: ", ncov)
                except (IndexError, ValueError) as e:
                    print("Exception: ", e)
                    continue

                if ncov > 0 and cnv > 0:
                    print("PASSED")
                    cnvlog = log(cnv, 2)
                    covlog = log(ncov, 2)
                    if not array_2[0] == "X" or not array_2[0] == "Y":
                        cnvlog -= 1
                        covlog -= 1

                    OUTFILE.write("Observed_CNVs\t%s\t%s\t%s\t%s\n" % (array_2[0], array_2[1], array_2[2], covlog))
                    OUTFILE2.write("Called_CNVs\t%s\t%s\t%s\t%s\n" % (array_2[0], array_2[1], array_2[2], cnvlog)) 
    return [f"{rundir}/CNV_observed.seg", f"{rundir}/CNV_called.seg"]

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
        logging.info("The sex was determined to be MALE due to {y_var_counter} variants found in the Y-chromosome")
        return "/apps/bio/software/canvas/male_hg19.vcf"
    logging.info("The sex was determined to be FEMALE due to {y_var_counter} variants found in the Y-chromosome")
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
    main_canvas(bam_file, normal_vcf, output_path, runtype)
    segs = create_seg(output_path)
    for segfile in segs:
        for port in ports:
            igv_modification()
