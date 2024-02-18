# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 13:34:44 2016

@author: samwebb
"""

import string
import collections
import re

def stripXML(string):
    return re.sub('<[^>]*>', '', string).strip() 

class MaterialItem:
    def __init__(self):
        
        self.name = None
        self.comment = None
        self.density = None
        self.thickness = None
        self.compoundList = []
        self.compoundFraction = []
        
    def getCL(self):      
        return ','.join(map(str, self.compoundList)) 
        
    def getCF(self):
        return ','.join(map(str, self.compoundFraction)) 
        
    def get(self):
        prop={}
        prop['Comment']=self.comment
        prop['Density']=self.density
        prop['Thickness']=self.thickness
        prop['CompoundFraction']=self.compoundFraction
        prop['CompoundList']=self.compoundList
        return prop

class Library:
    def __init__(self,fn=None):
        self.fn = fn
        
        self.reset()
        
        if self.fn!=None: self.load(fn)
        

    def reset(self):
        self.materials=collections.OrderedDict()
        i=MaterialItem()
        i.name='--' 
        i.comment='blank'
        i.density=0
        i.thickness=0
        i.compoundList=['H']
        i.compoundFraction=[1]
        self.materials[i.name]=i
        
        
    def load(self,nfn=None):
        print('reading')
        if nfn==None and self.fn==None:
            print('no file')
            return
        if nfn!=None: self.fn=nfn
            
        fid=open(self.fn,'rU')
        lines=fid.readlines()
        fid.close()
        
        matsec=False
        
        newItem = MaterialItem()
                
        for liner in lines:
            line=liner.strip('\n')
            if len(line)==0 or line[0]=='#' or line[0]=='!': continue
            if line.startswith('[materials]'):
                matsec=True
                continue
            if not matsec: continue
            if line[0]=="[":
                #save curmaterial
                if newItem.name!=None: self.materials[newItem.name]=newItem
                newItem = MaterialItem()
                if "materials" not in line: #end of section
                    matsec=False
                    continue
                #get name from [materials.Name]
                newItem.name=line.translate(str.maketrans('','','[]')).split('.')[1]
                continue
            dl = line.split('=')
            if "comment" in dl[0].lower():
                newItem.comment = '='.join(dl[1:])
            if "density" in dl[0].lower():
                newItem.density = float(dl[1])
            if "thickness" in dl[0].lower():
                newItem.thickness = float(dl[1])
            if "compoundfraction" in dl[0].lower():
                newItem.compoundFraction = list(map(float,dl[1].split(',')))
            if "compoundlist" in dl[0].lower():
                newItem.compoundList = list(map(str.strip,dl[1].split(',')))
            

    
    def save(self,nfn=None):
        if nfn==None and self.fn==None:
            print('no file')
            return
        if nfn!=None: self.fn=nfn

        if len(self.materials)==0:
            print('no data in materials')
            return
            
        fid=open(self.fn,'w')
        
        fid.write("[materials]\n\n")
        for m in list(self.materials.values()):
            if m.name=='--': continue
            fid.write("[materials."+m.name+"]\n")
            fid.write("Comment = "+m.comment+"\n")
            fid.write("CompoundFraction = "+m.getCF()+"\n")
            fid.write("CompoundList = "+m.getCL()+"\n")
            fid.write("Thickness = "+str(m.thickness)+"\n")
            fid.write("Density = "+str(m.density)+"\n\n")
        
        fid.write('[end]')
        fid.close()
        
  

    def loadPlistData(self,nfn):

        fid=open(nfn,'rU')
        lines=fid.readlines()
        fid.close()
        
        newItem = MaterialItem()
        itemkey = None              
              
        for liner in lines:
            line=liner.strip('\n')
            if len(line)==0 or line[0]=='#' or line[0]=='!': continue
            if "<dict>" in line:
                itemkey=None
                continue
            if "</dict>" in line:
                #save curmaterial
                if newItem.name!=None: 
                    if newItem.compoundFraction==[]: newItem.compoundFraction=[1.0]
                    if newItem.thickness==None: newItem.thickness=0.0005
                    if newItem.comment==None: newItem.comment = newItem.name
                    self.materials[newItem.name]=newItem
                newItem = MaterialItem()
                continue
            if "<key>" in line:
                itemkey=stripXML(line)
                continue
            if "<string>" in line:
                if itemkey==None: print("KEY ERROR")
                if string.lower(itemkey)=='density':
                    newItem.density=float(stripXML(line))
                if string.lower(itemkey)=='thickness':
                    newItem.thickness=float(stripXML(line))
                if string.lower(itemkey)=='name':
                    newItem.name=stripXML(line)
                if string.lower(itemkey)=='comment':
                    newItem.comment=stripXML(line)
                if string.lower(itemkey)=='formula':
                    newItem.compoundList=[stripXML(line)]
                continue
            
if __name__ == "__main__":
    d=Library()
    d.loadPlistData('FormulaData.plist.txt')
    d.save('defaultMaterials.cfg')
