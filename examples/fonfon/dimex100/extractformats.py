#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Extracts pitch
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
import praatUtil 
import numpy as np


# Local import
parent=os.path.abspath('../../')
sys.path.append(parent)

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
    
def process_file(filename,labdir,label):
    fn=os.path.basename(filename)
    if not os.path.exists(os.path.join(labdir,fn[:-4]+".phn")):
        return (filename,[])
    verbose('Extracting formatns from',filename)
    ps=praatUtil.calculateFormants(filename)[0]
    verbose('Extracting pitch aes',os.path.join(labdir,fn[:-4]+".phn"))
    aes=load_labeling(os.path.join(labdir,fn[:-4]+".phn"),label)
    if len(aes)==0:
        return (filename,[])
    seg=0
    ini=aes[seg][0]/1000
    fin=aes[seg][1]/1000
    state=0
    formants=[]
    for i in range(ps.getNumFrames()):
        time,fs=ps.get(i)
        if state==0 and time>ini:
            state=1
            formants.append(fs)
        if state==1 and time<fin:
            formants.append(fs)
        elif state==1 and time>fin:
            state=0
            seg+=1
            if seg>=len(aes):
                break
            ini=aes[seg][0]/1000
            fin=aes[seg][1]/1000

    return (filename,formants)

def process_file_(args):
    return process_file(*args)


# MAIN program
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Feature extaction from wav files")
    p.add_argument("WAVDIR",default="wav",
            action="store", help="Directory with wav files")
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

    opts.LABDIR=opts.WAVDIR+"/T22/individuales/"
    opts.WAVDIR=opts.WAVDIR+"/audio_editado/individuales/"

    # Process if only one ------------------------------------------------
    if not os.path.isdir(opts.WAVDIR):
        idd=process_file(opts.WAVDIR,opts.LABDIR,opts.label)
        sys.exit(0)
        
    # Preparing processors -----------------------------------------------
    pool =  Pool(processes=opts.nprocessors)
    # Traverse xml files -------------------------------------------------
    for root, dirs, files in os.walk(opts.WAVDIR):
        args=[ (os.path.join(root,file),opts.LABDIR,opts.label) 
                for file in files
                    if file.endswith('.wav')]
        verbose('Processing',len(args),'files from',root)
        if opts.nprocessors > 1:
            idds=pool.map(process_file_,args)
        else:
            idds=map(process_file_,args)

    f1,f2,f3,f4=[],[],[],[]
    for filename, formants in idds:
        f1.extend([f[0].get('frequency',0)  for f in formants if len(f)>3])
        f2.extend([f[1].get('frequency',0)  for f in formants if len(f)>3])
        f3.extend([f[2].get('frequency',0)  for f in formants if len(f)>3])
        f4.extend([f[3].get('frequency',0)  for f in formants if len(f)>3])
    print(opts.WAVDIR)
    print("F1",np.mean(f1))
    print("F2",np.mean(f2))
    print("F3",np.mean(f3))
    print("F4",np.mean(f4))

            

