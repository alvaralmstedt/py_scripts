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
                # it1 = 0
                # it2 = 0
                # it3 = 0
                # perfs = 0
                # secs = 0
                # truvalerrors = 0
                for line in sam:
                    old_line = line.split("\t")
                    # it3 += 1
#if len(old_line) != 13:
# logging.warning("Not 13 columns on line. Instead {} columns were found on line {}".format(str(len(old_line)),
#                                                                                                    str(it3)))
# new_line = old_line
                    if not line.startswith("@"):
                        NH_field = old_line[-2].split(":")[-1]
                        try:
                            if int(old_line[4]) <= 3 and int(NH_field) > 1 or bin(int(old_line[1]))[-2] == '0':
                                secondary.write(line)
                                # secs += 1
                                # new_line[1] = str(int(old_line[4]) + 256)

                            else:
                                perfect.write(line)
                                # perfs += 1
                        except TypeError:
                            # it1 += 1
                            # logging.warning("type error number {}".format(str(it1)))
                            # print("column 4: ", old_line[4])
                            # print("NH_field: ", NH_field)
                            # print("Column 1: ", old_line[1])
                            # print(str(te))
                            continue
                        except ValueError:
                            # it2 += 1
                            # logging.warning("value error number {}".format(str(it2)))
                            # print(str(ve))
                            if bin(int(old_line[1]))[-2] == "b":
                                # logging.info("This read has flag 0 (mapped, unpaired). Sending it to perfect.")
                                perfect.write(line)
                                # perfs += 1
                            # else:
                                # truvalerrors += 1
                            continue
                # logging.info("{} perfect. {} secondary. {} TypeErrors. {} ValueErrors of which {} are real errors".format(perfs, secs, it1, it2, truvalerrors))


    # with open(chunk, "r") as inp:
    #     with open(chunk.replace(".txt", "_evens.txt"), "w") as evens:
    #         with open(chunk.replace(".txt", "_odds.txt"), "w") as odds:
    #             for line in inp:
    #                 line = line.strip()
    #                 if int(line) % 2 == 0:
    #                     evens.write(line + "\n")
    #                 else:
    #                     odds.write(line + "\n")


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
    for i in (glob.glob(in_path + "chunk*")):
        os.remove(i)


def sorted_nicely(l):
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key=alphanum_key)


def sam_split_runner(sam_in, rundir, chunksize, threads):
    sam = chunks(sam_in, chunksize, rundir)
    pool = multiprocessing.Pool(processes=int(threads))
    pool.map(sam_parse_worker, sam)
    merger(rundir, "Perfect.sam", "Secondary.sam", "_perfect.sam", "_secondary.sam")
    pool.close()
    pool.join()

if __name__ == "__main__":
    # chunks_out = chunks("/Users/alvaralmstedt/Dropbox/Python/testfiles/multiprocess/numberfile.txt", 1000)
    # print chunks_out
    # pool = multiprocessing.Pool(processes=4)
    # pool.map(worker, chunks_out)
    # merger("/Users/alvaralmstedt/Dropbox/Python/testfiles/multiprocess/")
    input_file = str(argv[1])
    working_dir = str(argv[2])
    chunk_size = 100000
    chunk_size = int(argv[3])
    numb_threads = 4
    num_threads = int(argv[4])
    sam_split_runner(input_file, working_dir, chunk_size, num_threads)
