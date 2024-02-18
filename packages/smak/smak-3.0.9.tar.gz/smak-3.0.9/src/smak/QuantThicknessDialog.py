# -*- coding: utf-8 -*-
"""
Created on Thu Apr 07 11:45:25 2016

@author: samwebb
"""

import os
import os.path
import string
import sys
import tkinter


#third party
import Pmw

#local
import pyMcaParamGUI as pypg
import pyMcaMaterials

class quantthickfield:
    def __init__(self,name,master):
        self.name=name
        self.master=master
        w=15
        px=3
        f=tkinter.Frame(master,background="#d4d0c8")
        #channel name
        self.chname=Pmw.EntryField(f,entry_width=w,hull_background='#d4d0c8')
        self.chname.pack(side=tkinter.LEFT,padx=px)
        self.chname.setvalue(name)
        self.chname.component('entry').configure(state=tkinter.DISABLED)
        #length
        self.energy=Pmw.EntryField(f,entry_width=w,validate='real',hull_background='#d4d0c8')
        self.energy.pack(side=tkinter.LEFT,padx=px)        
        f.pack(side=tkinter.TOP,padx=2,pady=2)

class QuantThickDialog:
    def __init__(self,master,callback,chanlist,defenergy,chanDict=None):

        self.chanDict=chanDict
        self.corType = None

        if getattr(sys, 'frozen', False):
            path = os.path.dirname(sys.executable)
            if sys.platform=='darwin':
                if 'MacOS' in path: path = path.replace('MacOS','Resources')
        elif __file__:
            path = os.path.dirname(__file__)        
        path=path+os.sep+"pyMcaConfigs"+os.sep        
        self.materialDict=pyMcaMaterials.Library(path+"defaultMaterials.mfg") 
                       
        #main thickness dialog
        self.dialog=Pmw.Dialog(master,title="Quantitative Thickness Correction",buttons=('Apply','Cancel'),
                                         command=callback)
        h=self.dialog.interior()
        h.configure(background="#d4d0c8")
        
        nb=Pmw.TtkNoteBook(h)
        if sys.platform == 'win32':
            nb.configure(hull_background="SystemButtonFace")
        else:
            nb.configure(hull_background='#d4d0c8')
        nb.recolorborders()        
        nb.pack(fill="both",expand=1)        
        
        insd=nb.add('Main',page_background='#d4d0c8')
        
        inter=tkinter.Frame(insd,bd=2,relief=tkinter.SUNKEN,background="#d4d0c8")
        inter.pack(side=tkinter.TOP,expand=1,fill='both')
        #material properties
        g=Pmw.Group(inter,tag_text='Calculation Properties',tag_background='#d4d0c8',ring_background='#d4d0c8',hull_background='#d4d0c8')
        g.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')
        g.interior().configure(background='#d4d0c8')
        self.qtcorEnergy=Pmw.EntryField(g.interior(),labelpos='w',label_text='Excitation Energy (eV): ',validate='real',entry_width=10,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.qtcorEnergy.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)        
        self.qtcorEnergy.setvalue(defenergy)

        self.qtfinalthick=Pmw.RadioSelect(g.interior(),buttontype='checkbutton',labelpos='w',hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        self.qtfinalthick.add('Form volumetric units? ',background='#d4d0c8')
        self.qtfinalthick.pack(side=tkinter.TOP,fill='both')   

        #channel properties
        w=12
        px=3
        f=tkinter.Frame(g.interior(),background='#d4d0c8')
        for t in ['Chan Name',' Emission (eV)']:
            if len(t.split())>2: w=20
            l=tkinter.Label(f,text=t,width=w,background='#d4d0c8')
            l.pack(side=tkinter.LEFT,padx=px,fill=tkinter.X,expand=1)
        f.pack(side=tkinter.TOP,padx=2,pady=2)
        self.quantThicklist=[]
        for gch in chanlist:
            self.quantThicklist.append(quantthickfield(gch,g.interior()))#need the class here...

        #material properties        

        q2=tkinter.Frame(inter,bd=2,background="#d4d0c8")
        q2.pack(side=tkinter.TOP,expand=1,fill='both')
        
        self.matrixType = Pmw.RadioSelect(q2, labelpos = 'w', buttontype='radiobutton', command=self.matrixSelect, orient='horizontal', label_text = 'Matrix Type:', hull_background='#d4d0c8',frame_background='#d4d0c8',label_background='#d4d0c8')
        for text in ('Single','Dynamic'):
            self.matrixType.add(text,background='#d4d0c8')
        self.matrixType.pack(side=tkinter.TOP,padx=2,anchor=tkinter.W)
        #needs to call active/disabling callback
        
        fr = tkinter.Frame(inter, background='#d4d0c8')
        fr.pack(side=tkinter.TOP,fill='both',expand=1)
        
        #channel to dynamically allocate attenuators
        if self.chanDict==None:
            self.chanDict={'ChA':[2011,0],'ChB':[10,1],'ChC':[3,1],'ChD':[4055,0]}
        self.chanList=[]
        for i in list(self.chanDict.keys()): 
            if self.chanDict[i][1]==1: self.chanList.append(i)
        self.dynamicChan=pypg.myComboBox(fr,label_text='Data Channel for Dynamic Correction',selectioncommand=self.channelSelect,labelpos=tkinter.N,scrolledlist_items=self.chanList,listheight=100,history=0,hull_background='#d4d0c8',label_background='#d4d0c8')
        if len(self.chanList)>0: self.dynamicChan.selectitem(self.chanList[0])
        self.dynamicChan.pack(side=tkinter.TOP,padx=4,pady=8,anchor=tkinter.W)
        
        self.matrixAttenuators={}
                
        hwv=500
        j=Pmw.ScrolledFrame(fr,hull_width=hwv,hull_height=300,usehullsize=1,vertflex='expand',horizflex='expand')
        j.interior().configure(background='#d4d0c8')
        j.pack(side=tkinter.TOP,pady=2)
        self.Attint=tkinter.Frame(j.interior(),bd=2,relief=tkinter.SUNKEN,background='#d4d0c8')
        self.Attint.pack(side=tkinter.TOP,fill='both',expand='y')

        h=pypg.Attenuator(self.Attint,'','',header=True,interior=True)
        self.matrixType.invoke('Single')
        
        

            
            
        mateditorPage=nb.add('Materials',page_background='#d4d0c8')

        q3=tkinter.Frame(mateditorPage, relief=tkinter.GROOVE,bd=2, background='#d4d0c8')
        q3.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
         
        l=tkinter.Label(q3,text="Material Editor",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)

        w=20
        bb=Pmw.TtkButtonBox(q3,labelpos='n',label_text='Edit Options',orient='horizontal',padx=3,frame_background='#d4d0c8',hull_background='#d4d0c8',label_background='#d4d0c8')
        bb.add('New Material',style='LGREEN.TButton',width=w,command=self.newMaterial)
        bb.add('Save Material',style='GREEN.TButton',width=w,command=self.editSaveMaterial)
        bb.pack(side=tkinter.TOP,padx=5,pady=5,anchor=tkinter.W)        
        bb=Pmw.TtkButtonBox(q3,labelpos='n',label_text='Edit Options',orient='horizontal',padx=3,frame_background='#d4d0c8',hull_background='#d4d0c8',label_background='#d4d0c8')
        bb.add('Clear/Load Database',style='SBLUE.TButton',width=w,command=self.clearLoadMatDatabase)
        bb.add('Load into Database',style='NAVY.TButton',width=w,command=self.addtoMatDatabase)
        bb.add('Save Database',style='BROWN.TButton',width=w,command=self.saveMatDatabase)
        bb.pack(side=tkinter.TOP,padx=5,pady=5,anchor=tkinter.W)        

        self.ed_material=pypg.myComboBox(q3,label_text='Material Name:',selectioncommand=self.ed_materialSelect,labelpos=tkinter.W,scrolledlist_items=list(self.materialDict.materials.keys()),listheight=100,history=0,hull_background='#d4d0c8',label_background='#d4d0c8')
        if len(list(self.materialDict.materials.keys()))>0: self.ed_material.selectitem(list(self.materialDict.materials.keys())[0])
        self.ed_material.pack(side=tkinter.TOP,padx=4,pady=8,anchor=tkinter.W)       
        
        f=tkinter.Frame(q3, background='#d4d0c8')
        f.pack(side=tkinter.TOP,anchor=tkinter.W)
        
        fl=tkinter.Frame(f, background='#d4d0c8')
        fl.pack(side=tkinter.LEFT)
 
        self.ed_nummats=Pmw.Counter(fl,labelpos='w',label_text='Number of Compounds: ',datatype='numeric',entryfield_value=1,entry_width=20,hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8', entryfield_command=self.editNumCompounds, entryfield_validate = {'validator' : 'integer', 'min' : 1, 'max' : 50})
        self.ed_nummats.component('downarrow').bind(sequence='<Button-1>',func=self.editNumCompounds,add='+')
        self.ed_nummats.component('uparrow').bind(sequence='<Button-1>',func=self.editNumCompounds,add='+')
        self.ed_nummats.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)

        self.edCompounds=[]
                
        hwv=300
        j=Pmw.ScrolledFrame(fl,hull_width=hwv,hull_height=200,usehullsize=1,vertflex='expand',horizflex='expand')
        j.interior().configure(background='#d4d0c8')
        j.pack(side=tkinter.TOP,pady=2)
        self.edCompint=tkinter.Frame(j.interior(),bd=2,relief=tkinter.SUNKEN,background='#d4d0c8')
        self.edCompint.pack(side=tkinter.TOP,fill='both',expand='y')     

        h=pypg.Compound(self.edCompint,header=True)
        
        w=pypg.Compound(self.edCompint)
        self.edCompounds.append(w)
        
        
        fr=tkinter.Frame(f, background='#d4d0c8')
        fr.pack(side=tkinter.LEFT)
        
        self.ed_defdensity=Pmw.EntryField(fr,labelpos='w',label_text="Default Density: ",validate='real',entry_width=20,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.ed_defdensity.pack(side=tkinter.TOP,padx=2)
        self.ed_defthickness=Pmw.EntryField(fr,labelpos='w',label_text="Default Thickness: ",validate='real',entry_width=20,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.ed_defthickness.pack(side=tkinter.TOP,padx=2)                

        Pmw.alignlabels([self.ed_defdensity,self.ed_defthickness])
        
        self.ed_comment=Pmw.EntryField(q3,labelpos='w',label_text="Material Comment: ",entry_width=60,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.ed_comment.pack(side=tkinter.LEFT,padx=2)
        
        Pmw.alignlabels([self.ed_material,self.ed_comment,self.ed_nummats])


        nb.setnaturalsize()

    def activate(self):
        self.dialog.activate()
        
    def deactivate(self):
        self.dialog.deactivate()
        
      
    def editNumCompounds(self,*args):
        while int(self.ed_nummats.getvalue()) < len(self.edCompounds):
            self.edCompounds[-1].widget.destroy()
            self.edCompounds.pop()
            
        while int(self.ed_nummats.getvalue()) > len(self.edCompounds):
            w=pypg.Compound(self.edCompint)
            self.edCompounds.append(w)     
            
    def ed_materialSelect(self,sel):
        #clean up
        for i in range(len(self.edCompounds)):
            self.edCompounds[-1].widget.destroy()
            self.edCompounds.pop()    
        self.ed_defdensity.clear()
        self.ed_defthickness.clear()           
            
        #add back
        w=self.materialDict.materials[sel]
        if w.name=='--': return

        #print w.name,w.density,w.thickness
        #print w.compoundList
        #print w.compoundFraction

        self.ed_nummats.setvalue(len(w.compoundList))
        self.ed_nummats.invoke()

        #populate compounds
        for j in range(len(w.compoundList)):
            self.edCompounds[j].material.setvalue(w.compoundList[j])
            self.edCompounds[j].fraction.setvalue(w.compoundFraction[j])
            
        #populate values
        self.ed_defdensity.setvalue(float(w.density))
        self.ed_defthickness.setvalue(float(w.thickness))
        self.ed_comment.setvalue(w.comment)

    def reloadLists(self):
        self.ed_material._list.setlist(sorted(list(self.materialDict.materials.keys()),key=string.lower))
        for n in list(self.matrixAttenuators.values()):
            n.refresh(self.materialDict.materials)
        for o in list(self.attenuatorWidgets.values()):
            o.refresh(self.materialDict.materials)
        
    def newMaterial(self):
        new = pyMcaMaterials.MaterialItem()
        #JOY Q
        nn = tkinter.SimpleDialog.askstring('Material Properties','New Material Name: ',parent=self.master)        
        if nn=='':
            print('cancelled')
            return                    
        new.name=nn
        
        self.ed_comment.clear()
        self.ed_defdensity.clear()
        self.ed_defthickness.clear()
        for i in range(len(self.edCompounds)):
            self.edCompounds[-1].widget.destroy()
            self.edCompounds.pop()  
        self.ed_nummats.setvalue(1)
        self.ed_nummats.invoke()

        self.materialDict.materials[new.name]=new
        self.ed_material._list.setlist(sorted(list(self.materialDict.materials.keys()),key=string.lower))            
        self.ed_material.selectitem(new.name,setentry=1)

        
    def editSaveMaterial(self):
        if self.ed_material.getvalue()[0]=='--':
            print('null data')
            return
        new = pyMcaMaterials.MaterialItem()
        new.name=self.ed_material.getvalue()[0]
        new.comment=self.ed_comment.getvalue()
        new.density=float(self.ed_defdensity.getvalue())
        new.thickness=float(self.ed_defthickness.getvalue())
        for ms in self.edCompounds:
            new.compoundFraction.append(float(ms.fraction.getvalue()))
            new.compoundList.append(ms.material.getvalue())
            
        #print new.comment,new.name,new.density,new.thickness            
        self.materialDict.materials[new.name]=new
        self.reloadLists()        
    
    def clearLoadMatDatabase(self,reset=True):
        fty=[("Material Config Files","*.mfg"),("PyMCA Config Files","*.cfg"),("all files","*")]
        t=ask_for_file(fty,'')
        if t=='':
            print('load cancelled')
            return
        
        if reset: self.materialDict.reset()
        self.materialDict.load(nfn=t)       
        self.reloadLists()
        self.ed_material.selectitem('--',setentry=1)
    
    def addtoMatDatabase(self):
        self.clearLoadMatDatabase(reset=False)
    
    def saveMatDatabase(self):
        fn=ask_save_file('savedMaterials.mfg','')
        if fn=='':
            print('Save cancelled')
            return
        if os.path.splitext(fn)[1]=='':
            fn+fn+".mfg"
        self.materialDict.save(nfn=fn)            
        self.reloadLists()

    def channelSelect(self,sel):
        for w in list(self.matrixAttenuators.values()):
            w.widget.destroy()
        for i in range(self.chanDict[sel][0]):
            w = pypg.Attenuator(self.Attint,'Matrix '+str(i+1),default='--',interior=True,materialList=self.materialDict.materials)
            self.matrixAttenuators['Matrix '+str(i+1)]=w
                
    def matrixSelect(self,sel):
        if sel=='None':
            #disable channels and clear attenuators
            self.dynamicChan.disable()
            for w in list(self.matrixAttenuators.values()):
                w.widget.destroy()
            self.matrixAttenuators={}
            self.corType=None
        
        if sel=='Single':
            self.dynamicChan.disable()
            for w in list(self.matrixAttenuators.values()):
                w.widget.destroy()
            self.matrixAttenuators={}
            #add one back
            w = pypg.Attenuator(self.Attint,'Matrix 1',default='--',interior=True,materialList=self.materialDict.materials)
            self.matrixAttenuators['Matrix 1']=w
            self.corType="Single"
            
        if sel=='Dynamic':
            self.dynamicChan.enable()
            for w in list(self.matrixAttenuators.values()):
                w.widget.destroy()
            self.matrixAttenuators={}
            self.corType="Dynamic"
