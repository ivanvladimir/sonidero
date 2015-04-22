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
import os
import sys
from numpy import vstack, load, save


verbose = lambda *a,**k: None

# MAIN program
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Develop")
    p.add_argument("FEATSDIR",
            action="store", help="Directory with row feats")
    p.add_argument("OUTFILE",
            action="store", help="Output file")
    p.add_argument("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts = p.parse_args()

    # Managing configuration ----------------------------------------------
    # prepara función de verbose
    if opts.verbose:
        def verbose(*args,**kargs):
            print(*args,**kargs)
   
    # Loading ids
    ids=load(os.path.join(opts.FEATSDIR,'ids.npy'))
    ids_=dict(ids)
    ids=[]

    # Collecting features files ------------------------------------------
    first=True
    n=0
    verbose('Loading vectors')
    for root, dirs, files in os.walk(opts.FEATSDIR):

        files=[f for f in files if f.endswith('.npy') 
                                and not f.startswith('ids')]
        for filename in files:
            if n%300==0:
                verbose('.',end="")
            n+=1
            ids.append(ids_[os.path.basename(filename)[:-4]])
            row=load(os.path.join(root,filename))
            if first:
                data=row
                first=False
                continue
            data = vstack((data,row))
        verbose('')
    save(opts.OUTFILE+"_feats",data)
    save(opts.OUTFILE+"_ids",ids)
            
            

