# -*- coding: utf-8 -*-
"""
Created on Wed Apr 06 21:42:58 2016

@author: samwebb
"""

#standard imports
import math
import re
import string

#local imports
import mucal



class parseFormula:
    def __init__(self,formula,weights):
        self.formula = formula
        self.weights = weights
        self.result={}
        
        self.calculate()
        
    def calculate(self):
        for c in self.formula:
            for m in re.finditer(r"([A-Z][a-z]{0,2})(\d*)",c):
                if m.groups()[1]=='':
                    add = 1 * float(self.weights[self.formula.index(c)])
                else:
                    add = float(m.groups()[1]) * float(self.weights[self.formula.index(c)])
                if m.groups()[0] not in self.result.keys():
                    self.result[m.groups()[0]]=0.0
                self.result[m.groups()[0]]=self.result[m.groups()[0]]+add
                



class calculateXS:
    def __init__(self,formula,weights,density,energy,thickness=0):
        self.formula=formula
        self.weights=weights
        self.energy=energy/1000.
        self.density=density
        self.absLength = None
        self.thickness=thickness
        self.abs=None
        
        self.calculate()
        
    def calculate(self,energy=None):
        if energy != None:
            self.energy=energy/1000.
        
        parsed = parseFormula(self.formula,self.weights)
        wtsum = 0.0
        mu = 0.0
        for e in parsed.result.keys():
            if e not in mucal.esym:
                continue
            [err,energy,xsec,fl_yield,errmsg] = mucal.mucal(name=e, ephot=self.energy, unit='b')
            wtsum += parsed.result[e] * xsec[6]
            mu += xsec[3] / xsec[4] * parsed.result[e] * xsec[6]
        if wtsum==0: wtsum = 1
        mu = mu * self.density / wtsum
        self.absLength = 1/mu*10000 #cm to um
        if (self.thickness!=0):
            self.abs = (1 - math.exp(-mu*self.thickness))*100.0
  
        #print (self.formula,self.absLength)
	
