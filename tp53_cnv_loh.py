import os
import argparse
import sys

import pandas as pd
import multiprocessing
import logging


def find_vcf_files(resultdir, samplelist):
    """
    Recursively find the relevent vcf files ending with "SNV-pindel-filt.vcf" in a directory from that match a sample list
    Also save the filepaths to a cache file that will be read if the script is run again. return a list of filepaths
    """
    # check if the cache file exists
    if os.path.isfile('vcf_cache.txt'):
        # read the cached filepaths
        log_progress('Reading cached filepaths')
        with open('vcf_cache.txt', 'r') as f:
            vcf_files = [line.rstrip() for line in f]
    else:
        # find the vcf files
        vcf_files = []
        for root, dirs, files in os.walk(resultdir):
            for file in files:
                if file.endswith('SNV-pindel.vcf'):
                    vcf_files.append(os.path.join(root, file))
        # write the filepaths to a cache file
        with open('vcf_cache.txt', 'w') as f:
            for file in vcf_files:
                f.write(file + '\n')
    log_progress('Found {} vcf files'.format(len(vcf_files)))
    # log a few if the filepaths
    log_progress('First 5 vcf files: {}'.format(vcf_files[:5]))
    # read the sample list
    with open(samplelist, 'r') as f:
        samples = [line.rstrip() for line in f]
    # filter the vcf files to only those that match the sample list, not using list comprehension to make it easier to read
    filtered_vcf_files = []
    for vcf_file in vcf_files:
        for sample in samples:
            if sample in vcf_file:
                filtered_vcf_files.append(vcf_file)
                log_progress(f"Found {sample} in {vcf_file}")
            else:
                continue
                #log_progress(f"{sample} not in {vcf_file}")
    return filtered_vcf_files




