#!/usr/bin/env python

import argparse


parser = argparse.ArgumentParser()

parser.add_argument("-b", "--bam_file", nargs="?", type=str, action='store', help='Full path to your bam input file')
parser.add_argument("-m", "--mode", nargs="?", type=str, help='Specify which mode canvas will run in')
parser.add_argument("-v", "--vcf_out", nargs="?", action='store', type=str, help='Specify the path where'
                                                                                 ' the vcf file will be sent')
parser.add_argument("-t", "--cnv_text", nargs="?", action='store', type=str, help='Specify the path where'
                                                                                  ' the CNV textfile file will be sent')
parser.add_argument("-o", "--cnv_obs", nargs="?", action='store', type=str, help='Specify the path where the'
                                                                                 ' CNV_observed.seg file will be sent')
parser.add_argument("-c", "--cnv_call", nargs="?", action='store', type=str, help='Specify the path where the'
                                                                                  ' CNV_called.seg file will be sent')
parser.add_argument("-u", "--uname", nargs="?", action='store', type=str, help='Default username taken from CLC')
parser.add_argument("-n", "--custom_uname", nargs="?", action='store', type=str, help='Selected IGV username.'
                                                                                      ' Overrides default')
parser.add_argument("-a", "--manifest", nargs="?", action='store', type=str, help='Specify the path to the exome'
                                                                                  ' manifest file')
parser.add_argument("-r", "--normal_bam", nargs="?", action='store', type=str, help='Full path to bam_normal input file')

args = parser.parse_args()

print args