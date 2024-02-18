#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 14:38:39 2023

@author: samwebb
"""

#standard imports
import fnmatch
import functools
import math
import os
import sys
import tkinter
from tkinter.ttk import Button, Style


#third party
import numpy as np
import Pmw 


#local imports
import BatchAnalyze
import BatchDisplay
import BatchProcess
import globalfuncs
from MasterClass import MasterClass
import PmwTtkButtonBox
import PmwTtkNoteBook
import PmwTtkRadioSelect
import ScrollTree


SMAKStyle=Style()
SMAKStyle.theme_use('default')


DEFTYPES={}

###################### DISPLAY ######
DEFTYPES['edgeremoval']={'text':'Edge Removal','menu':'Display', 'submenu':'Display','cb':BatchDisplay.edgezoom}
DEFTYPES['setMaxDisp']={'text':'Set Display Maximum','menu':'Display', 'submenu':'Display','regex':True ,'cb':BatchDisplay.setMaxDisplay}
DEFTYPES['balanceMaxDisp']={'text':'Balance Display Maximum','menu':'Display', 'submenu':'Display', 'regex':True ,'cb':BatchDisplay.balanceMaxDisplay}
DEFTYPES['defaultMaxDisp']={'text':'Default Display Maximum','menu':'Display', 'submenu':'Display', 'regex':True ,'cb':BatchDisplay.defaultMaxDisplay}
DEFTYPES['saveDisplays']={'text':'Save Displays', 'menu':'Display', 'submenu':'Display', 'regex':True , 'cb':BatchDisplay.saveDisplay} 
DEFTYPES['saveTiffDisplays']={'text':'Save HiRes Displays', 'menu':'Display', 'submenu':'Display', 'regex':True , 'cb':BatchDisplay.saveTiffDisplay} 
DEFTYPES['saveProcessed']={'text':'Save Processed', 'menu':'Display', 'submenu':'Display', 'cb':BatchDisplay.saveProcessed} 
                            
#DEFTYPE\\'fn']={'text':'Normalize to Time', 'menu':'Process'} 
#DEFTYPES['fn']={'text':'Normalize to I0', 'menu':'Process'} 

###################### PROCESS - MASK ######
### other mask creations?
DEFTYPES['zoomAsMask']={'text':'Zoom As Mask', 'menu':'Process', 'submenu':'Mask', 'cb':BatchProcess.maskaszoom}
DEFTYPES['chanFromMask']={'text':'Create New Channel from Mask', 'menu':'Process', 'submenu':'Mask','cb':BatchProcess.addChanFromMask} 
DEFTYPES['addMaskToChan']={'text':'Add Mask to Channel', 'menu':'Process', 'submenu':'Mask', 'cb':BatchProcess.addMaskToChan} 
DEFTYPES['removeMaskFromChan']={'text':'Remove Mask from Channel', 'menu':'Process', 'submenu':'Mask', 'cb':BatchProcess.removeMaskFromChan} 
DEFTYPES['invMask']={'text':'Invert Mask', 'menu':'Process', 'submenu':'Mask', 'cb':BatchProcess.invertMask} 

###################### PROCESS - MATH A ######
#single channel Math Operations
DEFTYPES['Log']={'text':'Log Transforms', 'menu':'Process', 'submenu': 'MathA', 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['Smooth']={'text':'Smooth', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['Sharpen']={'text':'Sharpen', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['Derivative']={'text':'Derivative', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['Abs Deriv']={'text':'Abs Derivative', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['Apply Mask']={'text':'Appply Mask', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['Laplacian']={'text':'Laplacian', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['Abs Laplacian']={'text':'Abs Laplacian', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['Exp']={'text':'Exponential', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['AbsVal']={'text':'Absolute Value', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['2^x']={'text':'2^x', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['Sqrt']={'text':'Sqrt', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['Vert Shift']={'text':'Vert Shift', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 
DEFTYPES['Horz Shift']={'text':'Horz Shift', 'menu':'Process', 'submenu':'MathA' , 'regex':True , 'cb':BatchProcess.mathSingleChan} 

###################### PROCESS - MATH B ######
DEFTYPES['Add']={'text':'Add', 'menu':'Process', 'submenu':'MathB' , 'cb':BatchProcess.mathTwoChan} 
DEFTYPES['Subtract']={'text':'Subtract', 'menu':'Process', 'submenu':'MathB' , 'cb':BatchProcess.mathTwoChan} 
DEFTYPES['Multiply']={'text':'Multiply', 'menu':'Process', 'submenu':'MathB' , 'cb':BatchProcess.mathTwoChan} 
DEFTYPES['Divide']={'text':'Divide', 'menu':'Process', 'submenu':'MathB' , 'cb':BatchProcess.mathTwoChan} 
DEFTYPES['Align']={'text':'Align', 'menu':'Process', 'submenu':'MathB' , 'cb':BatchProcess.mathTwoChan} 

###################### PROCESS - FILTERING ######
DEFTYPES['filterMean']={'text':'Mean', 'menu':'Process', 'submenu':'Filtering', 'regex':True ,'cb':BatchProcess.filterGeneral} 
DEFTYPES['filterMedian']={'text':'Median', 'menu':'Process', 'submenu':'Filtering', 'regex':True, 'cb':BatchProcess.filterGeneral} 
DEFTYPES['filterMin']={'text':'Min', 'menu':'Process', 'submenu':'Filtering', 'regex':True, 'cb':BatchProcess.filterGeneral} 
DEFTYPES['filterMax']={'text':'Max', 'menu':'Process', 'submenu':'Filtering', 'regex':True, 'cb':BatchProcess.filterGeneral} 
DEFTYPES['filterOpen']={'text':'Open', 'menu':'Process', 'submenu':'Filtering', 'regex':True,'cb':BatchProcess.filterGeneral} 
DEFTYPES['filterClose']={'text':'Close', 'menu':'Process', 'submenu':'Filtering', 'regex':True,'cb':BatchProcess.filterGeneral} 
DEFTYPES['filterGradient']={'text':'Gradient', 'menu':'Process', 'submenu':'Filtering', 'regex':True,'cb':BatchProcess.filterGeneral} 
DEFTYPES['filterBlur']={'text':'Blur', 'menu':'Process', 'submenu':'Filtering', 'regex':True,'cb':BatchProcess.filterGeneral} 
DEFTYPES['filterMeanShift']={'text':'MeanShift', 'menu':'Process', 'submenu':'Filtering', 'regex':True,'cb':BatchProcess.filterGeneral} 
DEFTYPES['filterInvert']={'text':'Invert', 'menu':'Process', 'submenu':'Filtering', 'regex':True,'cb':BatchProcess.filterGeneral} 

###################### PROCESS - THRESHOLDING ######
DEFTYPES['threshTruncMax']={'text':'TruncMax', 'menu':'Process', 'submenu':'Threshold','regex':True,'cb':BatchProcess.threshGeneral} 
DEFTYPES['threshTruncMin']={'text':'TruncMin', 'menu':'Process', 'submenu':'Threshold','regex':True,'cb':BatchProcess.threshGeneral} 
DEFTYPES['threshInvBinary']={'text':'InvBinary', 'menu':'Process', 'submenu':'Threshold','regex':True,'cb':BatchProcess.threshGeneral} 
DEFTYPES['threshBinary']={'text':'Binary', 'menu':'Process', 'submenu':'Threshold','regex':True,'cb':BatchProcess.threshGeneral} 
DEFTYPES['threshOtsu']={'text':'Otsu', 'menu':'Process', 'submenu':'Threshold','regex':True,'cb':BatchProcess.threshGeneral} 
DEFTYPES['threshZero']={'text':'ThreshZero', 'menu':'Process', 'submenu':'Threshold','regex':True,'cb':BatchProcess.threshGeneral} 
DEFTYPES['threshInvZero']={'text':'InvThreshZero', 'menu':'Process', 'submenu':'Threshold','regex':True,'cb':BatchProcess.threshGeneral} 
DEFTYPES['threshAdapt']={'text':'Adapt', 'menu':'Process', 'submenu':'Threshold','regex':True,'cb':BatchProcess.threshGeneral} 
DEFTYPES['threshInvAdapt']={'text':'InvAdapt', 'menu':'Process', 'submenu':'Threshold','regex':True,'cb':BatchProcess.threshGeneral} 

###################### ANALYZE - XANES ######
DEFTYPES['doXANESFit']={'text':'XANES Fitting', 'menu':'Analyze', 'submenu':'XANES','cb':BatchAnalyze.doXANESfit} 

###################### ANALYZE - QUANTIFY ######
DEFTYPES['doQuant']={'text':'Quantify', 'menu':'Analyze', 'submenu':'Quantify','cb':BatchAnalyze.doQuantify} 

###################### ANALYZE - PCA ######
DEFTYPES['sPCA']={'text':'sPCA', 'menu':'Analyze', 'submenu':'PCA','regex':True,'cb':BatchAnalyze.PCAGeneral} 
DEFTYPES['CCIPCA']={'text':'CCIPCA', 'menu':'Analyze', 'submenu':'PCA', 'regex':True,'cb':BatchAnalyze.PCAGeneral} 
DEFTYPES['FA']={'text':'FactorAnalysis', 'menu':'Analyze', 'submenu':'PCA','regex':True,'cb':BatchAnalyze.PCAGeneral} 
DEFTYPES['NMF']={'text':'NMF', 'menu':'Analyze', 'submenu':'PCA','regex':True,'cb':BatchAnalyze.PCAGeneral} 
DEFTYPES['Dictionary']={'text':'Dictionary', 'menu':'Analyze', 'submenu':'PCA','regex':True,'cb':BatchAnalyze.PCAGeneral} 
DEFTYPES['SiVM']={'text':'SiVM', 'menu':'Analyze', 'submenu':'PCA','regex':True,'cb':BatchAnalyze.PCAGeneral} 
DEFTYPES['FastICA']={'text':'FastICA', 'menu':'Analyze', 'submenu':'PCA','regex':True,'cb':BatchAnalyze.PCAGeneral} 
#DEFTYPES['LDA']={'text':'LDA', 'menu':'Analyze', 'submenu':'PCA','regex':True,'cb':BatchAnalyze.PCAGeneral} 
DEFTYPES['Kmeans']={'text':'Kmeans', 'menu':'Analyze', 'submenu':'PCA','regex':True,'cb':BatchAnalyze.PCAGeneral} 
DEFTYPES['Gaussian']={'text':'Gaussian', 'menu':'Analyze', 'submenu':'PCA','regex':True,'cb':BatchAnalyze.PCAGeneral} 


#### segmentation?  particles?

###################### ANALYZE - MCA ######
### MCA/FTIR analysis
DEFTYPES['defMCAfile']={'text':'Define MCA file', 'menu':'Analyze', 'submenu':'MCA','cb':BatchAnalyze.defineMCAfile } 
DEFTYPES['defxrayslope']={'text':'Set MCA Slope', 'menu':'Analyze', 'submenu':'MCA','cb':BatchAnalyze.setMCAxraySlope } 
DEFTYPES['intMCArange']={'text':'Integrate MCA by bin range', 'menu':'Analyze', 'submenu':'MCA' ,'cb':BatchAnalyze.intMCArange } 
DEFTYPES['intMCAbin']={'text':'Integrate MCA by bin', 'menu':'Analyze', 'submenu':'MCA' ,'cb':BatchAnalyze.intMCAbyBin } 
DEFTYPES['intMCAvalue']={'text':'Integrate MCA by value', 'menu':'Analyze', 'submenu':'MCA' ,'cb':BatchAnalyze.intMCAbyValue } 
#PCA on MCA data...
DEFTYPES['PCAMCAdata']={'text':'PCA on MCA data', 'menu':'Analyze', 'submenu':'MCA' ,'cb':BatchAnalyze.doPCAonMCAdata } 

###################### ANALYZE - PyMCA ######
#load pymca settings
DEFTYPES['PyMCAload']={'text':'Load PyMCA Settings', 'menu':'Analyze', 'submenu':'PyMCA' ,'cb':BatchAnalyze.doPyMCAload } 
#perform fit on zoom
DEFTYPES['PyMCAzoomfit']={'text':'Fit PyMCA on Zoom', 'menu':'Analyze', 'submenu':'PyMCA' ,'cb':BatchAnalyze.doPyMCAzoomfit} 
#perform fit on entire map
DEFTYPES['PyMCAfullfit']={'text':'Fit PyMCA on Full Data', 'menu':'Analyze', 'submenu':'PyMCA' ,'cb':BatchAnalyze.doPyMCAfullfit } 

###################### ANALYZE - Octavvs FTIR ######
DEFTYPES['loadFTIRparam']={'text':'Load FTIR Settings', 'menu':'Analyze', 'submenu':'FTIR' ,'cb':BatchAnalyze.doFTIRload}
DEFTYPES['switchSpectumValues']={'text':'Switch to Wavenumbers', 'menu':'Analyze', 'submenu':'FTIR' ,'cb':BatchAnalyze.switchWavenumber}
DEFTYPES['correctIR']={'text':'Correct FTIR File', 'menu':'Analyze', 'submenu':'FTIR' ,'cb':BatchAnalyze.doFTIRcorrections}
DEFTYPES['correctIRload']={'text':'Correct FTIR File, load new', 'menu':'Analyze', 'submenu':'FTIR' ,'cb':BatchAnalyze.doFTIRcorrectionsLoad}


#DEFTYPES['fn']={'text':'Set MCA-HDF Compression', 'menu':'Analyze', 'submenu':'MCA' } 
#DEFTYPES['fn']={'text':'Construct Xspress3 HDFs', 'menu':'Analyze', 'submenu':'MCA' } 

#DEFTYPES['fn']={'text':'Set MCA multi-file lines', 'menu':'Analyze', 'submenu':'MCA' } 
#DEFTYPES['fn']={'text':'Split multi-files', 'menu':'Analyze', 'submenu':'MCA' } 

#maybe no need to view?
#DEFTYPES['fn']={'text':'Get MCA from mask', 'menu':'Analyze', 'submenu':'MCA' } 
#DEFTYPES['fn']={'text':'Get MCA from cluster map', 'menu':'Analyze', 'submenu':'MCA' } 

#DEFTYPES['fn']={'text':'Construct HDFs from OOMap', 'menu':'Analyze', 'submenu':'MCA' } 
#DEFTYPES['fn']={'text':'Convert UV-MCA to RGB', 'menu':'Analyze', 'submenu':'MCA' } 
#DEFTYPES['fn']={'text':'Convert UV-MCA to XYZ', 'menu':'Analyze', 'submenu':'MCA' } 
#DEFTYPES['fn']={'text':'Convert UV-MCA to Lab', 'menu':'Analyze', 'submenu':'MCA' } 


DEFMENUTYPES=['Display','Process','Analyze']
DEFPROCSUBMENUTYPES=['Mask','MathA','MathB','Filtering','Threshold']
DEFANALSUBMENUTYPES=['PCA','MCA','PyMCA','XANES','Quantify','FTIR']



###################################################################################################
TYPEREQUIRES={}

###################### DISPLAY ######
TYPEREQUIRES['edgeremoval']=None
TYPEREQUIRES['setMaxDisp']={'params':['value'],'validate':['real'],'extra':['displayS']}
TYPEREQUIRES['balanceMaxDisp']={'extra':['displayM']}
TYPEREQUIRES['defaultMaxDisp']={'extra':['displayS']}
TYPEREQUIRES['saveDisplays']={'extra':['display']}
TYPEREQUIRES['saveTiffDisplays']={'extra':['display']}
TYPEREQUIRES['saveProcessed']=None

###################### PROCESS - MASK ######
TYPEREQUIRES['zoomAsMask']=None
TYPEREQUIRES['chanFromMask']={'extra':['addchan']}
TYPEREQUIRES['addMaskToChan']={'params':['destchan'],'validate':[None]}
TYPEREQUIRES['removeMaskFromChan']={'params':['destchan'],'validate':[None]}
TYPEREQUIRES['invMask']=None

###################### PROCESS - FILTERING ######
TYPEREQUIRES['filterMean']={'params':['size'],'validate':['integer'],'extra':['addchan']}
TYPEREQUIRES['filterMedian']={'params':['size'],'validate':['integer'],'extra':['addchan']}
TYPEREQUIRES['filterMin']={'params':['size'],'validate':['integer'],'extra':['addchan']}
TYPEREQUIRES['filterMax']={'params':['size'],'validate':['integer'],'extra':['addchan']}
TYPEREQUIRES['filterOpen']={'params':['size'],'validate':['integer'],'extra':['addchan']}
TYPEREQUIRES['filterClose']={'params':['size'],'validate':['integer'],'extra':['addchan']}
TYPEREQUIRES['filterGradient']={'params':['size'],'validate':['integer'],'extra':['addchan']}
TYPEREQUIRES['filterBlur']={'params':['size','sigma'],'validate':['integer','real'],'extra':['addchan']}
TYPEREQUIRES['filterMeanShift']={'params':['size'],'validate':['integer'],'extra':['addchan']}
TYPEREQUIRES['filterInvert']={'extra':['addchan']}

###################### PROCESS - THRESHOLDING ######
TYPEREQUIRES['threshTruncMax']={'params':['level','value'],'validate':['real','real'],'extra':['addchan']} 
TYPEREQUIRES['threshTruncMin']={'params':['level','value'], 'validate':['real','real'],'extra':['addchan']} 
TYPEREQUIRES['threshInvBinary']={'params':['level'], 'validate':['real'],'extra':['addchan']} 
TYPEREQUIRES['threshBinary']={'params':['level'],'validate':['real'],'extra':['addchan']}  
TYPEREQUIRES['threshOtsu']={'params':['level'],'validate':['real'],'extra':['addchan']} 
TYPEREQUIRES['threshZero']={'params':['level','value'],'validate':['real','real'],'extra':['addchan']} 
TYPEREQUIRES['threshInvZero']={'params':['level','value'],'validate':['real','real'],'extra':['addchan']} 
TYPEREQUIRES['threshAdapt']={'params':['level','value'],'validate':['real','integer'],'extra':['addchan']} 
TYPEREQUIRES['threshInvAdapt']={'params':['level','value'],'validate':['real','integer'],'extra':['addchan']} 

###################### PROCESS - MATH A ######
TYPEREQUIRES['Log']={'extra':['addchan']}
TYPEREQUIRES['Smooth']={'extra':['addchan']}
TYPEREQUIRES['Sharpen']={'extra':['addchan']}
TYPEREQUIRES['Derivative']={'extra':['addchan']}
TYPEREQUIRES['Abs Deriv']={'extra':['addchan']}
TYPEREQUIRES['Apply Mask']={'extra':['addchan']}
TYPEREQUIRES['Laplacian']={'extra':['addchan']}
TYPEREQUIRES['Abs Laplacian']={'extra':['addchan']}
TYPEREQUIRES['Exp']={'extra':['addchan']}
TYPEREQUIRES['AbsVal']={'extra':['addchan']}
TYPEREQUIRES['2^x']={'extra':['addchan']}
TYPEREQUIRES['Sqrt']={'extra':['addchan']}

###################### PROCESS - MATH B ######
TYPEREQUIRES['Add']={'params':['Adata','Bdata'],'validate':[None,None],'extra':['addchan']}
TYPEREQUIRES['Subtract']={'params':['Adata','Bdata'],'validate':[None,None],'extra':['addchan']}
TYPEREQUIRES['Multiply']={'params':['Adata','Bdata'],'validate':[None,None],'extra':['addchan']}
TYPEREQUIRES['Divide']={'params':['Adata','Bdata'],'validate':[None,None],'extra':['addchan']}
TYPEREQUIRES['Align']={'params':['Adata','Bdata'],'validate':[None,None],'extra':['addchan']}     ## this needs to be fixed in math!
TYPEREQUIRES['Vert Shift']={'params':['scalar'],'validate':['integer'],'extra':['addchan']}
TYPEREQUIRES['Horz Shift']={'params':['scalar'],'validate':['integer'],'extra':['addchan']}


###################### ANALYZE - XANES ######
TYPEREQUIRES['doXANESFit']={'params':['xasfile'],'validate':[None],'extra':['addchan']} 

###################### ANALYZE - QUANTIFY ######
TYPEREQUIRES['doQuant']={'params':['quantfile'],'validate':[None],'extra':['addchan']} 

###################### ANALYZE - MCA ######
TYPEREQUIRES['defMCAfile']={'params':['filename'],'validate':[None]} 
TYPEREQUIRES['defxrayslope']={'params':['slope'],'validate':['real']}
TYPEREQUIRES['intMCArange']={'params':['binmin','binmax','binint'],'validate':['integer','integer','integer'],'extra':['addchan']} 
TYPEREQUIRES['intMCAbin']={'params':['binmin','binmax','name'],'validate':['integer','integer',None], 'extra':['addchan']} 
TYPEREQUIRES['intMCAvalue']={'params':['valmin','valmax','name'],'validate':['integer','integer',None],'extra':['addchan'] } 

TYPEREQUIRES['PCAMCAdata']={'params':['comps','minbin','maxbin'],'validate':['integer','integer','integer'], 'extra':['addchan']} 

###################### ANALYZE - PyMCA ######
TYPEREQUIRES['PyMCAload']={'params':['pyfile'],'validate':[None]} 
TYPEREQUIRES['PyMCAzoomfit']={'extra':['addchan']} 
TYPEREQUIRES['PyMCAfullfit']={'extra':['addchan']} 

###################### ANALYZE - Octavvs FTIR ######
TYPEREQUIRES['loadFTIRparam']={'params':['irfile'],'validate':[None]}
TYPEREQUIRES['switchSpectumValues']=None
TYPEREQUIRES['correctIR']=None
TYPEREQUIRES['correctIRload']=None

###################### ANALYZE - PCA ######
TYPEREQUIRES['sPCA']={'params':['comps'], 'validate':['integer'], 'checkbox':['Single File','Multi File'],'extra':['addchan'] } 
TYPEREQUIRES['CCIPCA']={'params':['comps'], 'validate':['integer'],'checkbox':['Single File','Multi File'],'extra':['addchan'] } 
TYPEREQUIRES['FA']={'params':['comps'], 'validate':['integer'], 'checkbox':['Single File','Multi File'],'extra':['addchan'] } 
TYPEREQUIRES['NMF']={'params':['comps'], 'validate':['integer'], 'checkbox':['Single File','Multi File'],'extra':['addchan'] } 
TYPEREQUIRES['Dictionary']={'params':['comps'], 'validate':['integer'], 'checkbox':['Single File','Multi File'],'extra':['addchan'] } 
TYPEREQUIRES['SiVM']={'params':['comps','thresh'], 'validate':['integer','real'], 'checkbox':['Single File','Multi File'], 'extra':['addchan'] } 
TYPEREQUIRES['FastICA']={'params':['comps'], 'validate':['integer'], 'checkbox':['Single File','Multi File'],'extra':['addchan'] } 
#TYPEREQUIRES['LDA']={'params':['comps'], 'validate':['integer'], 'checkbox':['Single File','Multi File'],'extra':['addchan'] } 
TYPEREQUIRES['Kmeans']={'params':['comps'], 'validate':['integer'], 'checkbox':['Single File','Multi File'],'extra':['addchan'] } 
TYPEREQUIRES['Gaussian']={'params':['comps'], 'validate':['integer'], 'checkbox':['Single File','Multi File'],'extra':['addchan'] } 


class MCALoadObject:
    def __init__(self,master,name,dir=''):

        self.dir=dir        
        
        f=tkinter.Frame(master,bd=2,background='#d4d0c8')

        filebar=tkinter.Frame(f,bd=2,background='#d4d0c8')
        self.fe=Pmw.EntryField(filebar, label_text=name+" : MCA =",labelpos=tkinter.W,validate=None,entry_width=38,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.fe.pack(side=tkinter.LEFT,padx=5,pady=2,fill=tkinter.X)
        b=Button(filebar,text="Open",command=self.load,width=7)
        b.pack(side=tkinter.LEFT,padx=2,pady=2)
        filebar.pack(side=tkinter.LEFT,padx=2,pady=2,fill=tkinter.X)
        f.pack(side=tkinter.TOP,pady=2,fill=tkinter.X)

    def load(self):
        fty=[("hdf files","*.hdf5"),("all files","*")]
        fn=globalfuncs.ask_for_file(fty,self.dir)
        if fn!='':
            globalfuncs.entry_replace(self.fe,fn)

class Macro:
    def __init__(self,item):
        self.macro=item
        print (item)
        self.execnum=0
        
    def execute(self,fb,ac,d,dfb):
        
        kw={}
        exitearly=False
        if 'param' in self.macro:
            for p,v in zip(self.macro['param'],self.macro['value']):
                kw[p]=v
        if 'regex' in self.macro:
            kw['regex']=self.macro['regex']
        if 'filedir' in self.macro:
            kw['filedir']=self.macro['filedir']
        if 'checkbox' in self.macro:
            kw['checkbox'] = self.macro['checkbox']
            if kw['checkbox']=='Multi File' and self.execnum>0: 
                return
        #check for all keys if needed
        if TYPEREQUIRES[self.macro['func']] is not None:
            if 'params' in TYPEREQUIRES[self.macro['func']]:
                for p in TYPEREQUIRES[self.macro['func']]['params']:
                    if p not in kw:
                        print ('need parmeter '+p+' for macro function: ',self.macro['func'])
                        return
            if 'extra' in TYPEREQUIRES[self.macro['func']]:
                if 'addchan' in TYPEREQUIRES[self.macro['func']]['extra']:
                    kw['addchan']=ac
                if 'display' in TYPEREQUIRES[self.macro['func']]['extra']:
                    kw['display']=d
                if 'displayS' in TYPEREQUIRES[self.macro['func']]['extra']:
                    kw['display']=d
                    exitearly=True
                if 'displayM' in TYPEREQUIRES[self.macro['func']]['extra']:
                    kw['display']=d
                    kw['dataFB']=dfb
                    exitearly=True
                                        
            if 'submenu' in DEFTYPES[self.macro['func']] and DEFTYPES[self.macro['func']]['submenu'] in ['Filtering','Threshold']:
                kw['filter']=DEFTYPES[self.macro['func']]['text']
            if 'submenu' in DEFTYPES[self.macro['func']] and DEFTYPES[self.macro['func']]['submenu'] in ['MathA','MathB','PCA']:
                kw['oper']=self.macro['func']
            if 'checkbox' in self.macro and 'submenu' in DEFTYPES[self.macro['func']] and DEFTYPES[self.macro['func']]['submenu'] in ['PCA']:
                kw['dataFB']=dfb

        if exitearly and self.execnum>0:
            return
        DEFTYPES[self.macro['func']]['cb'](fb,kw=kw)
        self.execnum+=1
        
        

class ScriptManager:
    def __init__(self,display,addchannel,filedir,imgwin):
        self.maindisp = display
        self.addchannel = addchannel
        self.filedir=filedir
        self.imgwin=imgwin
        
    def update(self,dfb,afb):
        self.dataFileBuffer = dfb
        self.activeFileBuffer = afb


    def prepMacro(self,command):
        self.command=command
        for c in self.command:
            if 'param' in c and "filename" in c['param']:
                self.editme = c['value']
                self.getFileAssociations()
                #print (self.editme)
                c['value']=[self.editme]
        
    def defMacro(self):

        self.comlist=[]
        for c in self.command:
            if 'func' not in c:
                print ('invalid command:',c)
                return False
            c['filedir']=self.filedir
            self.comlist.append(Macro(c))
        return True

    
    def execute(self):
        for n,fb in zip(self.dataFileBuffer.keys(),self.dataFileBuffer.values()):
            for c in self.comlist:
                c.execute([n,fb],self.addchannel,self.maindisp,self.dataFileBuffer)



    def getFileAssociations(self):
        
        self.getMCADataDialog=Pmw.Dialog(self.imgwin,title="MCA File Associations",buttons=('OK','Cancel'),defaultbutton='OK',
                                        command=self.getMCADataDone)
        intex=self.getMCADataDialog.interior()
        intex.configure(background='#d4d0c8')
        self.mcaloaddict={}        

        for n in self.dataFileBuffer.keys():
            obj=MCALoadObject(intex,n,dir=self.filedir)
            self.mcaloaddict[n]=obj
            
        #Pmw.alignlabels(list(self.mcaloaddict.values()))
        self.getMCADataDialog.activate()
        
        

    def getMCADataDone(self,result):
        if result=='Cancel':
            print('Load cancelled')
            self.getMCADataDialog.deactivate()   
            return
        
        newd={}
        for n in self.mcaloaddict.keys():
            val = self.mcaloaddict[n].fe.getvalue()
            newd[n]=val
        self.editme = newd
        
        self.getMCADataDialog.deactivate()  
            

class ScriptItemWidget():
    def __init__(self,master,cb,dfb):
        
        self.delcb=cb
        self.dfb=dfb
        self.frame = tkinter.Frame(master)
        self.frame.pack(side=tkinter.TOP,padx=2,pady=2)
    
        b=PmwTtkButtonBox.PmwTtkButtonBox(self.frame,hull_background='#d4d0c8')
        b.add('X',command=self.remove,style='RED.TButton',width=5)
        b.pack(side=tkinter.LEFT,padx=3,pady=2)

        self.menutype = Pmw.ComboBox(self.frame,history=0,selectioncommand=self.chooseMenuType,hull_background='#d4d0c8',
                                      labelpos='w',label_text="Menu: ",label_background='#d4d0c8',hull_width=50) 
        self.menutype.setlist(DEFMENUTYPES)
        self.menutype.pack(side=tkinter.LEFT,padx=3,pady=2)  

        self.submenutype = Pmw.ComboBox(self.frame,history=0,selectioncommand=self.chooseSubMenuType,hull_background='#d4d0c8',
                                      labelpos='w',label_text="Submenu: ",label_background='#d4d0c8',hull_width=50) 
        self.submenutype.pack(side=tkinter.LEFT,padx=3,pady=2)  

        self.optype = Pmw.ComboBox(self.frame,history=0,selectioncommand=self.chooseOpType,hull_background='#d4d0c8',
                                      labelpos='w',label_text="Operation: ",label_background='#d4d0c8',hull_width=50) 
        self.optype.pack(side=tkinter.LEFT,padx=3,pady=2)  

        self.entryFrame = tkinter.Frame(self.frame)
        self.entryFrame.pack(side=tkinter.TOP, padx=2,pady=2)
        
        self.subwids={}


    def remove(self):
        self.delcb(self)
        
    def destroy(self):
        self.frame.destroy()
        
    def valid(self):
        if self.menutype.get()=='': return False
        if self.submenutype.get()=='': return False
        if self.optype.get()=='': return False
        if len(self.subwids)>0:
            for k,w in zip(self.subwids.keys(),self.subwids.values()):
                if k not in ['checkbox']:
                    if not w.valid(): return False
        #for regex?
        
        return True

    def chooseMenuType(self,sel):
        for w in self.subwids.values():
            w.destroy()
        self.subwids={}
        self.optype.clear()
        self.submenutype.clear()
        
        if sel == 'Display':
            self.submenutype.setlist(['Display'])
        elif sel == 'Process':
            self.submenutype.setlist(DEFPROCSUBMENUTYPES)
        elif sel == 'Analyze':
            self.submenutype.setlist(DEFANALSUBMENUTYPES)
        else:
            self.submenutype.clear()
        

    def chooseSubMenuType(self,sel):
        for w in self.subwids.values():
            w.destroy()
        self.subwids={}
        self.optype.clear()
        
        oplist=[]
        for t in DEFTYPES.keys():
            if t=='fn': continue
            if self.menutype.get() == DEFTYPES[t]['menu'] and self.submenutype.get() == DEFTYPES[t]['submenu']:
                oplist.append(t)
        self.optype.setlist(oplist)
        
    def chooseOpType(self,sel):
        for w in self.subwids.values():
            w.destroy()
        self.subwids={}

        if TYPEREQUIRES[sel] == None:
            return
        self.subwids={}
        align=[]
        if 'params' in TYPEREQUIRES[sel]:
            for wt,val in zip(TYPEREQUIRES[sel]['params'],TYPEREQUIRES[sel]['validate']):
                nw = Pmw.EntryField(self.entryFrame,labelpos='w',label_text=wt+': ',entry_width=15,validate=val,hull_background='#d4d0c8',label_background='#d4d0c8')
                if wt=='filename':
                    #something more complex here...
                    nw.setvalue("-MCA for File-")
                    nw.component('entry').configure(state=tkinter.DISABLED)
                align.append(nw)
                self.subwids[wt]=nw
                nw.pack(side=tkinter.TOP,padx=3,pady=2)
        if 'regex' in DEFTYPES[sel]:
            nw = Pmw.EntryField(self.entryFrame,labelpos='w',label_text='Regex: ',entry_width=15,validate=None,hull_background='#d4d0c8',label_background='#d4d0c8')
            align.append(nw)
            self.subwids['regex']=nw
            nw.pack(side=tkinter.TOP,padx=3,pady=2)
        if 'checkbox' in TYPEREQUIRES[sel]:
            nw =Pmw.RadioSelect(self.entryFrame,buttontype='radiobutton',orient='vertical',hull_background='#d4d0c8')
            for text in TYPEREQUIRES[sel]['checkbox']:
                nw.add(text,background='#d4d0c8')
            nw.setvalue(TYPEREQUIRES[sel]['checkbox'][0])
            nw.pack(side=tkinter.TOP,padx=3,pady=3)
            self.subwids['checkbox']=nw
        Pmw.alignlabels(align)

class ScriptEditorParams():    
    def __init__(self, status, batchData, addinmenuOpts, mainmenubar, runAddin, dataFileBuffer):
        self.status=status
        self.batchData=batchData
        self.addinmenuOpts=addinmenuOpts
        self.dataFileBuffer = dataFileBuffer
        self.mainmenubar = mainmenubar
        self.runAddin = runAddin
    
    
class ScriptEditorWindow(MasterClass):
     
    def _create(self):
        
        self.win = Pmw.MegaToplevel(self.imgwin)
        self.win.title('Script Editor')
        self.win.userdeletefunc(func=self.kill)

        hm=self.win.interior()
        hm.configure(background='#d4d0c8')
        
        self.scriptsel=Pmw.ScrolledListBox(hm,labelpos='n',label_text='Scripts',items=self.ps.batchData.keys(),listbox_selectmode=tkinter.BROWSE,
                                              listbox_exportselection=tkinter.FALSE,selectioncommand=self.setScript,listbox_height=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.scriptsel.pack(side=tkinter.TOP,padx=4,pady=5,fill='both')
        
        
        b=PmwTtkButtonBox.PmwTtkButtonBox(hm,orient='horizontal',hull_background='#d4d0c8')
        self.addbut = b.add('Add Command',command=self.addCommand,style='LGREEN.TButton',width=15,state=tkinter.DISABLED) 
        b.add('New Script',command=self.newScript,style='GREEN.TButton',width=15) 
        self.savebut = b.add('Save Script',command=self.saveScript,style='ORANGE.TButton',width=15,state=tkinter.DISABLED) 
        b.add('Clear Script',command=self.clean,style='RED.TButton',width=15) 
        
        b.pack(side=tkinter.TOP,padx=5,pady=10)  

        h2=Pmw.ScrolledFrame(hm,usehullsize=1,vertflex='fixed',horizflex='fixed',
                             hscrollmode='static',vscrollmode='static',
                             hull_width=900,hull_height=500)
        h2.interior().configure(background='#d4d0c8')
        h2.pack(side=tkinter.TOP,pady=2)
        h=h2.interior()        

        self.namelabel = tkinter.Label(h,text="",relief=tkinter.RAISED,bd=2, background='#d4d0c8',width=95)
        self.namelabel.pack(side=tkinter.TOP,fill='x',expand=0,padx=2,pady=4)  
        
        self.widframe=h
        self.scriptwidgets={}
        self.lastid=1
     
    def addCommand(self):
        nw = ScriptItemWidget(self.widframe, self.delwid, self.ps.dataFileBuffer)
        self.scriptwidgets[self.lastid]=nw
        self.lastid+=1
        
    def newScript(self):
        self.clearscript()
        #ask for new name
        newname = tkinter.simpledialog.askstring(title='New Script',prompt='Enter the name for the script',initialvalue='myscript')
        if newname=='': return
        self.namelabel.configure(text=newname)    
        self.addbut.configure(state=tkinter.NORMAL)
        self.savebut.configure(state=tkinter.NORMAL)
        
    def saveScript(self):
        #make script dictionary
        newscr = {}
        newscr['requires']=['data']
        newscr['title']=self.namelabel.configure('text')[-1]
        newscr['seq']=[]

        kev = list(self.scriptwidgets.keys())
        kev.sort()

        #check for empty set
        if len(kev) == 0:
            if newscr['title'] in self.ps.batchData:
                #remove it
                self.ps.batchData.pop(newscr['title'])

        else:        
            valid=True
            for wn in kev:
                w=self.scriptwidgets[wn]
                if not w.valid():
                    valid=False
            if not valid:
                print ('script entries not valid')
                return

            for wn in kev:
                w=self.scriptwidgets[wn]
                command={}
                command['func']=w.optype.get()
                if len(w.subwids)>0:
                    command['param']=[]
                    command['value']=[]
                    for wek in w.subwids.keys():
                        if wek == 'regex':
                            if w.subwids[wek].getvalue()!='':
                                command[wek]=w.subwids[wek].getvalue()
                        elif wek == 'checkbox':
                            command[wek]=w.subwids[wek].getvalue()
                        else:
                            command['param'].append(wek)
                            command['value'].append(w.subwids[wek].getvalue())
                
                #add command
                newscr['seq'].append(command)
         
            #now preserve macro...
            self.ps.batchData[newscr['title']]=newscr
            globalfuncs.setstatus(self.ps.status,'Workflow script '+newscr['title']+' saved...')
        
        #edit list
        self.scriptsel.setlist(self.ps.batchData.keys())

        #edit menu?
        for it in self.ps.batchData.keys():
            scr = self.ps.batchData[it]
            if it in self.ps.addinmenuOpts: continue
            m=self.ps.mainmenubar.addmenuitem('Workflow','command',label=scr['title'],command=functools.partial(self.ps.runAddin,kwargs=scr))
            self.ps.addinmenuOpts[scr['title']]=m
        poplist=[]
        for ms in self.ps.addinmenuOpts.keys():
            if ms not in self.ps.batchData.keys():
                men = self.ps.mainmenubar.component('Workflow-menu')
                ind = men.index(ms)
                self.ps.mainmenubar.deletemenuitems('Workflow',ind)
                poplist.append(ms)
        for ms in poplist:
            self.ps.addinmenuOpts.pop(ms)
            
    
    def delwid(self,w):
        
        for k,v in zip(self.scriptwidgets.keys(),self.scriptwidgets.values()):
            if v == w:
                self.scriptwidgets.pop(k)
                break
        w.destroy()

    def clean(self):
        self.addbut.configure(state=tkinter.DISABLED)
        self.savebut.configure(state=tkinter.DISABLED)
        self.clearscript()

    def clearscript(self):
        for w in self.scriptwidgets.values():
            w.destroy()
        self.scriptwidgets={}
        self.namelabel.configure(text='')
        
    def setScript(self):
        self.clearscript()
        name = self.scriptsel.getvalue()[0]
        scr=self.ps.batchData[name]
        
        self.namelabel.configure(text=name) 
        self.addbut.configure(state=tkinter.NORMAL)
        self.savebut.configure(state=tkinter.NORMAL)
        
        #add widgets... with values
        for n in scr['seq']:
            nw = ScriptItemWidget(self.widframe, self.delwid, self.ps.dataFileBuffer)
            self.scriptwidgets[self.lastid]=nw
            self.lastid+=1
            
            nw.menutype.selectitem(DEFTYPES[n['func']]['menu'])
            nw.chooseMenuType(DEFTYPES[n['func']]['menu'])
            nw.submenutype.selectitem(DEFTYPES[n['func']]['submenu'])
            nw.chooseSubMenuType(DEFTYPES[n['func']]['submenu'])
            nw.optype.selectitem(n['func'])
            nw.chooseOpType(n['func'])

            if 'param' in n:
                for p,v in zip(n['param'],n['value']):
                    nw.subwids[p].setvalue(v)
        
            if 'regex' in n:
                nw.subwids['regex'].setvalue(n['regex'])
                     
            if 'checkbox' in n:
                nw.subwids['checkbox'].setvalue(n['checkbox'])                
                
                
                
                
                
        