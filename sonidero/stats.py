#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Module for dealing with extraction the features and creating csv lines
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
""" 
.. module:: stats
    :platform: Unix
    :synopsis: Calculates basic statistics for matrix audio data

.. moduleauthor:: Ivan Meza-Ruiz <ivanvladimir@turing.iimas.unam.mx>

"""

import numpy as np
from scipy.stats import scoreatpercentile, skew, kurtosis

class StatsCalculator:
    def __init__(self,stats=['mean']):
        self.stats=['mean']
        #self._stats=['mean','std','median','q1','q2','q3','skew','kustosis','min','max']
        self._stats=['mean','std','median','skew']

    def set(self,option):
        if option=='all':
            self.stats=self._stats
        else:
            if self.option in self._stats:
                self.stats.append(option)
            
    
    def calculate(self,data,axis=0):
        values=[]
        for stat in self.stats:
            if stat.startswith('mean'):
                ndata=np.mean(data,axis=axis)
            elif stat.startswith('std'):
                ndata=np.std(data,axis=axis)
            elif stat.startswith('median'):
                ndata=np.median(data,axis=axis)
            elif stat.startswith('q1'):
                ndata=[scoreatpercentile(data[:,col],25)
                        for col in range(data.shape[1]) ]
            elif stat.startswith('q2'):
                ndata=[scoreatpercentile(data[:,col],50)
                        for col in range(data.shape[1]) ]
            elif stat.startswith('q3'):
                ndata=[scoreatpercentile(data[:,col],75)
                        for col in range(data.shape[1]) ]
            elif stat.startswith('skew'):
                ndata=[skew(data[:,col])
                        for col in range(data.shape[1]) ]
            elif stat.startswith('kurtosis'):
                ndata=[kurtosis(data[:,col])
                        for col in range(data.shape[1]) ]
            elif stat.startswith('max'):
                ndata=np.amax(data,axis=axis)
            elif stat.startswith('min'):
                ndata=np.amin(data,axis=axis)
            values.append(ndata)
        return np.hstack(values)
        


