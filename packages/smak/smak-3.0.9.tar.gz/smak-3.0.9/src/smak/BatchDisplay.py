#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 15:42:14 2023

@author: samwebb
"""
import shutil
import math
import sys
import os
import fnmatch

import numpy as np


import globalfuncs


def edgezoom(fbl,**kw):
    [fbn,fb]=fbl
    if fb['zoom'][0:4]==[0,0,-1,-1]:
        globalfuncs.setList(fb['zoom'],[1,1,fb['data'].data.get(0).shape[1]-2,fb['data'].data.get(0).shape[0]-2,0,0])
    else:
        globalfuncs.setList(fb['zoom'],[fb['zoom'][0]+1,fb['zoom'][1]+1,fb['zoom'][2]-1,fb['zoom'][3]-1,0,0])
    #globalfuncs.setList(self.zmxyc,[0,0,0,0])

def saveDisplay(fbl,**kw):
    [fbn,fb]=fbl
    ps=kw['kw']    
        
    j=0
    if 'regex' in ps:
        oklabs = fnmatch.filter(fb['data'].labels,ps['regex'])
    else:
        oklabs = fb['data'].labels.copy()
    
    for chn in fb['data'].labels.copy():
        if chn in oklabs:
            #display image
            #
            #save
            fn=fb['fname'] + '_MD_' + chn + '.jpg'
            ps['display'].savejpgimage(fn)
        j+=1       
    
def saveTiffDisplay(fbl,**kw):
    [fbn,fb]=fbl
    ps=kw['kw']    
        
    j=0
    if 'regex' in ps:
        oklabs = fnmatch.filter(fb['data'].labels,ps['regex'])
    else:
        oklabs = fb['data'].labels.copy()
    
    for chn in fb['data'].labels.copy():
        if chn in oklabs:
            #display image
            #
            #save
            fn=fb['fname'] + '_MD_' + chn + '.tiff'
            ps['display'].saveHDimage(fn)
        j+=1    
    
def saveProcessed(fbl,**kw):
    [fbn,fb]=fbl
    fn = fb['fname']+'_process.dat'

    if fb['data'].hasHDF5:
        fb['data'].hdf5group.attrs.create("channels",fb['data'].channels)
        fb['data'].hdf5group.attrs.create("labels",fb['data'].labels)
        fb['data'].hdf5.flush()
        hdffn=os.path.splitext(fn)[0]+".hdf5"
        shutil.copy(fb['data'].hdf5.filename,hdffn)
        print("hdf5 saved")
    
    fb['changes']=0
    
def setMaxDisplay(fbl,**kw):
    [fbn,fb]=fbl
    ps=kw['kw']   
    
    if 'regex' in ps:
        oklabs = fnmatch.filter(fb['data'].labels,ps['regex'])
    else:
        oklabs = fb['data'].labels.copy()

    for l in oklabs:
        ps['display'].scalemaxlist[l]=float(ps['value'])
    

def defaultMaxDisplay(fbl,**kw):
    [fbn,fb]=fbl
    ps=kw['kw']   
    
    if 'regex' in ps:
        oklabs = fnmatch.filter(fb['data'].labels,ps['regex'])
    else:
        oklabs = fb['data'].labels.copy()

    for l in oklabs:
        if l in ps['display'].scalemaxlist: 
            del ps['display'].scalemaxlist[l]

def balanceMaxDisplay(fbl,**kw):
    [fbn,fb]=fbl
    ps=kw['kw']       
    
    if 'regex' in ps:
        oklabs = fnmatch.filter(fb['data'].labels,ps['regex'])
    else:
        oklabs = fb['data'].labels.copy()
        
    
    iters=list(ps['dataFB'].keys())
    for l in oklabs:
        cmax=0
        for nbuf in iters:
            buf=ps['dataFB'][nbuf]
            dataind=buf['data'].labels.index(l)+2
            dr=buf['data'].data.get(dataind)[::-1,:]#[::-1,:,dataind]
            if buf['zoom'][0:4]!=[0,0,-1,-1]:
                dr=dr[buf['zoom'][1]:buf['zoom'][3],buf['zoom'][0]:buf['zoom'][2]]
            pv  = np.max(dr)                
            cmax = max(pv,cmax)
            ps['display'].scalemaxlist[l]=cmax
 
