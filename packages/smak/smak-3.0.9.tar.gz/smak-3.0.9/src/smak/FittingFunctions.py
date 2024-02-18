# -*- coding: utf-8 -*-
"""
Created on Mon May  8 12:30:04 2023

@author: f006sq8
"""
import numpy as np 

#deatime model   SCA=kappa*ICR*exp(-ICR*tau) tau in usecs
def dteqn(pars,point):
    #return pars[0]*point*exp(-pars[1]/point)
    return pars[2]+pars[0]*point*np.exp(-pars[1]*point*1e-6)

def dteqnFit(point,p0,p1,p2):
    return dteqn([p0,p1,p2],point)