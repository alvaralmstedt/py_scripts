#!/usr/bin/env python

import multiprocessing
import glob
import re
import os
from sys import argv


def sam_parse_worker(chunk):
    with open(chunk, "r") as sam:
        with open(chunk.replace(".txt", "_perfect.sam"), "w+") as perfect:
            with open(chunk.replace(".txt", "_secondary.sam"), "w+") as secondary:
                for line in sam:
                    old_line = line.split("\t")
                    if not line.startswith("@"):
                        NH_field = old_line[-2].split(":")[-1]
                        try:
                            if int(old_line[4]) <= 3 and int(NH_field) > 1 or bin(int(old_line[1]))[-2] == '0':
                                secondary.write(line)
                            else:
                                perfect.write(line)
                        except TypeError:
                            continue
                        except ValueError:
                            if bin(int(old_line[1]))[-2] == "b":
                                perfect.write(line)
                            continue
    os.remove(chunk)

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


def merger(in_path, resultname1, resultname2, chnkname1, chnkname2):
    with open(in_path + resultname1, "w") as evens:
        e = set(glob.glob("{}*{}".format(in_path, chnkname1)))
        for fname in sorted_nicely(e):
            with open(fname) as infile:
                for line in infile:
                    evens.write(line)
            os.remove(fname)
    with open(in_path + resultname2, "w") as odds:
        o = set(glob.glob("{}*{}".format(in_path, chnkname2)))
        for fname in sorted_nicely(o):
            with open(fname) as infile:
                for line in infile:
                    odds.write(line)
            os.remove(fname)
    # for i in (glob.glob(in_path + "chunk*")):
    #     os.remove(i)


def sorted_nicely(l):
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key=alphanum_key)


def sam_split_runner(sam_in, rundir, chunksize, threads):
    sam = chunks(sam_in, chunksize, rundir)
    pool = multiprocessing.Pool(processes=int(threads))
    pool.map(sam_parse_worker, sam)
    pool.close()
    pool.join()
    merger(rundir, "Perfect.sam", "Secondary.sam", "_perfect.sam", "_secondary.sam")


if __name__ == "__main__":
    input_file = str(argv[1])
    working_dir = str(argv[2])
    chunk_size = 100000
    chunk_size = int(argv[3])
    numb_threads = 4
    num_threads = int(argv[4])
    sam_split_runner(input_file, working_dir, chunk_size, num_threads)
