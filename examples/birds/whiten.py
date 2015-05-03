#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Whithens signal 
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
from numpy import vstack, save,load
from sklearn.decomposition import IncrementalPCA
import pickle

verbose = lambda *a: None

def fit(xmlname,dirmat):
    verbose('Openning ',xmlname)
    with open(xmlname) as xml_:
        birdinfo=BeautifulSoup(xml_.read())
    matname=birdinfo.filename.string[:-4]+".npy"
    matname=os.path.join(dirmat,matname)
    verbose('Fitting ',matname)
    feats=load(matname)
    IPCA.partial_fit(feats)
            
    
def fit_file(filename,matdir,outdir):
    verbose('Procesing file',filename)
    fit(filename,matdir)
    return None

def fit_file_(args):
    return fit_file(*args)


def transform(xmlname,dirmat):
    verbose('Openning ',xmlname)
    with open(xmlname) as xml_:
        birdinfo=BeautifulSoup(xml_.read())
    matname=birdinfo.filename.string[:-4]+".npy"
    matname=os.path.join(dirmat,matname)
    verbose('Openning ',matname)
    feats=load(matname)
    print(feats.shape)
    return IPCA.transform(feats)
            
    
def transform_file(filename,matdir,outdir):
    verbose('Transforming',filename)
    feats=transform(filename,matdir)
    name=os.path.basename(filename)
    name=os.path.splitext(name)[0]
    save(os.path.join(outdir,name),feats)
    return name

def transform_file_(args):
    return transform_file(*args)



# MAIN program
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Feature extaction from wav files")
    p.add_argument("XMLDIR",default=None,
            action="store", help="Directory with xml descriptions or xml")
    p.add_argument("MATDIR",default="mat",
            action="store", help="Directory with mat files")
    p.add_argument("OUTDIR",default="whiten",
            action="store", help="Output directory files")
    p.add_argument("--model",default="whiten",type=str,
            action="store", dest="model",
            help="Model to save the PCA transfrom [model.dat]")
    p.add_argument("-n",default=None,type=int,
            action="store", dest="total",
            help="Number of files to analyse [all]")
    p.add_argument("--components",default=40,type=int,
            action="store", dest="components",
            help="Number of components [40]")
    p.add_argument("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts = p.parse_args()

    # Managing configuration ----------------------------------------------
    # prepara función de verbose
    if opts.verbose:
        def verbose(*args,**kargs):
            print(*args,**kargs)

    # fit files into PCA  -------------------------------------------------
    if not os.path.isdir(opts.XMLDIR):
        idd=fit_file(opts.XMLDIR,opts.MATDIR,opts.OUTDIR)
        save(os.path.join(opts.OUTDIR,'ids'),[idd])
        sys.exit(0)

    IPCA = IncrementalPCA(n_components=opts.components,whiten=True)

    # Traverse xml files -------------------------------------------------
    for root, dirs, files in os.walk(opts.XMLDIR):
        args=[ (os.path.join(root,file),opts.MATDIR,opts.OUTDIR) 
                for file in files
                    if file.endswith('.xml')]
        if opts.total:
            args=args[:opts.total]

        idds=map(fit_file_,args)
        idds=map(transform_file_,args)

    # Savig withen model
    with open(os.path.join(opts.OUTDIR,opts.model),'wb') as idxf:
        pickle.dump(IPCA, idxf, pickle.HIGHEST_PROTOCOL)
            