def read_vcf(vcffile):
    """
    Read a vcf file into a pandas dataframe
    :param vcffile:
    :return:
    """
    vcf = pd.read_csv(vcffile, delim_whitespace=True, comment='#', header=None, names=['chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'info', 'format', 'sample'])
    return vcf


def read_snps(snp_list):
    """
    The snp list is a 2 column csv which contain chr and position
    :param snp_list:
    :return:
    """
    snps = pd.read_csv(snp_list, header=None, names=['chr', 'pos'])
    return snps


def get_af_from_vcf(vcf, snps):
    """
    Get AF from matching the vcf and snp datafreames and return a dataframe.
    Example vcf line:
    CHROM  POS ID  REF ALT QUAL    FILTER  INFO    FORMAT  166210244
    1   4849384 .  T C .   PopAF;ProtCode;Conseq
    AF=0.119;AS_FilterStatus=SITE;AS_SB_TABLE=63,77|9,9;CALLERS=mutect2,vardict,pisces,freebayes;DP=163;ECNT=2;GERMQ=93;
    MBQ=20,20;MFRL=124,128;MMQ=60,60;MPOS=33;POPAF=7.3;TLOD=59.84;CSQ=C|intergenic_variant|MODIFIER||||||||||||||
    |rs2235438||||SNV||||||||||||||||||||0.5901|0.8858|0.6138|0.129|0.6282|0.6094||||||||||0.8858|AFR||||||||
    GT:AD:AF:DP:F1R2:F2R1:PGT:PID:PS:SB_mutect2 0|1:140,18:0.119:158:73,10:65,8:0|1:4849384_T_C:4849384:63,77,9,9

    :param vcf: vcf dataframe
    :param snps: snp dataframe
    :return: list of dataframe with chr, pos, AF

    """
    snps_out = pd.DataFrame(columns=['sample', 'chr', 'pos', 'AF'])
    for vcf_file in vcf:
        vcf_df = read_vcf(vcf_file)
        iterator = 0
        # for each line in the snp list
        for index, row in snps.iterrows():
            # for each line or entry in the vcf
            for index2, row2 in vcf_df.iterrows():
                # skip immeatiately if its not chromosome 17
                if row2['chr'] != "17":
                    continue
                # if the chr and pos match
                if str(row['chr']) == str(row2['chr']):
                    #log_progress(f"Wohoo chromosome match {row['chr']} == {row2['chr']}")
                    if int(row['pos']) == int(row2['pos']):
                        log_progress(f"Yipee position match {row['pos']} == {row2['pos']}")
                        # get the AF from the info column
                        info = row2['info']
                        # split the info column on ';'
                        info_split = info.split(';')
                        # loop through the info_split list
                        for item in info_split:
                            # if the item contains 'AF=', append to the snps_out dataframe
                            if 'AF=' in item:
                                # if its POPAF, skip
                                if 'POPAF' in item:
                                    continue
                                log_progress(f"AF found {item}")
                                af = item.split('=')[1]
                                log_progress(f"AF = {af}")
                                # get vcf file basename
                                vcf_basename = os.path.basename(vcf_file)
                                log_progress(f"appending {vcf_basename}, {row['chr']}, {row['pos']}, {af} to snps_out dataframe")
                                snps_out = snps_out.append({'sample': vcf_basename, 'chr': row['chr'], 'pos': row['pos'], 'AF': af}, ignore_index=True)
                    else:
                        continue
                else:
                    continue
    log_progress(f'The start of the snps out variable {snps_out[5:]}')
    return snps_out



# run function
def runner(args):

    log_progress('Function vcf_files starting (which searches for vcf files on the system)')
    vcf_files = find_vcf_files(args.resultdir, args.sample_list)
    log_progress("Found {} matching vcf files".format(len(vcf_files)))

    log_progress('Reading snp list')
    snps = read_snps(args.snp_list)
    log_progress('Read {} snps'.format(len(snps)))

    # get the AF from the vcf files and snp list in parellel using mutliprocessing
    log_progress('Getting AF from vcf files')
    pool = multiprocessing.Pool(processes=8)
    results = [pool.apply_async(get_af_from_vcf, args=(vcf_files, snps)) for i in range(8)]

    log_progress('Getting AF from vcf files complete')

    # results is a list of AsyncResult objects but we need the actual results
    # Turn the results into a list of dataframes
    log_progress('Creating list of dataframes from results. Length of results: {}'.format(len(results)))

    dataframes = [result.get() for result in results]



    log_progress('List of dataframes created')

    # merge the results into a single dataframe
    log_progress('Merging dataframes')
    af_df = pd.concat(dataframes)




    log_progress('Merging results complete')

    # write out the af dataframe to a csv file
    log_progress('Writing AF to file')
    af_df.to_csv(args.output, index=False)
    log_progress('Writing AF to file complete')

    #if everything worked, delete the cache file
    if os.path.isfile('vcf_cache.txt') and not args.keep_cache:
        os.remove('vcf_cache.txt')


def log_progress(message):
    """
    Create info logger and log the message from function argument. Also return and print the message to the terminal.
    add timestamps to the log entries
    :param message: message to log
    :return: message
    """
    logging.basicConfig(filename='tp53_cnv_loh.log', level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info(message)
    print(message)
    return message



# main function
def main():
    parser = argparse.ArgumentParser(description='tp53_cnv_loh.py')

    # result dir path
    parser.add_argument('-r', '--resultdir', type=str, help='Path to the result directory', required=True)
    # sample list input
    parser.add_argument('-s', '--sample_list', type=str, required=True, help='sample list')
    # snp list input
    parser.add_argument('-p', '--snp_list', type=str, required=True, help='snp list')
    # output file for AF
    parser.add_argument('-o', '--output', type=str, required=True, help='output file')
    # keep the cache file
    parser.add_argument('-k', '--keep_cache', action='store_true', help='keep the cache file')
    args = parser.parse_args()

    runner(args)

if __name__ == '__main__':
    main()