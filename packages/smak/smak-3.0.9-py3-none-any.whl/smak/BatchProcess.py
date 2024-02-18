#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 15:52:47 2023

@author: samwebb
"""
import fnmatch
import math
import os
import sys


import numpy as np



from AdvancedFilteringClass import advancedfilters
import globalfuncs
import MathWindowClass
from ThresholdingClass import thresholdfilters


def maskaszoom(fbl,**kw):
    [fbn,fb]=fbl
    if fb['zoom'][2]!=-1 and fb['zoom'][3]!=-1:
        fb['mask'].mask=np.zeros((fb['data'].data.shape[0],fb['data'].data.shape[1]),dtype=np.float32)
        fb['mask'].mask[fb['zoom'][1]:fb['zoom'][3],fb['zoom'][0]:fb['zoom'][2]]=np.ones(fb['data'].data.get(0)[fb['zoom'][1]:fb['zoom'][3],fb['zoom'][0]:fb['zoom'][2]].shape)

    else:
        fb['mask'].mask=np.ones((fb['data'].data.shape[0],fb['data'].data.shape[1]),dtype=np.float32)
 
def invertMask(fbl,**kw):
    [fbn,fb]=fbl
    if len(fb['mask'].mask)>0:
        md = np.where(fb['mask'].mask==0,1,0)
    else:
        md = np.ones((fb['data'].data.shape[0],fb['data'].data.shape[1]),dtype=np.float32)      

def addChanFromMask(fbl,**kw):
    [fbn,fb]=fbl 
    ps=kw['kw']
    if len(fb['mask'].mask)>0:
        md = fb['mask'].mask
    else:
        md = np.zeros((fb['data'].data.shape[0],fb['data'].data.shape[1]),dtype=np.float32)
        
    svtype='ROImask'
    i=1
    newname=svtype
    while newname in fb['data'].labels:
        newname=svtype+str(i)
        i+=1    
    ps['addchan'](md,newname,fbuffer=fbn)    
    
    
def addMaskToChan(fbl,**kw):
    [fbn,fb]=fbl
    ps=kw['kw']

    if len(fb['mask'].mask)==0:
        print('no mask in ',fbn)
        return
    
    datind=fb['data'].labels.index(ps['destchan'])+2
    data=fb['data'].data.get(datind)
    #find power of 2...
    factor=globalfuncs.powernext(int(max(np.ravel(data))))
    fb['data'].data.put(datind,data+fb['mask'].mask*float(factor))
    fb['data'].data.put(datind,data)  

def removeMaskFromChan(fbl,**kw):
    [fbn,fb]=fbl
    ps=kw['kw']   
    
    if len(fb['mask'].mask)==0:
        print('no mask in ',fbn)
        return
    
    datind=fb['data'].labels.index(ps['destchan'])+2
    data=fb['data'].data.get(datind)
    data=np.where(fb['mask'].mask>0,0,data)
    fbl['data'].data.put(datind,data)    
    
        
def filterGeneral(fbl,**kw):
    typd={'Mean':'-avg','Median':'-med','Min':'-min','Max':'-max','Invert':'-inv','Blur':'-blur','Unsharp':'-shrp','Denoise':'-den','Open':'-open','Close':'-close','Gradient':'-grad','TopHat':'-toph','BlackHat':'-blackh','FFT':'-fft','iFFT':'-ifft','Similarity':'-sim','SimBlur':'-sblr','MeanShift':'-ms','EDT':'-edt'}          
    [fbn,fb]=fbl
    ps=kw['kw']
    ppass={}
    for k in ps:
        if k in ['filter']: ppass[k]=ps[k]
        if k in ['size']: ppass[k]=int(ps[k])
        if k in ['sigma']: ppass[k]=float(ps[k])
    j=0
    if 'regex' in ps:
        oklabs = fnmatch.filter(fb['data'].labels,ps['regex'])
    else:
        oklabs = fb['data'].labels.copy()
    
    for chn in fb['data'].labels.copy():
        if chn in oklabs:
            newdata = advancedfilters(fb['data'].data.get(j+2),**ppass)
     
            svtype=typd[ps['filter']]
            i=1
            newname=chn+svtype
            while newname in fb['data'].labels:
                newname=chn+svtype+str(i)
                i+=1
            
            ps['addchan'](newdata,newname,fbuffer=fbn)
        j+=1

def threshGeneral(fbl,**kw):
    [fbn,fb]=fbl
    ps=kw['kw']
    ppass={}
    for k in ps:
        if k in ['filter']: ppass[k]=ps[k]
        if k in ['level','value']: ppass[k]=float(ps[k])
    j=0
    if 'regex' in ps:
        oklabs = fnmatch.filter(fb['data'].labels,ps['regex'])
    else:
        oklabs = fb['data'].labels.copy()
    
    for chn in fb['data'].labels.copy():
        if chn in oklabs:
            newdata = thresholdfilters(fb['data'].data.get(j+2),**ppass)
     
            svtype='-thresh'
            i=1
            newname=chn+svtype
            while newname in fb['data'].labels:
                newname=chn+svtype+str(i)
                i+=1
            
            ps['addchan'](newdata,newname,fbuffer=fbn)
        j+=1    
        
        
def mathSingleChan(fbl,**kw):
    [fbn,fb]=fbl
    ps=kw['kw']        
        
    j=0
    if 'regex' in ps:
        oklabs = fnmatch.filter(fb['data'].labels,ps['regex'])
    else:
        oklabs = fb['data'].labels.copy()
        
    if ps['oper'] in ['Horz Shift','Vert Shift']:
        ext = ps['scalar']
    else:
        ext = None
    
    for chn in fb['data'].labels.copy():
        if chn in oklabs:
            
            newdata=MathWindowClass.MathOp(ps['oper'], fb['data'].data.get(j+2), ext)
     
            svtype=ps['oper'].lower()
            i=1
            newname=chn+'-'+svtype
            while newname in fb['data'].labels:
                newname=chn+'-'+svtype+str(i)
                i+=1
            
            ps['addchan'](newdata,newname,fbuffer=fbn)
        j+=1        

def mathTwoChan(fbl,**kw):
    [fbn,fb]=fbl
    ps=kw['kw']        
        
    Aind=fb['data'].labels.index(ps['Adata'])+2
    Adata = fb['data'].data.get(Aind)
    if ps['Bdata'][0]=='&':  #denote for scalar
        Bdata = float(ps['Bdata'][1:])
        blab = 'scalar'
    else:
        Bind = fb['data'].labels.index(ps['Bdata'])+2
        Bdata = fb['data'].data.get(Bind)
        blab = ps['Bdata']
    option={}
    if ps['oper'] in ['Translate','Register','Transform','Align']:
        if fb['zoom'][0:4]!=[0,0,-1,-1]:  
            Adata = Adata[fb['zoom'][1]:fb['zoom'][3],fb['zoom'][0]:fb['zoom'][2]]
            Bdata = Bdata[fb['zoom'][1]:fb['zoom'][3],fb['zoom'][0]:fb['zoom'][2]]
            option['fullB']= fb['data'].data.get(Bind)
            
    newdata=MathWindowClass.MathOp(ps['oper'], Adata, Bdata, option)
     
    svtype=ps['Adata']+'.'+ps['oper'].lower()+'.'+blab
    i=1
    newname=svtype
    while newname in fb['data'].labels:
        newname=svtype+'-'+str(i)
        i+=1
            
    ps['addchan'](newdata,newname,fbuffer=fbn)











