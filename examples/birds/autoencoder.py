#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# denoising autoencoder
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------

from __future__ import print_function

# System libraries
import argparse
import theano.tensor as T
from pylearn2.costs.cost import Cost, DefaultDataSpecsMixin
import numpy
from pylearn2.models.model import Model
from pylearn2.space import VectorSpace
from pylearn2.utils import sharedX
from pylearn2.config import yaml_parse


# Verbose definition
verbose = lambda *a: None

class Autoencoder(Model):
    def __init__(self, nvis, nhid):
        super(Autoencoder, self).__init__()

        self.nvis = nvis
        self.nhid = nhid

        W_value = numpy.random.uniform(size=(self.nvis, self.nhid))
        self.W = sharedX(W_value, 'W')
        b_value = numpy.zeros(self.nhid)
        self.b = sharedX(b_value, 'b')
        c_value = numpy.zeros(self.nvis)
        self.c = sharedX(c_value, 'c')
        self._params = [self.W, self.b, self.c]

        self.input_space = VectorSpace(dim=self.nvis)

    def reconstruct(self, X):
        h = T.tanh(T.dot(X, self.W) + self.b)
        return T.nnet.sigmoid(T.dot(h, self.W.T) + self.c)


class AutoencoderCost(DefaultDataSpecsMixin, Cost):
    supervised = False

    def expr(self, model, data, **kwargs):
        space, source = self.get_data_specs(model)
        space.validate(data)
        
        X = data
        X_hat = model.reconstruct(X)
        loss = -(X * T.log(X_hat) + (1 - X) * T.log(1 - X_hat)).sum(axis=1)
        return loss.mean()



# MAIN program
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Feature extaction from wav files")
    p.add_argument("MODELYAML",default=None,
            action="store", help="Autoencoder model description in YAML")
    p.add_argument("H5DATA",default=None,
            action="store", help="hdf5 file with the data")
    p.add_argument("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts = p.parse_args()

    # Managing configuration ----------------------------------------------
    # prepara función de verbose
    if opts.verbose:
        def verbose(*args,**kargs):
            print(*args,**kargs)
    with open(opts.MODELYAML) as f:
        model_yaml=f.read()
        model_yaml=model_yaml%{'filename':opts.H5DATA}

    trainer = yaml_parse.load(model_yaml)
    trainer.main_loop()  
