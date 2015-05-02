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

from sklearn.metrics import accuracy_score
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.metrics import precision_score, recall_score, confusion_matrix, classification_report, f1_score
from sklearn import preprocessing


verbose = lambda *a,**k: None

# MAIN program
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Develop")
    p.add_argument("FEATS",
            action="store", help="Feats file")
    p.add_argument("IDS",
            action="store", help="IDs file")
    p.add_argument("--estimators",
        action="store", dest="estimators",default=100,type=int,
        help="Define el valor para n_estimators")
    p.add_argument("--processors",default=1,type=int,
            action="store", dest="nprocessors",
            help="Number of processors [1]")
    p.add_argument("--max_depth",default=20,type=int,
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
            print(*args,**kargs)
    
    # Collecting features files ------------------------------------------
    first=True
    n=0
    verbose('Loading vectors')
    feats=np.load(opts.FEATS)
    ids_=np.load(opts.IDS)

    le = preprocessing.LabelEncoder()
    le.fit(ids_)
    verbose("Total classes",le.classes_.shape[0])
    ids=le.transform(ids_)

    from sklearn.utils import shuffle

    feats,ids=shuffle(feats,ids)

    X_train, X_test, y_train, y_test=\
        train_test_split(feats, ids, test_size=0.20,
        random_state=42) 
   
    verbose('Datos entrenamientp:',X_train.shape)
    verbose('Etiquetas:',y_train.shape)
    verbose('Datos prueva:',X_test.shape)

    verbose("Training")
    classifier=RandomForestClassifier(
            n_estimators=opts.estimators,
            n_jobs=opts.nprocessors,
            max_depth=opts.max_depth,
            verbose=True)

    # Aprendiendo
    classifier.fit(X_train, y_train)

    # Prediciendo
    verbose("Prediction")
    prediction = classifier.predict(X_test)

    print( 'Accuracy              :', accuracy_score(y_test, prediction))
    print( 'Precision             :', precision_score(y_test, prediction))
    print( 'Recall                :', recall_score(y_test, prediction))
    print( 'F-score               :', f1_score(y_test, prediction))
    print( '\nClasification report:\n', classification_report(y_test,
            prediction))
    cm=confusion_matrix(y_test, prediction)
    print( '\nConfussion matrix   :\n',cm)
    for x in cm:
        print(x)
