#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 08:53:14 2023

@author: samwebb
"""
#standard
import json
import os
import sys
import tkinter
from tkinter.ttk import Button, Style

#third party
import Pmw
import sortedcontainers

#local imports
import globalfuncs
from MasterClass import MasterClass
import mucal
import PmwTtkButtonBox


SMAKStyle=Style()
SMAKStyle.theme_use('default')

"""
Define a concentation "standard" file structure saved in JSON format

Main class has a dictionary (data) with two entries:
    
Data
    ["Properies"] - dictionary of properties
        ["Desciption"] - description of standard
        ["Matrix"] - matrix of standard
        ["Name"] - name of standard
        
    ["Results"] - list of information
        FOR EACH ENTRY IN THE RESULTS LIST = ITEM
        ["Properties"] - dictionary of properties for location
            ["Name"] - unique name of location
            ["Xcoord"] - optional x position (float)
            ["Ycoord"] - optional y position (float)
        ["Contents"] - dictionary of elements/values
        FOR EACH ENTRY IN THE CONTENTS DICTIONARY
            ["Element"] - Element symbol is the key, follows dictionary with the following entries
                ["Value"] - concentration (float)
                ["Units"] - concentration units
                ["Uncertainty"] - error bar on value

"""

    
    
class ConcentrationItem:
    def __init__(self,name,xc=None,yc=None):
        self.item={}
        self.item["Properties"]={}
        self.item["Properties"]["Name"]=name
        self.item["Properties"]["Xcoord"]=xc
        self.item["Properties"]["Ycoord"]=yc
        self.item["Contents"]=sortedcontainers.SortedDict(mucal.name_z)
    
class ConcentrationStandardData:
    def __init__(self,name):
        self.data={}
        
        properties={}
        properties['Name']=name
        
        self.data['Properties']=properties
        results=[]
        self.data['Results']=results
        
        self.stdPropLabels = ['Description','Matrix','Name']
        self.itemPropLabels = ['Name','Xcoord','Ycoord']
        self.contentLabels = ['Element','Value','Units','Uncertainty']
        
    def setStdPValue(self,label,value):
        if label in self.stdPropLabels:
            self.data['Properties'][label]=value
        else:
            raise Exception("Standard property "+str(label)+" invalid")
    
    def setItemPValue(self,index,label,value):
        if label not in self.itemPropLabels:
            raise Exception("Item property "+str(label)+" invalid")
        try:
            it = self.data['Results'][index]
        except IndexError:
            raise Exception("Item position "+str(index)+" invalid")
        self.data['Results'][index]['Properties'][label]=value
    
    def setContentValue(self,index,element,label,value):
        if label not in self.contentLabels:
            raise Exception("Content property "+str(label)+" invalid")
        try:
            it = self.data['Results'][index]
        except IndexError:
            raise Exception("Item position "+str(index)+" invalid")
        if element not in it["Contents"].keys():
            raise Exception("Element "+str(element)+" not in standard")            
        self.data['Results'][index]["Contents"][element][label]=value
    
    def addElement(self,index,element,value,units,uncert):
        try:
            it = self.data['Results'][index]
        except IndexError:
            raise Exception("Item position "+str(index)+" invalid")
        cont = {}
        cont["Value"]=float(value)
        cont["Units"]=units
        cont["Uncertainty"]=uncert
        cont["Element"]=element
        self.data['Results'][index]["Contents"][element]=cont
        
    def addItem(self,name,xc=None,yc=None):
        item=ConcentrationItem(name,xc,yc)
        self.data['Results'].append(item)
        return len(self.data['Results'])-1            
        
    def ImportItemFromIolite(self,fn,addraw=False):
        fid = open(fn,"r")
        tf = fid.read()
        fid.close()
        indata = json.loads(tf)
 
        if addraw:
            #parse iolite file...
            index = self.addItem(indata['Properties']['Name'])
            for res in indata['Results']:
                self.addElement(index,res['Name'],res['Value'],res['Units'],res['Uncertainty'])
        return indata
    
    def LoadFromJSON(self,fn):
        fid= open(fn,"r")
        tf = fid.read()
        fid.close()
        self.data=json.loads(tf)
        
    def SavetoJSON(self,fn):
        fid= open(fn,"w")
        rd = json.dumps(self.data)
        fid.write(rd)
        fid.close()
    
    def getItem(self,index):
        return self.data["Results"][index]
    
    def getElement(self,index,ele):
        return self.data['Results'][index]["Contents"][ele]


class ConcentrationElementWidget:
    def __init__(self,mf,callback):
        f=tkinter.Frame(mf,background='#d4d0c8')
        f.pack(side=tkinter.TOP,padx=2,pady=2)
        self.callback=callback
        self.rootf=f
        self.name=''
        self.namelab=tkinter.Label(f,text='Name: ',width=10,background='#d4d0c8')
        self.value=Pmw.EntryField(f,labelpos='w',label_text='Value: ',validate='real',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.units=Pmw.EntryField(f,labelpos='w',label_text='Units: ',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.uncert=Pmw.EntryField(f,labelpos='w',label_text='Uncert: ',validate='real',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.namelab.pack(side=tkinter.LEFT,padx=5,pady=2)
        self.value.pack(side=tkinter.LEFT,padx=5,pady=2)
        self.uncert.pack(side=tkinter.LEFT,padx=5,pady=2)  
        self.units.pack(side=tkinter.LEFT,padx=5,pady=2)   
        b=PmwTtkButtonBox.PmwTtkButtonBox(f,hull_background='#d4d0c8')
        b.add('X',command=self.deleElement,style='RED.TButton',width=5)
        b.pack(side=tkinter.LEFT,padx=5,pady=2)
        
    def updatename(self,name=None):
        if name is not None:
            self.name=name
        self.namelab.config(text="Name: "+str(self.name))
        
    def set(self,ele,value,uncert,units):
        self.name=ele
        self.updatename()
        self.value.setvalue(value)
        self.uncert.setvalue(uncert)
        self.units.setvalue(units)
        
        
    def setfromDict(self,d):
        if "Element" in d:       
            self.name=d["Element"]
        elif "Name" in d:
            self.name=d["Name"]
        else:
            self.name='H'
        self.updatename()
        self.value.setvalue(d["Value"])
        self.uncert.setvalue(d["Uncertainty"])
        self.units.setvalue(d["Units"])  
        
    def gettoDict(self,d):
        if self.isValid:
            d["Element"]=self.name
            d["Value"]=float(self.value.getvalue())
            d["Uncertainty"]=float(self.uncert.getvalue())
            d["Units"]=self.units.getvalue()
        else:
            print ('invalid entries for element - '+str(self.name.getvalue()))

    def isValid(self):
        #if self.name.getvalue() == "" : return False
        if not self.value.valid() : return False
        if not self.uncert.valid() : return False
        if self.units.getvalue() == "" : return False
        return True          
        
    def getDict(self):
        d={}
        if self.isValid():  
            self.gettoDict(d)
        else:
            print ('invalid entries for element - '+str(self.name.getvalue()))
        return d
    
    def deleElement(self):
        self.callback(self.name)
        self.rootf.destroy()
        

class ConcentrationItemWidgetEmpty:
    def __init__(self,mf,name,cb):
        self.mf=mf
        self.name=name
        self.callback=cb
        self.makewid(mf)
    
    def makewid(self,mf):
        grp=Pmw.Group(mf,tag_text=self.name,hull_background='#d4d0c8',tag_background='#d4d0c8',ring_background='#d4d0c8')
        grp.interior().configure(background='#d4d0c8')
        grp.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')
        #coords?
        f=tkinter.Frame(grp.interior())
        f.pack(side=tkinter.TOP, anchor=tkinter.W, padx=2)
        self.xc=Pmw.EntryField(f,labelpos='w',label_text='Xcoord: ',validate='real',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.yc=Pmw.EntryField(f,labelpos='w',label_text='Ycoord: ',validate='real',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.xc.pack(side=tkinter.LEFT,padx=5,pady=2)  
        self.yc.pack(side=tkinter.LEFT,padx=5,pady=2)      
        b=PmwTtkButtonBox.PmwTtkButtonBox(f,hull_background='#d4d0c8')
        b.add('+',command=self.addElement,style='GREEN.TButton',width=5)
        b.add('X',command=self.remove,style='RED.TButton',width=5)
        b.pack(side=tkinter.LEFT,padx=8,pady=2)
        self.grp=grp
        
        self.elements=sortedcontainers.SortedDict(mucal.name_z)
        
 
    def addElement(self):
        #get elemenet name?
        self.elementdialog=Pmw.SelectionDialog(self.mf,title="Element Selection",buttons=('OK','Cancel'),defaultbutton='OK',
                                                   scrolledlist_labelpos='n',label_text='Element',scrolledlist_items=mucal.esym,
                                                   command=self.finelements)
        self.elementdialog.component('scrolledlist').component('listbox').configure(selectmode=tkinter.EXTENDED)

    def finelements(self,result):
        
        choice=self.elementdialog.getcurselection()
        self.elementdialog.withdraw()
        if result=='Cancel':
            return
        for e in choice:
        
            ew = ConcentrationElementWidget(self.grp.interior(),self.killelement)
            ew.updatename(e)
            self.elements[e]=ew
    
    def killelement(self,name):
        self.elements.pop(name)
        
 
    #add getters/setters?
    def gettoDict(self):
        arg={}
        if self.xc.valid():
            arg['xc']=self.xc.getvalue()
        else:
            arg['xc']=None
        if self.yc.valid():
            arg['yc']=self.yc.getvalue()
        else:
            arg['yc']=None
        
        item=ConcentrationItem(self.name,**arg)
        for e in self.elements.keys():
            ed = self.elements[e].getDict()
            if ed == {}: continue
            item.item['Contents'][e]=ed
            
        return item.item
    
    def remove(self):
        self.callback(self)
        self.grp.destroy()
        
        
class ConcentrationItemWidgetFromDict(ConcentrationItemWidgetEmpty):
    def __init__(self,mf,item,cb):
        self.mf=mf
        self.callback=cb
        self.name=item["Properties"]["Name"]
        self.makewid(mf)
        
        #set coords
        if item["Properties"]["Xcoord"] is not None:
            self.xc.setvalue(item["Properties"]["Xcoord"])
        if item["Properties"]["Ycoord"] is not None:
            self.yc.setvalue(item["Properties"]["Ycoord"])

        #add contents
        for e in item["Contents"].keys():
            ew = ConcentrationElementWidget(self.grp.interior(),self.killelement)
            ew.setfromDict(item["Contents"][e])
            self.elements[e]=ew
        

class ConcentrationStandardWidgetEmpty:
    def __init__(self,mf,name):
        self.name=name
        self.standard = ConcentrationStandardData(name)
        
        self.makewid(mf)
        
    def makewid(self,mf):
        grp=Pmw.Group(mf,tag_text=self.name,hull_background='#d4d0c8',tag_background='#d4d0c8',ring_background='#d4d0c8')
        grp.interior().configure(background='#d4d0c8')
        grp.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')
        #properties?
        f=Pmw.Group(grp.interior(),tag_text='Properties',hull_background='#d4d0c8',tag_background='#d4d0c8',ring_background='#d4d0c8')
        f.interior().configure(background='#d4d0c8')
        f.pack(side=tkinter.TOP, anchor=tkinter.W, padx=2)
        self.matrix=Pmw.EntryField(f.interior(),labelpos='w',label_text='Matrix: ',entry_width=20,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.description=Pmw.EntryField(f.interior(),labelpos='w',label_text='Description: ',entry_width=40,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.matrix.pack(side=tkinter.TOP,padx=5,pady=2,anchor='w')  
        self.description.pack(side=tkinter.TOP,padx=5,pady=2,anchor='w')           
        Pmw.alignlabels([self.matrix,self.description])

        self.grp=grp
        self.results=[]
        
    def remove(self):  #removing entire standard...
        self.standard=None
        self.grp.destroy()

    def removeItem(self,item):
        #bookkeeping...
        self.results.pop(self.results.index(item))

    def updateStandard(self):
        #update standard data structure from inputs...
        self.standard.setStdPValue('Description',self.description.getvalue())
        self.standard.setStdPValue('Matrix',self.matrix.getvalue())
        #iterate through items
        self.standard.data['Results']=[]
        for it in self.results:
            self.standard.data['Results'].append(it.gettoDict())
        print ('complete update')
            
    
class ConcentrationStandardWidgetFromFile(ConcentrationStandardWidgetEmpty):
    def __init__(self,mf,fn):
        self.mf=mf
        
        self.standard = ConcentrationStandardData("")
        self.standard.LoadFromJSON(fn)
               
        self.name=self.standard.data["Properties"]["Name"]
        
        self.makewid(mf)

        #set props
        self.matrix.setvalue(self.standard.data["Properties"]["Matrix"])
        self.description.setvalue(self.standard.data["Properties"]["Description"])
        
        #add items...
        for i in self.standard.data["Results"]:
            it = ConcentrationItemWidgetFromDict(self.grp.interior(),i,self.removeItem)
            self.results.append(it)
        

class ConcStdParams:
    def __init__(self, filedir, status):
        self.filedir=filedir
        self.status=status

class ConcentrationStandardWindow(MasterClass):
    def _create(self):
        #make window
        self.calib = None
        
        self.win=Pmw.MegaToplevel(self.imgwin)
        self.win.title('Concentration Standard Editor')
        self.win.userdeletefunc(func=self.kill)
        h=self.win.interior()   
        
        j=Pmw.ScrolledFrame(h,hull_width=750,hull_height=750,usehullsize=1,vertflex='expand',horizflex='expand')
        j.interior().configure(background='#d4d0c8')
        j.pack(side=tkinter.TOP)
               
        self.sframe = tkinter.Frame(j.interior(), relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
        self.sframe.pack(side=tkinter.TOP,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
        
        w=15
        bb=PmwTtkButtonBox.PmwTtkButtonBox(h,labelpos='n',label_text='File Actions:',orient='horizontal',pady=3,padx=5,frame_background='#d4d0c8',hull_background='#d4d0c8',label_background='#d4d0c8')
        bb.add('New Standard',command=self.newConfig,style='SBLUE.TButton',width=w)
        bb.add('Load Standard',command=self.loadConfig,style='NAVY.TButton',width=w)
        bb.add('Save Standard',command=self.saveConfig,style='GREEN.TButton',width=w)
        bb.pack(side=tkinter.TOP,fill='both',padx=2,pady=5)
        
        
    def newConfig(self):
        #get name
        stdname=tkinter.simpledialog.askstring(title='New Calibration File',prompt='Enter the name for the calibrant',initialvalue='')
        if stdname == '' or stdname is None:
            print ('canceled')
            return

        if self.calib is not None:
            #delete
            self.calib.remove()
        else:
            self.itemButtons()

        self.calib = ConcentrationStandardWidgetEmpty(self.sframe,stdname)

        
    def itemButtons(self):
        #create new widgets:
        w=15
        bb=PmwTtkButtonBox.PmwTtkButtonBox(self.sframe,labelpos='nw',label_text='Actions:',orient='horizontal',pady=3,padx=5,frame_background='#d4d0c8',hull_background='#d4d0c8',label_background='#d4d0c8')
        bb.add('Add Item',command=self.addItem,style='SBLUE.TButton',width=w)
        bb.add('Import Item',command=self.importItem,style='MBLUE.TButton',width=w)
        bb.pack(side=tkinter.BOTTOM,fill='both',padx=2,pady=5)
    
    def loadConfig(self):
        #get file
        infile=globalfuncs.ask_for_file([("JSON Calibration files","*.json"),("all files","*")],self.ps.filedir.get(),multi=False)
        if infile == '' or infile is None:
            print ('canceled')
            globalfuncs.setstatus(self.ps.status,"No calibration file defined...")
            return
        
        if self.calib is not None:
            #delete
            self.calib.remove()
        else:
            self.itemButtons()
            
        self.calib = ConcentrationStandardWidgetFromFile(self.sframe,infile)
        
    def saveConfig(self):
        if self.calib is None:
            print('No data to save')
            globalfuncs.setstatus(self.ps.status,'No data to save')
            return               
        #get file name to save
        fn=self.calib.standard.data["Properties"]["Name"]+".json"
        fn=globalfuncs.ask_save_file(fn,self.ps.filedir.get())
        if fn=='':
            print('Save cancelled')
            globalfuncs.setstatus(self.ps.status,'Save cancelled')
            return   
        if os.path.splitext(fn)[1]!='.json':
            fn=fn+".json"
        #update info in calib....
        self.calib.updateStandard()
        self.calib.standard.SavetoJSON(fn)
        globalfuncs.setstatus(self.ps.status,'Calibration file '+fn+' saved')
    
    def addItem(self):
        #get name
        itname=tkinter.simpledialog.askstring(title='New Item',prompt='Enter the name for the item',initialvalue='')
        if itname == '' or itname is None:
            print ('canceled')
            return
        
        #add items...
        it = ConcentrationItemWidgetEmpty(self.calib.grp.interior(),itname,self.calib.removeItem)
        self.calib.results.append(it)
    
    def importItem(self):
        #get file
        infile=globalfuncs.ask_for_file([("JSON Calibration files","*.json"),("all files","*")],self.ps.filedir.get(),multi=False)
        if infile == '' or infile is None:
            print ('canceled')
            globalfuncs.setstatus(self.ps.status,"No calibration file defined...")
            return

        nid = self.calib.standard.ImportItemFromIolite(infile)

        #make items...
        it = ConcentrationItemWidgetEmpty(self.calib.grp.interior(),nid['Properties']['Name'],self.calib.removeItem)
        #add elements
        for e in nid['Results']:
            ew = ConcentrationElementWidget(it.grp.interior(),it.killelement)
            ew.setfromDict(e)
            it.elements[e['Name']]=ew            
        
        self.calib.results.append(it)        
        
        