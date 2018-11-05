#!/usr/bin/env python

from IGV_mod_medstore import igv_modification
import os
import subprocess
import glob


# This function will compare which files are present in the seqstore igv data folder 
# with a medstore igv folder and make symlinks to the seqstore files in the medstore folder
def sync_links(med_dir, seq_dir):
    med_files = glob.glob(os.path.join(med_dir, '*'))
    seq_files = glob.glob(os.path.join(seq_dir, '*'))
    unsynced_bams = []
    for file in seq_files:
        if file not in med_files:
            os.chdir(med_dir)
            PIPE = subprocess.PIPE
            proc = subprocess.Popen(["ln", "-s", file], stdout=PIPE, stderr=PIPE)
            output, err = proc.communicate()
            print("stdout and ederr: ", output, err)
            err_code = proc.returncode
            print("Error code: ", err_code)
            if file.endswith(".bam"):
                unsynced_bams.append(file)
    return unsynced_bams

# This function calls a script in another file which modifies the users xml registry 
# file to detect the medstore synlinks as loadable igv files
def mod_registries(user, filelist):
    for each_file in filelist:
        igv_modification(user, each_file)

if __name__ == "__main__":
    from sys import argv

    user = argv[1]
    medstore = "/medstore/IGV_Folders/igv/data/{}".format(user)
    seqstore = "/seqstore/webfolders/igv/data/{}".format(user)

    mod_registries(user, sync_links(medstore, seqstore))
