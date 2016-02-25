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
from utils import praatTextGrid

# Local import
from utils import contexts

verbose = lambda *a: None

def process_file(filename,cont):
    contexts_=Counter()
    if cont=="vocal-nasal":
        prev=('none','none')
    else:
        prev='none'
    candidate=('ini','ini')
    c=0
    si=get_speaker(filename)
    for line in open(filename):
        c+=1
        if c<3:
            continue
        line=line.strip().split()
        if len(line)==3:
            # Contexto vocal
            if cont=="vocal":
                if line[2] in contexts.vocals:
                    if prev in contexts.vocals:
                        candidate=(candidate[0],candidate[1]+'*')
                    if not candidate[0]=='ini':
                        contexts_.update([candidate])
                    candidate=(prev,line[2])
                prev=line[2]
            elif cont=="nasal":
                if line[2] in contexts.nasal:
                    if candidate[0]=='n':
                        contexts_.update([candidate])
                    candidate=(prev,line[2])
                prev=line[2]
            elif cont=="vocal-nasal":
                if line[2] in contexts.vocal_nasal:
                    if candidate[0]=='e-n':
                        contexts_.update([candidate])
                    candidate=("%s-%s"%prev,line[2])
                prev=(prev[1],line[2])
 
    if cont=='vocal':
        contexts_.update([candidate])
    return si,contexts_
    

def process_file_(args):
    return process_file(*args)

def process_file_textgrid_(args):
    return process_file_textgrid(*args)

def process_file_textgrid(filename,cont):
    contexts_=Counter()
    tg = praatTextGrid.PraatTextGrid(0,0)
    tg.readFromFile(filename)
    prev='none'
    for tier in tg.arrTiers:
        if tier.getName().lower() == 'fonema':
            for i in range(tier.getSize()):
                label=tier.getLabel(i)
                if len(label)==0:
                    label="_"
                contexts_.update([("None",label)])
                prev=label
    return filename,contexts_

# MAIN program
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Extract contexts")
    p.add_argument("CORPUS",default="corpus",
            action="store", help="Directory with corpus")
    p.add_argument("--type",default="dimex100",type=str,
            action="store", dest="type",
            help="Type of corpus (textgrid|dimex100) [dimex100]")
    p.add_argument("--label",default="a",type=str,
            action="store", dest="label",
            help="Label to extract statistics from [a]")
    p.add_argument("--processors",default=1,type=int,
            action="store", dest="nprocessors",
            help="Number of processors [1]")
    p.add_argument("--filter",default=None,type=str,
            action="store", dest="filter",
            help="File with files context to extract")
    p.add_argument("--context",default='vocal',type=str,
            action="store", dest="cont",
            help="Context to analyse [vocal|nasal]")
    p.add_argument("--set",default='individuales',type=str,
            action="store", dest="set",
            help="Set of recordings to analyse")
    p.add_argument("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts = p.parse_args()

    # Managing configuration ----------------------------------------------
    # prepara función de verbose
    if opts.verbose:
        def verbose(*args,**kargs):
            print(*args,**kargs)

    if opts.type=="dimex100":
        from dimex100.files import get_files, get_speaker
    else:
        from textgrid.files import get_files, get_speaker


    files=[(x,opts.cont) for x in get_files(opts.CORPUS,set=opts.set)]

    if opts.nprocessors > 1:
        pool =  Pool(processes=opts.nprocessors)
        if opts.type=="dimex100":
            cs=pool.map(process_file_,files)
        else:
            cs=pool.map(process_file_textgrid_,files)

    else:
        if opts.type=="dimex100":
            cs=map(process_file_,files)
        else:
            cs=map(process_file_textgrid_,files)


    if opts.filter:
        selected_filter=[]
        for line in open(opts.filter):
            line=line.strip().split()
            selected_filter.append((line[0],line[1]))


    contexts_=Counter()
    contextssi={}
    for si,c in cs:
        contexts_.update(c)
        for c_ in c:
            try:
                contextssi[c_].update([si])
            except KeyError:
                contextssi[c_]=set([si])


    for ((p,v),c) in contexts_.most_common():
        if opts.filter and (p,v) in selected_filter:
            print("{0} {1} {2} {3}".format(p,v,c,len(contextssi[(p,v)])))
        if not opts.filter:
            print("{0} {1} {2} {3}".format(p,v,c,len(contextssi[(p,v)])))


