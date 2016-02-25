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
import numpy as np
import pickle
import random

from flask_wtf import Form
from wtforms import SelectField
from wtforms.validators import DataRequired

class CntSpkForm(Form):
    context = SelectField(u'Contexto',validators=[DataRequired()])
    dubitada = SelectField(u'Dubitada',validators=[DataRequired()])
    indubitada = SelectField(u'Indubitada',validators=[DataRequired()])


app = Flask('poswebservice')

corpora={}
info={}
info_test={}
gender={}
gender_={}
indices={}

minFs={
    'F0':0,
    'F1':150,
    'F2':900,
    'F3':1500,
    'F4':2500
    }
maxFs={
    'F0':350,
    'F1':850,
    'F2':3000,
    'F3':5000,
    'F4':5000,
    }

@app.route('/fonfon/')
def main():
    return render_template('index.html',info=indices) 


@app.route('/fonfon/up')
def up():
    return "Service up" 


@app.route('/fonfon/list/contexts/<string:index>')
def list_contexts(index):
    corpus=indices[index]['corpus']
    maximum=max([x[2] for x in corpora[index]])
    mets=info[corpus].keys()
    return \
     render_template('list_contexts.html',contexts=corpora[index],corpusname=corpus,maximum=maximum,ignore=100,mets=mets) 


@app.route('/fonfon/lr0/<string:index>/<string:met>', methods=('GET', 'POST'))
def lr0(index,met):
    form = CntSpkForm(csrf_enabled=False)
    corpus=indices[index]['corpus']
    form.context.choices=[("{0} {1}".format(x[0],x[1]),"{0} {1}".format(x[0],x[1])) for  x in corpora[index]]
    opts_gen=[]
    for gen,s in gender[corpus].iteritems():
        opts_gen+=[(ss,gen) for ss in s]
    opts_gen.sort()
    form.indubitada.choices=[("{0} {1}".format(s,gen[0]),"{0} ({1})".format(s,gen[0])) for s,gen in opts_gen]
    form.dubitada.choices=[("{0} {1}".format(s,gen[0]),"{0} ({1})".format(s,gen[0])) for s,gen in opts_gen]
    if form.validate_on_submit():
        sos_d,gen_d=form.dubitada.data.split()
        sos_i,gen_i=form.indubitada.data.split()
        cnt=form.context.data
        cnt=tuple(cnt.split())
        ref=[]
        minF=minFs[met]
        maxF=maxFs[met]
        total_spk=0
        for spk in gender[corpus][gen_i]:
            if not spk==sos_i and not spk==sos_d:
                try:
                    data_=info[corpus][met][spk][cnt]
                    ref.extend([m for m in data_ if m < maxF and m > minF ])
                    total_spk+=1
                except KeyError:
                    pass
            else:
                dub=info[corpus][met][sos_d][cnt]
                random.shuffle(dub)
                dub=dub[:len(dub)/2]
                indub=info[corpus][met][sos_i][cnt]
                random.shuffle(indub)
                indub=indub[len(indub)/2:]
                
        mu=np.mean(ref)
        tao=np.std(ref)                
        x=np.mean(dub)
        y=np.mean(indub)
        delta=np.std(dub+indub)
        z=(x+y)/2
        m=len(dub)
        n=len(indub)
        w=(x*m+y*n)/(m+n)
        a=np.sqrt(1.0/m+1.0/n)
        b=tao/(a*delta)
        sim=np.exp(-np.power(x-y,2)/(2*a*a*delta*delta))
        tip=np.exp(-(np.power(w-mu,2)/(2*tao*tao))+np.power(z-mu,2)/(tao*tao))
        lr0=b*sim*tip
        return render_template('result_lr0.html',gen_ind=gen_i,gen_dub=gen_d,ind=sos_i,dub=sos_d,cnt=cnt,mu=mu,tao=tao,x=x,y=y,delta=delta,z=z,w=w,m=m,n=n,a=a,b=b,sim=sim,tip=tip,lr0=lr0)

     
    return render_template('cntspk.html',form=form,index=index,met=met)




@app.route('/fonfon/get/<string:corpus>/<string:met>/<string:spk_gen>/<string:prev>/<string:curr>')
def detail_corpus(corpus,met,spk_gen,prev,curr):
    minF=minFs[met]
    maxF=maxFs[met]
    if spk_gen in gender[corpus].keys():
        gen=spk_gen
        data=[]
        total_spk=0
        for spk in gender[corpus][gen]:
            try:
                data_=info[corpus][met][spk][(prev,curr)]
                data.extend([m for m in data_ if m < maxF and m > minF ])
                total_spk+=1
            except KeyError:
                pass
        st=np.std(data)
        mu=np.mean(data)
        return \
                render_template('corpus_spk_cntx.html',corpusname=corpus,gender=gen,prev=prev,curr=curr,
                    mu=mu,st=st,data=data,total=len(data),met=met,nspk=total_spk,ignore=100) 
    else:
        spk=spk_gen
        data=info[corpus][met][spk][(prev,curr)]

        data=[m for m in data_ if m < maxF and m > minF ]

        st=np.std(data)
        mu=np.mean(data)
        return \
         render_template('corpus_spk_cntx.html',corpusname=corpus,
                spk=spk,prev=prev,curr=curr,mu=mu,st=st,gender=gender_[corpus][spk],data=data,total=len(data)) 

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
        gender[name]={}
        gender_[name]={}
        info[name]={}
        info_test[name]={}
        for line in open(conf['corpora'][name]['gender']):
            line=line.strip().split()
            try:
                gender[name][line[1]].append(line[0])
            except KeyError:
                gender[name][line[1]]=[line[0]]
            gender_[name][line[0]]=line[1]
        for met,data in conf['corpora'][name]['context_info'].iteritems():
            info[name][met]=pickle.load(open(data,'rb'))
        for met,data in conf['corpora'][name]['test_info'].iteritems():
            info_test[name][met]=pickle.load(open(data,'rb'))


    indices=conf['indices']
    for index in conf['indices']:
        corpora[index]=[]
        for line in open(conf['indices'][index]['contexts']):
            line=line.strip().split()
            if len(line)==4:
                corpora[index].append((line[0],line[1],int(line[2]),int(line[3])))



    app.run(debug=opts.debug,
            host=opts.host,
            port=opts.port)

