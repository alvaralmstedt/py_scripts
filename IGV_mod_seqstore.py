#!/usr/bin/env python

import os


def igv_modification(user, infile):

    """
    Adds entries for seg files to user IGV xml list.
    """
    with open("/medstore/IGV_Folders/igv/users/%s_igv.xml" % user, "r+") as userfile:
        lines_of_file = userfile.readlines()
        bam = os.path.basename(infile)
        lines_of_file.insert(-2,
                             '\t\t<Resource name="%s" path="http://medstore.sahlgrenska.gu.se:8008/data/%s/%s" />\n' % (
                                 bam, user, bam))
        userfile.seek(0)
        userfile.truncate()
        userfile.writelines(lines_of_file)

    with open("/medstore/IGV_Folders/igv/users/%s_igv_su.xml" % user, "r+") as userfile:
        lines_of_file = userfile.readlines()
        bam = os.path.basename(infile)
        lines_of_file.insert(-2,
                             '\t\t<Resource name="%s" path="http://medstore.sahlgrenska.gu.se:80/data/%s/%s" />\n' % (
                                 bam, user, bam))
        userfile.seek(0)
        userfile.truncate()
        userfile.writelines(lines_of_file)


if __name__ == "__main__":
    from sys import argv

    user = argv[1]
    infile = argv[2]

    igv_modification(user, infile)
