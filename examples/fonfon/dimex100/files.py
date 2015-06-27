#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# File information
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

# System libraries
import argparse
import sys
import os.path
import re


def get_dirs(type="T22",set="all"):
    paths=[]
    if type=="T22":
        paths.append(['T22'])

    if set=="all":
        paths=[ [x for x in p1]+[p2] for p1 in paths for p2 in ['individuales','comunes']]
    elif set=="individuales":
        paths=[ [x for x in p1]+[p2] for p1 in paths for p2 in ['individuales']]
    elif set=="comunes":
        paths=[ [x for x in p1]+[p2] for p1 in paths for p2 in ['comunes']]

    
    return [os.path.join(*p) for p in paths]


def get_files(dir="corpus",type="T22",set="all",ext='phn'):
    files_=[]
    
    paths=get_dirs(type=type,set=set)
    # Traverse xml files -------------------------------------------------
    for root, dirs, files in os.walk(dir):
        f=False
        for p in paths:
            f=f or root.endswith(p)
        if f:
            files_.extend([os.path.join(root,file) 
                for file in files if file.endswith(ext)])
    return files_

re_speakerid=re.compile('/(s\d\d\d)/')
def get_speaker(filename):
    m=re_speakerid.search(filename)
    if m:
        return m.groups(0)
    else:
        return 'unknown'


    


            

