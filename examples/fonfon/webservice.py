#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Flask web service for fonfon
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

from flask import Flask, request, render_template
from tempfile import NamedTemporaryFile
from os import remove
import codecs
import json
import yaml
import argparse

app = Flask('poswebservice')

corpora={}


@app.route('/')
def index():
    return render_template('index.html') 


@app.route('/up')
def up():
    return "Service up" 


@app.route('/list/contexts/<string:corpus>')
def list_contexts(corpus):
    maximum=max([x[2] for x in corpora[corpus]])
    return \
     render_template('list_contexts.html',contexts=corpora[corpus],corpusname=corpus,maximum=maximum,ignore=100) 


if __name__ == '__main__':
    p = argparse.ArgumentParser("Fonfon service")
    p.add_argument("CONF",
            action="store",
            help="Configuration file")
    p.add_argument("--host",default="127.0.0.1",
            action="store", dest="host",
            help="Root url [127.0.0.1]")
    p.add_argument("--port",default=5000,type=int,
            action="store", dest="port",
            help="Port url [500]")
    p.add_argument("--debug",default=False,
            action="store_true", dest="debug",
            help="Use debug deployment [Flase]")
    p.add_argument("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts = p.parse_args()

    with open(opts.CONF, 'r') as stream:
        conf=yaml.load(stream)

    for name in conf['corpora']:
        corpora[name]=[]
        for line in open(conf['corpora'][name]['contexts']):
            line=line.strip().split()
            if len(line)==4:
                corpora[name].append((line[0],line[1],int(line[2]),int(line[3])))
            

    app.run(debug=opts.debug,
            host=opts.host,
            port=opts.port)

