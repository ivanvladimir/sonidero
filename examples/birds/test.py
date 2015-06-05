#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Splits wavs into splits
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2013/IIMAS/UNAM
# ----------------------------------------------------------------------

from __future__ import print_function

# System libraries
import argparse
import numpy as np
from sklearn.utils.extmath import fast_dot
import os.path

from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.metrics import precision_score, recall_score, confusion_matrix, classification_report, f1_score
from sklearn import preprocessing
import sys

verbose = lambda *a,**k: None

# MAIN program
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Develop")
    p.add_argument("FEATS",
            action="store", help="Feats file")
    p.add_argument("PROBS",
            action="store", help="Problems id file")
    p.add_argument("--model",default="model.data",type=str,
            action="store", dest="model",
            help="Maximum depth of random forest [model.dat]")
    p.add_argument("--processors",default=1,type=int,
            action="store", dest="nprocessors",
            help="Number of processors [1]")
    p.add_argument("--max_depth",default=None,type=int,
            action="store", dest="max_depth",
            help="Maximum depth of random forest [20]")
    p.add_argument("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts = p.parse_args()

    # Managing configuration ----------------------------------------------
    # prepara función de verbose
    if opts.verbose:
        def verbose(*args,**kargs):
            kargs['file']=sys.stderr
            print(*args,**kargs)
    
    # Collecting features files ------------------------------------------
    first=True
    n=0
    verbose('Loading vectors')
    feats=np.load(opts.FEATS)
    verbose('Loading problems')
    probs=np.load(opts.PROBS)


    verbose('Loading label encoder')
    le = joblib.load(os.path.join(opts.model,"le.idx"))
    verbose('Loading model')
    classifier= joblib.load(os.path.join(opts.model,"model"))

  
    X_test = feats

    # Prediciendo
    verbose("Prediction")
    prediction = classifier.predict_proba(X_test)

    for pid,row in zip(probs,prediction):
        pid=pid[2:]
        idxs=np.argsort(row)
        final=row[idxs[-5:]]
        label=le.inverse_transform(idxs[-5:])
        for e,(a,b) in enumerate(zip(label,final)):
            print(";".join([pid,a,str(5-e),str(b)]))



