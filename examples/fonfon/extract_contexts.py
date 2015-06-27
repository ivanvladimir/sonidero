#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Extracts phonetic/phonologic context from dimex100 corpus
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

# System libraries
import argparse
import sys
import os.path
from multiprocessing import Pool
from collections import Counter


# Local import
from dimex100.files import get_files, get_speaker

verbose = lambda *a: None

def load_labeling(filename,label):
    c=0
    aes=[]
    for line in open(filename):
        c+=1
        if c<3:
            continue
        line=line.strip().split()
        try:
            if line[2]==label:
                aes.append((float(line[0]),float(line[1])))
        except IndexError:
            pass
    return aes


labels=['a','e','i','o','u']
def process_file(filename):
    contexts=Counter()
    prev='ini'
    c=0
    si=get_speaker(filename)
    for line in open(filename):
        c+=1
        if c<3:
            continue
        line=line.strip().split()
        if len(line)==3:
            if line[2] in labels:
                contexts.update([(prev,line[2])])
            prev=line[2]
    return si,contexts
    


def process_file_(args):
    return process_file(*args)


# MAIN program
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Extract contexts")
    p.add_argument("CORPUS",default="corpus",
            action="store", help="Directory with corpus")
    p.add_argument("--label",default="a",type=str,
            action="store", dest="label",
            help="Label to extract statistics from [a]")
    p.add_argument("--processors",default=1,type=int,
            action="store", dest="nprocessors",
            help="Number of processors [1]")
    p.add_argument("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts = p.parse_args()

    # Managing configuration ----------------------------------------------
    # prepara función de verbose
    if opts.verbose:
        def verbose(*args,**kargs):
            print(*args,**kargs)

    files=[(x) for x in get_files(opts.CORPUS)]

    if opts.nprocessors > 1:
        pool =  Pool(processes=opts.nprocessors)
        cs=pool.map(process_file,files)
    else:
        cs=map(process_file,files)

    contexts=Counter()
    contextssi={}
    for si,c in cs:
        contexts.update(c)
        for c_ in c:
            try:
                contextssi[c_].update(si)
            except KeyError:
                contextssi[c_]=set(si)


    for ((p,v),c) in contexts.most_common():
        print("{0} {1} {2} {3}".format(p,v,c,len(contextssi[(p,v)])))


