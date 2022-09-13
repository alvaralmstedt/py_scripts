#!/usr/bin/env python3

import os
import argparse
import multiprocessing

def read_csv(infile):
    with open(infile, "r") as my_in:
        lines = [line.rstrip('\n').lstrip() for line in my_in]
    return lines


def find_paths_seqstore(infile, rot):
    targetfilename = "report.pdf"
    filenamelist = read_csv(infile)
    pathdict = {}
    reallist = os.listdir(rot)
    for each_file in filenamelist:
        print(f" csv: {each_file} rot: {rot}")
        match = "notadir"
        for r in reallist:
            if each_file in r:
                match = r
                break
        if os.path.isdir(f"{rot}/{match}"):
            for root, dirs, files in os.walk(rot):
                if each_file in dirs and "report.pdf" in files:
                    pathdict[f"{each_file}"] = f"{root}{dirs}{files}"
        else:
            print(f"No matches for {each_file}")
    return pathdict


def copy_targets(infile, outdir, root):
    my_paths = find_paths_seqstore(infile, root)
    for keys, items in my_paths:
        #create outpath directory here
        print(f"Copying file from run: '{keys}' from path '{items}' to outpath: {outdir}/{keys}")


def get_tarballs_from_hcp(infile):
    from HCP import HCPManager
    filenamelist = read_csv(infile)



def main():
    parser = argparse.ArgumentParser(prog="1kk.py", description="Get s5 vcfs")
    parser.add_argument("-r", "--root", nargs="?", type=str, action='store', help="Root path to look in")
    parser.add_argument("-l", "--list", nargs="?", type=str, action='store', help="File containing list of runnames")
    parser.add_argument("-o", "--output", nargs="?", type=str, action='store', help="Target folder for outputs. FULL PATH")

    args = parser.parse_args()

    copy_targets(args.list, args.output, args.root)


if __name__ == "__main__":
    main()