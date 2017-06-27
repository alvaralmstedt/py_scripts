#!/usr/bin/env python

import multiprocessing
import glob
import re
import os


def worker(chunk):
    with open(chunk, "r") as inp:
        with open(chunk.replace(".txt", "_evens.txt"), "w") as evens:
            with open(chunk.replace(".txt", "_odds.txt"), "w") as odds:
                for line in inp:
                    line = line.strip()
                    if int(line) % 2 == 0:
                        evens.write(line + "\n")
                    else:
                        odds.write(line + "\n")


def chunks(filename, chnksize, r_dir):
    chunksize = chnksize
    fid = 1
    name_list = []
    with open(filename) as infile:
        chunkname = r_dir + 'chunk%d.txt' % fid
        f = open(chunkname, 'w')
        for i, line in enumerate(infile, 1):
            f.write(line)
            if not i % chunksize:
                f.close()
                name_list.append(chunkname)
                fid += 1
                chunkname = r_dir + 'chunk%d.txt' % fid
                f = open(chunkname, 'w')
        name_list.append(chunkname)
        f.close()
    return name_list


def merger(in_path):
    with open(in_path + "Evens.txt", "w") as evens:
        e = set(glob.glob("{}*_evens.txt".format(in_path)))
        for fname in sorted_nicely(e):
            with open(fname) as infile:
                for line in infile:
                    evens.write(line)
            os.remove(fname)
    with open(in_path + "Odds.txt", "w") as odds:
        o = set(glob.glob("{}*_odds.txt".format(in_path)))
        for fname in sorted_nicely(o):
            with open(fname) as infile:
                for line in infile:
                    odds.write(line)
            os.remove(fname)
    for i in (glob.glob(in_path + "chunk*")):
        os.remove(i)


def sorted_nicely(l):
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key=alphanum_key)


def runner(sam_in, rundir, chunksize, threads):
    sam = chunks(sam_in, chunksize, rundir)
    pool = multiprocessing.Pool(processes=int(threads))
    pool.map(worker, sam)
    merger(rundir)

if __name__ == "__main__":
    #chunks_out = chunks("/Users/alvaralmstedt/Dropbox/Python/testfiles/multiprocess/numberfile.txt", 1000)
    #print chunks_out
    #pool = multiprocessing.Pool(processes=4)
    #pool.map(worker, chunks_out)
    #merger("/Users/alvaralmstedt/Dropbox/Python/testfiles/multiprocess/")
    runner("/Users/alvaralmstedt/Dropbox/Python/testfiles/multiprocess/numberfile.txt",
           "/Users/alvaralmstedt/Dropbox/Python/testfiles/multiprocess/", 1000, 4)