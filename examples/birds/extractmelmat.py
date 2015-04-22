#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Splits wavs into splits
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2013/IIMAS/UNAM
# ----------------------------------------------------------------------

#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Author ID main using a sparse representation
# ----------------------------------------------------------------------
# Ivan V. Meza
# 2014/IIMAS, México
# ----------------------------------------------------------------------
# authorid.py is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------------
from __future__ import print_function

# System libraries
import argparse
import sys
import os
from bs4 import BeautifulSoup
from multiprocessing import Pool
from numpy import vstack, save
from essentia.standard import *
import audiolab


# Local import
parent=os.path.abspath('../../')
sys.path.append(parent)
from sonidero.stats import StatsCalculator


w = Windowing(type = 'hann')
spectrum  = Spectrum()
melbands  = MelBands(numberBands=40,inputSize=513)
withening = SpectralWhitening()
peaks     = SpectralPeaks(maxFrequency=22100)
statcalculator = StatsCalculator()
statcalculator.set('all')

verbose = lambda *a: None

def extract_feats(xmlname,dirwave):
    verbose('Openning ',xmlname)
    with open(xmlname) as xml_:
        birdinfo=BeautifulSoup(xml_.read())
    wavname=os.path.join(dirwave,birdinfo.filename.string)
    verbose('Openning ',wavname)
    sound=audiolab.sndfile(wavname,'read')
    audio=sound.read_frames(sound.get_nframes())
    energies=[]
    for frame in FrameGenerator(essentia.array(audio), frameSize = 1024, hopSize = 210):
        fspectrum=spectrum(w(frame))
        fpeaksF,fpeaksM=peaks(fspectrum)
        withening(fspectrum,fpeaksF,fpeaksM)
        band=melbands(fspectrum)
        energies.append(band)
    if birdinfo.classid:
        idd=birdinfo.classid.string
    else:
        idd='u'
    return idd, vstack(energies)
            
    
def process_file(filename,wavdir,outdir):
    verbose('Extracting features from',filename)
    idd,feats=extract_feats(filename,wavdir)
    name=os.path.basename(filename)
    name=os.path.splitext(name)[0]
    save(os.path.join(outdir,name),feats)
    return (name,idd)

def process_file_(args):
    return process_file(*args)


# MAIN program
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Feature extaction from wav files")
    p.add_argument("XMLDIR",default=None,
            action="store", help="Directory with xml descriptions or xml")
    p.add_argument("WAVDIR",default="wav",
            action="store", help="Directory with wav files")
    p.add_argument("OUTDIR",default="wav",
            action="store", help="Output directory files")
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
    if not os.path.isdir(opts.XMLDIR):
        idd=process_file(opts.XMLDIR,opts.WAVDIR,opts.OUTDIR)
        save(os.path.join(opts.OUTDIR,'ids'),[idd])
        sys.exit(0)
        
    # Preparing processors -----------------------------------------------
    pool =  Pool(processes=opts.nprocessors)
    # Traverse xml files -------------------------------------------------
    for root, dirs, files in os.walk(opts.XMLDIR):
        args=[ (os.path.join(root,file),opts.WAVDIR,opts.OUTDIR) 
                for file in files
                    if file.endswith('.xml')]
        verbose('Processing',len(args),'files from',root)
        if opts.nprocessors > 1:
            idds=pool.map(process_file_,args)
        else:
            idds=map(process_file_,args)
    save(os.path.join(opts.OUTDIR,'ids'),idds)


            

