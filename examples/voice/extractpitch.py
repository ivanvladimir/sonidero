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
import audiolab
from essentia.standard import *


# Local import
parent=os.path.abspath('../../')
sys.path.append(parent)

verbose = lambda *a: None

w = Windowing(type = 'hann')
spectrum  = Spectrum()
pitch = PitchYinFFT(frameSize=1024)

def extract_pitch(wavname):
    verbose('Openning ',wavname)
    sound=audiolab.sndfile(wavname,'read')
    audio=sound.read_frames(sound.get_nframes())
    ps=[]
    for frame in FrameGenerator(essentia.array(audio), frameSize = 1024, hopSize = 210):
        fspectrum=spectrum(w(frame))
        p,c=pitch(fspectrum)
        if c >= 0.1:
            ps.append(p)
        else:
            ps.append(0)
    return ps



def load_labeling(filename):
    c=0
    aes=[]
    for line in open(filename):
        c+=1
        if c<3:
            continue
        line=line.strip().split()
        if line[2]=='a':
            aes.append((float(line[0]),float(line[1])))
    return aes
    
def process_file(filename,labdir):
    fn=os.path.basename(filename)
    if not os.path.exists(os.path.join(labdir,fn[:-4]+".phn")):
        return (filename,[])
    verbose('Extracting pitch from',filename)
    ps=extract_pitch(filename)
    verbose('Extracting pitch aes',os.path.join(labdir,fn[:-4]+".phn"))
    aes=load_labeling(os.path.join(labdir,fn[:-4]+".phn"))
    p_aes=[]
    for ini,fin in aes:
        i_x=int(ini*210/1000)
        f_x=int(fin*210/1000)
        seg=ps[i_x:f_x]
        p_aes.append(seg[(len(seg)/2+1+1)])
    return (filename,p_aes)

def process_file_(args):
    return process_file(*args)


# MAIN program
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Feature extaction from wav files")
    p.add_argument("WAVDIR",default="wav",
            action="store", help="Directory with wav files")
    p.add_argument("LABDIR",default="lab",
            action="store", help="Directory with segmentation files")
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

    # Process if only one ------------------------------------------------
    if not os.path.isdir(opts.WAVDIR):
        idd=process_file(opts.WAVDIR,opts.LABDIR)
        sys.exit(0)
        
    # Preparing processors -----------------------------------------------
    pool =  Pool(processes=opts.nprocessors)
    # Traverse xml files -------------------------------------------------
    for root, dirs, files in os.walk(opts.WAVDIR):
        args=[ (os.path.join(root,file),opts.LABDIR) 
                for file in files
                    if file.endswith('.wav')]
        verbose('Processing',len(args),'files from',root)
        if opts.nprocessors > 1:
            idds=pool.map(process_file_,args)
        else:
            idds=map(process_file_,args)

    print(idds)

            

