#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# data2h5py saves the audiodata into an hdf5 container
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------

from __future__ import print_function

# System libraries
import argparse
import os
from bs4 import BeautifulSoup
import numpy as np
from multiprocessing import Pool
import scikits.audiolab as audiolab
import h5py
from collections import Counter

# Verbose definition
verbose = lambda *a: None

def extract_info(xmlname):
    #verbose('Openning ',xmlname)
    with open(xmlname) as xml_:
        birdinfo=BeautifulSoup(xml_.read())
    wavname=birdinfo.filename.string
    if birdinfo.classid:
        idd=birdinfo.classid.string
    else:
        idd='u'
    return idd, wavname
            
    
def get_info(filename):
    #verbose('Extracting info from',filename)
    idd,wavefile=extract_info(filename)
    return idd,wavefile

def get_info_(args):
    return get_info(*args)


# MAIN program
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Feature extaction from wav files")
    p.add_argument("XMLDIR",default=None,
            action="store", help="Directory with xml descriptions or xml")
    p.add_argument("WAVDIR",default="wav",
            action="store", help="Directory with wav files")
    p.add_argument("OUTDIR",default="feats",
            action="store", help="Output directory files")
    p.add_argument("--h5_file",default="spectrum.hdf5",type=str,
            action="store", dest="hdf5",
            help="Name of hdf5 file [spectrum.hdf5]")
    p.add_argument("--framesize",default=1024,type=int,
            action="store", dest="framesize",
            help="Framesize to analyse [1024]")
    p.add_argument("--hopsize",default=420,type=int,
            action="store", dest="hopsize",
            help="Frames to hop in spectrum analysis [210]")
    p.add_argument("-n",default=None,type=int,
            action="store", dest="total",
            help="Number of files to analyse [all]")
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

    # Setting variables for extraction
    framesize=opts.framesize
    hopsize=opts.hopsize
    freqbins=framesize/2+1
    window = np.hanning(framesize)

    # Creating the hdf5 file ---------------------------------------------
    h5_file = h5py.File(os.path.join(opts.OUTDIR,opts.hdf5), "w")


    # Traverse xml files -------------------------------------------------
    for root, dirs, files in os.walk(opts.XMLDIR):
        if root==opts.XMLDIR:
            continue
        args=[ (os.path.join(root,file),) 
                for file in files
                    if file.endswith('.xml')]

        if opts.total:
            args=args[:opts.total]

        if opts.nprocessors > 1:
            pool =  Pool(processes=opts.nprocessors)
            idds=pool.map(get_info_,args)
        else:
            idds=map(get_info_,args)
       
        idmap=Counter([x for x,y in idds]).keys()
        verbose('Recovered',len(idmap),'labels')
        nlabels=999
        verbose('Processing',len(args),'files from',root)
        
        label = os.path.basename(root)
        verbose('Creating',label,'group')
        gr=h5_file.create_group(label)
        for ix,label in enumerate(idmap):
            gr.attrs[label]=ix
        dX=gr.create_dataset("X",(freqbins,0),dtype="float32",maxshape=(freqbins,None))
        
        dY=gr.create_dataset("Y",(nlabels,0),dtype="int32",maxshape=(nlabels,None))

        ix=0
        for label,wavfile in idds:
            wavname=os.path.join(opts.WAVDIR,wavfile)
            verbose('Openning ',wavname)
            sound=audiolab.sndfile(wavname,'read')
            audio=sound.read_frames(sound.get_nframes())
            # Mono in case sterio
            if len(audio.shape) != 1: 
                audio = np.sum(audio, axis=1)/2
          
            # Saving X 
            # Info from size of file 
            nframes  = (len(audio)-framesize)//hopsize
            if nframes < 44:
                continue
            windoed  = np.zeros((nframes, framesize))
            ix=dX.shape
            # Resizing data
            dX.resize((freqbins,ix[1]+nframes))
            dY.resize((nlabels,ix[1]+nframes))

            # Extract windows
            for i in xrange(nframes):
                sup = i*hopsize + np.arange(framesize)
                windoed[i,:] = audio[sup] * window
            
            # Extract espectrum
            fft = np.fft.rfft(windoed)
            fft=(np.abs(fft)**2).T
            dX[:,ix[1]:ix[1]+nframes]=fft

            # Saving Y
            vlabel = np.zeros((nlabels,nframes))
            target=idmap.index(label)
            if(label!='u'):
                vlabel[target,:] = 1
            dY[ix[1]:ix[1]+nframes]=vlabel

    h5_file.close()

            
            
            

