# -*- coding: utf-8 -*-
"""
Created on Mon May  8 10:42:44 2023

@author: f006sq8
"""
import tkinter

import numpy as np

class MultiFitObj:
    def __init__(self,xd,yd,maxN,default=False):
        self.xd=xd
        self.yd=yd
        self.yfit=[]
        self.xpvs=[]
        self.ratio=np.where(xd>1,yd/xd,0)
        maxslope=1.0*np.mean(self.ratio)
        self.initguess=maxslope/maxN*(np.arange(maxN)+1)  #slope, int

        if not default:
            for i in range(maxN):
                ev=tkinter.simpledialog.askfloat(title='MultiRegression',prompt='Enter starting guess for slope '+str(i+1),initialvalue=self.initguess[i])
                if ev!='' or ev is not None:
                    self.initguess[i]=ev

                
        self.initguess=tuple(self.initguess)
        
    def eqn(self,pars):
        yf=[]
        for j in pars:
            yf.append((self.yd-self.xd*j)**2)
#            yf.append(np.where(self.yd>0,(self.yd-self.xd*j)**2,0))
#            yf.append(np.where(self.yd>0,(self.yd-self.xd*j)**2/(self.yd**2),0))
        yf=np.array(yf)
        mv=np.min(yf,axis=0)
        nv=np.argmin(yf,axis=0)+1
        nv=nv*np.where(self.yd>0,1,0)
        nv=nv-1
        for i in range(len(pars)):
            nc=(np.count_nonzero(nv==i))
            if nc>0.01*len(self.xd): 
                mv[i]=mv[i]/nc
            else:
                mv[i]=1e10
        return sum(mv)
        
    def calc(self,pars):
        order=np.argsort(self.xd)
        nx=self.xd[order]
        for j in pars:
            ny=nx*j   
            
            if len(np.where(ny>np.max(self.yd))[0])>0:
                ind=np.where(ny>np.max(self.yd))[0][0]
                self.yfit.append(ny[:ind])
                self.xpvs.append(nx[:ind])
            else:
                self.yfit.append(ny)
                self.xpvs.append(nx)
        
