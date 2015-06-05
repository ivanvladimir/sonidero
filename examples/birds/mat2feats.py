#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Collapses matrices into vects
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2013/IIMAS/UNAM
# ----------------------------------------------------------------------

from __future__ import print_function

# System libraries
import argparse
import sys
import os
from bs4 import BeautifulSoup
from multiprocessing import Pool
from numpy import load, save


# Local import
parent=os.path.abspath('../../')
sys.path.append(parent)
from sonidero.stats import StatsCalculator

statcalculator = StatsCalculator()
statcalculator.set('all')

verbose = lambda *a: None

def extract_feats(xmlname,dirmat):
    verbose('Openning ',xmlname)
    with open(xmlname) as xml_:
        birdinfo=BeautifulSoup(xml_.read())
    matname=os.path.join(dirmat,birdinfo.filename.string[:-4]+".npy")
    if os.path.exists(matname):
        verbose('Openning ',matname)
        mat=load(matname)
    else:
        mat=None
    if birdinfo.classid:
        idd=birdinfo.classid.string
    else:
        idd='u'
    return idd, mat
                
    
def process_file(filename,matdir,outdir):
    verbose('Extracting features from',filename)
    idd,feats=extract_feats(filename,matdir)
    if not feats is None:
        verbose('Identifier species',idd)
        stats=statcalculator.calculate(feats)
        name=os.path.basename(filename)
        name=os.path.splitext(name)[0]
        save(os.path.join(outdir,name),stats)
        return (name,idd)
    else:
        return None

def process_file_(args):
    return process_file(*args)


# MAIN program
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Feature extaction from wav files")
    p.add_argument("XMLDIR",default=None,
            action="store", help="Directory with xml descriptions or xml")
    p.add_argument("MATDIR",default="wav",
            action="store", help="Directory with mat files")
    p.add_argument("OUTDIR",default="wav",
            action="store", help="Output directory files")
    p.add_argument("--processors",default=1,type=int,
            action="store", dest="nprocessors",
            help="Number of processors [1]")
    p.add_argument("-n",default=None,type=int,
            action="store", dest="total",
            help="Number of files to analyse [all]")
 
    p.add_argument("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts = p.parse_args()

    # Managing configuration ----------------------------------------------
    # prepara función de verbose
    if opts.verbose:
        def verbose(*args,**kargs):
            print(*args,**kargs)

    # Process if only one ------------------------------------------------
    if not os.path.isdir(opts.XMLDIR):
        idd=process_file(opts.XMLDIR,opts.MATDIR,opts.OUTDIR)
        save(os.path.join(opts.OUTDIR,'ids'),[idd])
        sys.exit(0)
        
    # Preparing processors -----------------------------------------------
    pool =  Pool(processes=opts.nprocessors)
    # Traverse xml files -------------------------------------------------
    for root, dirs, files in os.walk(opts.XMLDIR):
        args=[ (os.path.join(root,file),opts.MATDIR,opts.OUTDIR) 
                for file in files
                    if file.endswith('.xml')]
        if opts.total:
            args=args[:opts.total]

        verbose('Processing',len(args),'files from',root)
        if opts.nprocessors > 1:
            idds=pool.map(process_file_,args)
        else:
            idds=map(process_file_,args)
    save(os.path.join(opts.OUTDIR,'ids'),[x for x in idds if x])


            

