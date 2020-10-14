#!/usr/bin/env python3

import os
import multiprocessing
import argparse
from glob import glob
import shutil

# Gets full path to the fastq.gz or fq.gz files in the input directory
def get_infile_paths(infldr, recurse):    
    good_patterns = ['fastq.gz', 'fq.gz']
    if recurse:
        #my_dirs = os.listdir(infldr)
        my_files = list(absoluteFilePaths(infldr))
        #my_files = [os.listdir(f) for f in my_dirs]
        #my_files = [absoluteFilePaths(f) for f in my_dirs]
        #import pdb; pdb.set_trace()
    else:
        #my_files = os.listdir(infldr)
        #import pdb; pdb.set_trace()
        my_files = list(absoluteFilePaths(infldr))
    good_files = [f for f in my_files if any(sub in f for sub in good_patterns)]
    good_paths = [os.path.abspath(i) for i in good_files]    
    return good_paths


# Helper function til get abolute paths
def absoluteFilePaths(directory):
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           yield os.path.abspath(os.path.join(dirpath, f))


# Modifies the filepaths to what balsamic needs and appends to dict {newfilepath: [old, file, paths]}
def create_new_filenames(good_inlist):
    change_dict = {}
    changed = []
    for p in good_inlist:
        #good_indict[p.rsplit('/', 1)[1]] = p.rsplit('/', 1)[0]
        mypath = p.rsplit('/', 1)[0]
        old_samplename = p.rsplit('/', 1)[1]
        print(f"old_samplename = {old_samplename}")
        samponly = old_samplename.split('_S', 1)[0]
        print(f"samponly = {samponly}")
        rtype = old_samplename.rsplit('_001.fastq', 1)[0].rsplit('_', 1)[-1]
        print(f"rtype = {rtype}")
        newrtype = f"{rtype[0]}_{rtype[1]}"
        if (f"{mypath}/{samponly}_{newrtype}.fastq.gz") not in change_dict.keys():
            change_dict[(f"{mypath}/{samponly}_{newrtype}.fastq.gz")] = [p]
        else:
            change_dict[(f"{mypath}/{samponly}_{newrtype}.fastq.gz")].append(p)
    return change_dict


def merge(fq1, fq2):
    with open(fq1, 'ab+') as ofq1:
        with open(fq2, 'rb') as ofq2:
            print(f"shutil.copyfileobj({ofq2}, {ofq1})")
            shutil.copyfileobj(ofq2, ofq1)
            return os.path.abspath(fq1)


def merge_and_rename(chdict, rec=False, outfolder=os.getcwd()):
    #print(chdict)
    #merge
    completedfiles = []
    for i in chdict:
        s_infiles = sorted(chdict[i])
        print(f"s_infiles: {s_infiles}")
        if rec:
            #print(s_infiles, '\n')
            print(f"all files: {s_infiles}")
            pair1 = merge(s_infiles[0], s_infiles[1])
            print(f"pair1: {pair1}")
            #pair2 = merge(s_infiles[2], s_infiles[3])
            #print(f"pair2: {pair2}")
            #fullfile = merge(pair1, pair2)
            os.rename(pair1, i)
            print(f'{pair1} was renamed to {i}')
            #os.remove(s_infiles[0])
            os.remove(s_infiles[1])   
        elif len(s_infiles) == 2:
            pair = merge(s_infiles[0], s_infiles[1])
            rev = s_infiles[1]
            print(f"i: {i}")
            print(f"pair: {pair}")
            print(f"rev: {rev}")
            print("\n")
            os.rename(pair, i)
            os.remove(rev)
        else:
            continue
        completedfiles.append(i)
    return completedfiles


def remove_originals():
    pass


def test():
    """
    To recreate the recurse test folder:
    for file in $(ls /seqstore/instruments/novaseq_687_gc/Demultiplexdir/200924_A00687_0099_BHMW3JDRXX/TwistExom_prep1) ; do mkdir $file ;done
    for folder in /seqstore/instruments/novaseq_687_gc/Demultiplexdir/200924_A00687_0099_BHMW3JDRXX/TwistExom_prep1/* ; do for file in $(ls $folder) ; do touch $(basename $folder)/$file ; done ; done
    To recreate the 1samp test folder:
    for file in /seqstore/instruments/novaseq_687_gc/Demultiplexdir/200924_A00687_0099_BHMW3JDRXX/TwistExom_prep1/C10913/* ; do touch $(basename $file) ; done
    """
    infolder = "/home/xalmal/repos/py_scripts/test_files/balsamic_merge_test"
    rec = f"{infolder}/recurse"
    one_samp = f"{infolder}/1samp"
    #import pdb; pdb.set_trace()
    merge_and_rename(create_new_filenames(get_infile_paths(one_samp, False)))
    merge_and_rename(create_new_filenames(get_infile_paths(rec, True)), True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infolder", action="store", nargs="?", help="input folder containing fastqs to be renamed")
    parser.add_argument("-o", "--outfolder", action="store", nargs="?", help="output folder when renamed files go")
    parser.add_argument("-r", "--recursively", action="store_true", help="go recursively into subdirectories")
    parser.add_argument("-t", "--test", action="store_true", help="test the script")


    args = parser.parse_args()

    if args.test:
        test()
    else:
        merge_and_rename(create_new_filenames(get_infile_paths(args.infolder, args.recursively)))

if __name__ == "__main__":
    main()
