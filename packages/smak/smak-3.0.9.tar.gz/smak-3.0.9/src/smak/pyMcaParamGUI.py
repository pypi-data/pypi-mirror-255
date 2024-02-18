# -*- coding: utf-8 -*-
"""
Created on Wed Mar 02 15:19:08 2016

@author: samwebb
"""
#standard
import decimal
from inspect import getsourcefile
import os
import os.path
import string
import sys
import tkinter
import tkinter.filedialog
import tkinter.simpledialog
from operator import itemgetter


#third party
import Pmw

#local
from globalfuncs import ask_for_file, ask_save_file
from PyMca5.PyMcaIO import ConfigDict as PyCD
from PyMca5.PyMcaPhysics.xrf import Elements as pEle
import PmwTtkButtonBox
import PmwTtkNoteBook
import pyMcaMaterials
import ScrollTree
import SortedCollection



########### Style
    
from tkinter.ttk import Button, Style
SMAKStyle=Style()
SMAKStyle.theme_use('default')



fz=15
SMAKStyle.configure("PTgoldenrod.TButton",foreground='black',background='goldenrod',font=('Arial',fz,'bold'))
SMAKStyle.configure("PTtan.TButton",foreground='black',background='tan',font=('Arial',fz,'bold'))
SMAKStyle.configure("PTorange.TButton",foreground='black',background='orange',font=('Arial',fz,'bold'))
SMAKStyle.configure("PTlight blue.TButton",foreground='black',background='light blue',font=('Arial',fz,'bold'))
SMAKStyle.configure("PTdark green.TButton",foreground='black',background='dark green',font=('Arial',fz,'bold'))
SMAKStyle.configure("PTrosy brown.TButton",foreground='black',background='rosy brown',font=('Arial',fz,'bold'))
SMAKStyle.configure("PTdark red.TButton",foreground='black',background='dark red',font=('Arial',fz,'bold'))

SMAKStyle.configure("PTgray.TButton",foreground='black',background='gray81',font=('Arial',fz,'bold'),relief='sunken')

SMAKStyle.configure("sPTgoldenrod.TButton",foreground='black',background='lightyellow',font=('Arial',fz,'bold'),relief='sunken')
SMAKStyle.configure("sPTtan.TButton",foreground='black',background='lightyellow',font=('Arial',fz,'bold'),relief='sunken')
SMAKStyle.configure("sPTorange.TButton",foreground='black',background='lightyellow',font=('Arial',fz,'bold'),relief='sunken')
SMAKStyle.configure("sPTlight blue.TButton",foreground='black',background='lightyellow',font=('Arial',fz,'bold'),relief='sunken')
SMAKStyle.configure("sPTdark green.TButton",foreground='black',background='lightyellow',font=('Arial',fz,'bold'),relief='sunken')
SMAKStyle.configure("sPTrosy brown.TButton",foreground='black',background='lightyellow',font=('Arial',fz,'bold'),relief='sunken')
SMAKStyle.configure("sPTdark red.TButton",foreground='black',background='lightyellow',font=('Arial',fz,'bold'),relief='sunken')


def stylecomp(s):
    if type(s)==type(('f','f')):
        st=' '.join(s)
    else:
        st=s
    return st

def sci_str(dec):
    dec = decimal.Decimal(dec)
    return ('{:.' + str(len(dec.normalize().as_tuple().digits) - 1) + 'E}').format(dec)

class myComboBox(Pmw.ComboBox):
    def disable(self):
        # Rebind things to my empty handler
        self.component('arrowbutton').bind('<1>',self.handler)
        self.component('arrowbutton').bind('<3>',self.handler)
        self.component('arrowbutton').bind('<Shift-3>',self.handler)
        self.component('entryfield_entry').configure(state='disabled',fg='grey')

    def enable(self):
        # bind the events back up to the original methods
        self.component('arrowbutton').bind('<1>',self._postList)
        self.component('arrowbutton').bind('<3>',self._next)
        self.component('arrowbutton').bind('<Shift-3>',self._previous)
        self.component('arrowbutton').configure(takefocus=1)
        self.component('entryfield_entry').configure(state='normal',fg='black')
        
    def handler(self,event):
        # so it doesn't propagate the event
        return('break')

class FitOptWidget:
    def __init__(self,master,label,w=10):
                
        f=tkinter.Frame(master, background='#d4d0c8')
        f.pack(side=tkinter.TOP, anchor=tkinter.W, padx=2)
        
        self.fix = Pmw.RadioSelect(f, labelpos = 'w', buttontype='checkbutton', orient='horizontal', label_text = label, hull_background='#d4d0c8',frame_background='#d4d0c8',label_background='#d4d0c8')
        for text in ('Fix',):
            self.fix.add(text,background='#d4d0c8')
        self.fix.pack(side=tkinter.LEFT,padx=2,anchor=tkinter.W)


        self.value=Pmw.EntryField(f,labelpos='w',label_text="value: ",validate='real',entry_width=w,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.value.pack(side=tkinter.LEFT,padx=2)
        self.error=Pmw.EntryField(f,labelpos='w',label_text='+/-',validate='real',entry_width=w,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.error.pack(side=tkinter.LEFT,padx=2)
        
    def getFix(self):
        if len(self.fix.getvalue())>0: return 1
        else: return 0
    
    def getValue(self,convert=False):
        if convert: return float(self.value.getvalue())/1000.0
        return self.value.getvalue()
        
    def getError(self,convert=False):
        if convert: return float(self.error.getvalue())/1000.0
        return self.error.getvalue()
        
    def setFix(self,value):
        if value == 1 or value==True: self.fix.setvalue(['Fix',])
        else: self.fix.setvalue([])
        
    def setValue(self,value,convert=False):
        if convert: self.value.setvalue(value*1000.0)
        else: self.value.setvalue(value)
        
    def setError(self,value,convert=False):
        if convert: self.error.setvalue(value*1000.0)
        else: self.error.setvalue(value)
  
class Compound:
    def __init__(self,master,header=False):
        
        if sys.platform=='darwin':
            w=10
        else:
            w=20
    
        f=tkinter.Frame(master, background='#d4d0c8')
        f.pack(side=tkinter.TOP, anchor=tkinter.NW, padx=2, pady=2, fill=tkinter.X)

        self.widget=f

        if not header:
            
            self.material=Pmw.EntryField(f,labelpos='e',label_text="",entry_width=w,hull_background='#d4d0c8',label_background='#d4d0c8')
            self.material.pack(side=tkinter.LEFT,padx=2)
            self.fraction=Pmw.EntryField(f,labelpos='e',label_text='',validate='real',entry_width=w,hull_background='#d4d0c8',label_background='#d4d0c8')
            self.fraction.pack(side=tkinter.LEFT,padx=2)

        else:

            self.material=tkinter.Label(f,text="Formula", background='#d4d0c8',width=18,anchor='w')
            self.material.pack(side=tkinter.LEFT,padx=2)
            self.fraction=tkinter.Label(f,text="Mass Fraction", background='#d4d0c8',width=15,anchor='w')
            self.fraction.pack(side=tkinter.LEFT,padx=2)
      
class Attenuator:
    def __init__(self,master,label,materialList={'--':None},default=None,header=False,interior=False):
        
        if sys.platform=='darwin':
            w=10
        else:
            w=20

        self.label = label
        self.default = default
        self.materialList=materialList
        
        f=tkinter.Frame(master, background='#d4d0c8')
        f.pack(side=tkinter.TOP, anchor=tkinter.NW, padx=2, pady=2, fill=tkinter.X)

        self.widget=f

        if not header:
        
            if not interior:
                self.use = Pmw.RadioSelect(f, labelpos = 'w', buttontype='checkbutton', orient='horizontal', label_text = label, hull_background='#d4d0c8',frame_background='#d4d0c8',label_background='#d4d0c8')
                for text in ('Use',):
                    self.use.add(text,background='#d4d0c8')
                self.use.pack(side=tkinter.LEFT,padx=2,anchor=tkinter.W)
            else:
                self.use=tkinter.Label(f,text=label, background='#d4d0c8',width=7,anchor='w')
                self.use.pack(side=tkinter.LEFT,fill=tkinter.X,padx=2)
                

            self.material=Pmw.ComboBox(f,label_text='',labelpos=tkinter.W,scrolledlist_items=sorted(list(materialList.keys()),key=str.lower),selectioncommand=self.selection,listheight=100,history=0,hull_background='#d4d0c8',label_background='#d4d0c8')
            if default==None or default not in list(materialList.keys()):
                self.material.selectitem(list(materialList.keys())[0])
            else:
                self.material.selectitem(default)                
            self.material.pack(side=tkinter.LEFT,fill=tkinter.X,padx=2)
    
            self.density=Pmw.EntryField(f,labelpos='e',label_text="",validate='real',entry_width=w,hull_background='#d4d0c8',label_background='#d4d0c8')
            self.density.pack(side=tkinter.LEFT,padx=2)
            self.thickness=Pmw.EntryField(f,labelpos='e',label_text='',validate='real',entry_width=w,hull_background='#d4d0c8',label_background='#d4d0c8')
            self.thickness.pack(side=tkinter.LEFT,padx=2)

        else:

            if not interior:
                self.use=tkinter.Label(f,text="Name", background='#d4d0c8',width=18,anchor='w')
                self.use.pack(side=tkinter.LEFT,fill=tkinter.X,padx=2)
            else:
                self.use=tkinter.Label(f,text="Name", background='#d4d0c8',width=7,anchor='w')
                self.use.pack(side=tkinter.LEFT,fill=tkinter.X,padx=2)                
            self.material=tkinter.Label(f,text="Material", background='#d4d0c8',width=20,anchor='w')
            self.material.pack(side=tkinter.LEFT,padx=2)
            self.density=tkinter.Label(f,text="Density (g/cm3)", background='#d4d0c8',width=18,anchor='w')
            self.density.pack(side=tkinter.LEFT,padx=2)
            self.thickness=tkinter.Label(f,text="Thickness (cm)", background='#d4d0c8',width=15,anchor='w')
            self.thickness.pack(side=tkinter.LEFT,padx=2)
            
    def selection(self,sel):
        w=self.materialList[sel]
        if w.name=='--':
            self.density.clear()
            self.thickness.clear()
            return
        self.density.setvalue(float(w.density))
        self.thickness.setvalue(float(w.thickness))
        
    def refresh(self,newList):
        self.materialList=newList
        self.material._list.setlist(sorted(list(newList.keys()),key=string.lower))
        
    def valid(self):
        if self.material.getvalue()[0]=='--': return False
        if not self.density.valid(): return False
        if not self.thickness.valid(): return False
        return True
       


class PyMcaParameterDialog:
    def __init__(self,master,energy=1,graphwid=None,closeCallBack=None,configFile=None,chanDict=None):

        self.master = master
        self.energy = energy
        self.graphwid = graphwid
        self.closeCallBack=closeCallBack
        self.configFile=configFile
        self.chanDict=chanDict
        
        self.atom=None
        self.atomDict={}
        self.parameterDict={}
        
        if getattr(sys, 'frozen', False):
            path = os.path.dirname(sys.executable)
            if sys.platform=='darwin':
                if 'MacOS' in path: path = path.replace('MacOS','Resources')
        elif __file__:
            path = os.path.dirname(__file__)
        
        #path=os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))+os.sep+"pyMcaConfigs"+os.sep
        path=path+os.sep+"pyMcaConfigs"+os.sep
        
        self.materialDict=pyMcaMaterials.Library(path+"defaultMaterials.mfg")     

        self.pyParamWin=Pmw.MegaToplevel(self.master)
        self.pyParamWin.title('PyMCA Parameter Configuration')
        self.pyParamWin.userdeletefunc(func=self.killpyParamWin)           
        h=self.pyParamWin.interior()
        h.configure(background='#d4d0c8')

        if sys.platform=='darwin':
            #mac specific layout as notebook has weird behavior?
            
            hh=Pmw.ScrolledFrame(h,usehullsize=1,vertflex='fixed',horizflex='fixed',
                                 hscrollmode='static',vscrollmode='static',
                                 hull_width=1200,hull_height=1100)
            hh.interior().configure(background='#d4d0c8')
            hh.pack(side=tkinter.TOP,pady=2)
            ii=hh.interior()
            ##ii=h
            
            topCon = tkinter.Frame(ii, background='#d4d0c8')
            topCon.pack(side=tkinter.TOP,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            peakPage = tkinter.Frame(topCon, relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
            peakPage.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            attenuatorPage = tkinter.Frame(topCon, relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
            attenuatorPage.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            
            botCon = tkinter.Frame(ii, background='#d4d0c8')
            botCon.pack(side=tkinter.TOP,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            paramPage = tkinter.Frame(botCon, relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
            paramPage.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            mateditorPage = tkinter.Frame(botCon, relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
            mateditorPage.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)

            l=tkinter.Label(peakPage,text="Peaks",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)        
            l=tkinter.Label(attenuatorPage,text="Attenuators",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)        
            l=tkinter.Label(paramPage,text="Parameters",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)        
            l=tkinter.Label(mateditorPage,text="Materials",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)
            
            w=10
        

        else:
            #windoze...
        
            pymcanb=PmwTtkNoteBook.PmwTtkNoteBook(h,raisecommand=self.raiseme)
            if sys.platform == 'win32':
                pymcanb.configure(hull_background="SystemButtonFace")
            else:
                pymcanb.configure(hull_background='#d4d0c8')
            pymcanb.recolorborders()        
            pymcanb.pack(fill="both",expand=1)
 
            peakPage=pymcanb.add('Peaks',page_background='#d4d0c8')
            paramPage=pymcanb.add('Parameters',page_background='#d4d0c8')
            attenuatorPage=pymcanb.add('Attenuators',page_background='#d4d0c8')
            mateditorPage=pymcanb.add('Materials',page_background='#d4d0c8')
            
            w=20
                                    
#        graphPage=pymcanb.add('Graph',page_background='#d4d0c8')
#        g1=tkinter.Frame(graphPage, relief=tkinter.GROOVE,bd=2, background='#d4d0c8')
#        g1.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
#        self.MCAtracescalevar=StringVar()
#        self.MCAtracescalevar.set('Linear')
#        self.MCAgraph=MyGraph(g1,whsize=(6.5,3),tool=1,graphpos=[[.15,.1],[.9,.9]])
#        g2=tkinter.Frame(graphPage, relief=tkinter.GROOVE,bd=2, background='#d4d0c8')
#        g2.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
#        l=tkinter.Label(g2,text="Fitting",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
#        l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)
#        w=15
#        bb=Pmw.TtkButtonBox(g2,labelpos='n',label_text='Fit Actions:',orient='vertical',pady=3,padx=5,frame_background='#d4d0c8',hull_background='#d4d0c8',label_background='#d4d0c8')
#        bb.add('Set Config',command=self.saveConfig,style='NAVY.TButton',width=w)
#        bb.add('Fit Current',command=self.testFit,style='NAVY.TButton',width=w)
#        bb.add('Fit All MCA',command=self.doCallbackFit,style='GREEN.TButton',width=w)
#        bb.pack(side=tkinter.TOP,fill='both',padx=2,pady=5)

        
        #peakPage=pymcanb.add('Peaks',page_background='#d4d0c8')
        p1=tkinter.Frame(peakPage, relief=tkinter.GROOVE,bd=2, background='#d4d0c8')
        p1.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
        
        self.beamEnergy = Pmw.EntryField(p1,label_text="Incident Energy (eV):",labelpos=tkinter.W,validate='real',entry_width=10,value=self.energy,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.beamEnergy.pack(side=tkinter.TOP,padx=2,pady=2)
        #periodic table
        #define elements 1=noble, 2=alkali, 3=pseudo, 4=non, 5=metal, 6=lanth, 7=act
        self.elist={'H':(1,0,1),'He':(2,0,1),
            'Li':(3,1,2),'Be':(4,1,2),'B':(5,1,3),'C':(6,1,4),'N':(7,1,4),'O':(8,1,4),'F':(9,1,4),'Ne':(10,1,1),
            'Na':(11,2,2),'Mg':(12,2,2),'Al':(13,2,5),'Si':(14,2,3),'P':(15,2,4),'S':(16,2,4),'Cl':(17,2,4),'Ar':(18,2,1),
            'K':(19,3,2),'Ca':(20,3,2),'Sc':(21,3,5),'Ti':(22,3,5),'V':(23,3,5),'Cr':(24,3,5),'Mn':(25,3,5),'Fe':(26,3,5),
            'Co':(27,3,5),'Ni':(28,3,5),'Cu':(29,3,5),'Zn':(30,3,5),'Ga':(31,3,5),'Ge':(32,3,3),'As':(33,3,3),'Se':(34,3,4),'Br':(35,3,4),'Kr':(36,3,1),
            'Rb':(37,4,2),'Sr':(38,4,2),'Y':(39,4,5),'Zr':(40,4,5),'Nb':(41,4,5),'Mo':(42,4,5),'Tc':(43,4,5),'Ru':(44,4,5),'Rh':(45,4,5),
            'Pd':(46,4,5),'Ag':(47,4,5),'Cd':(48,4,5),'In':(49,4,5),'Sn':(50,4,5),'Sb':(51,4,3),'Te':(52,4,3),'I':(53,4,4),'Xe':(54,4,1),
            'Cs':(55,5,2),'Ba':(56,5,2),'La':(57,8,6),'Ce':(58,8,6),'Pr':(59,8,6),'Nd':(60,8,6),'Pm':(61,8,6),'Sm':(62,8,6),'Eu':(63,8,6),
            'Gd':(64,8,6),'Tb':(65,8,6),'Dy':(66,8,6),'Ho':(67,8,6),'Er':(68,8,6),'Tm':(69,8,6),'Yb':(70,8,6),'Lu':(71,5,5),'Hf':(72,5,5),
            'Ta':(73,5,5),'W':(74,5,5),'Re':(75,5,5),'Os':(76,5,5),'Ir':(77,5,5),'Pt':(78,5,5),'Au':(79,5,5),'Hg':(80,5,5),'Tl':(81,5,5),
            'Pb':(82,5,5),'Bi':(83,5,5),'Po':(84,5,5),'At':(85,5,3),'Rn':(86,5,1),'Fr':(87,6,2),'Ra':(88,6,2),'Ac':(89,9,7),'Th':(90,9,7),
            'Pa':(91,9,7),'U':(92,9,7),'Np':(93,9,7),'Pu':(94,9,7),'Am':(95,9,7),'Cm':(96,9,7),'Bk':(97,9,7),'Cf':(98,9,7),'Es':(99,9,7),
            'Fm':(100,9,7),'Md':(101,9,7),'No':(102,9,7),'Lr':(103,6,5),'Rf':(104,6,5),'Db':(105,6,5),'Sg':(106,6,5),'Bh':(107,6,5),'Hs':(108,6,5),'Mt':(109,6,5)}        
        table=tkinter.Frame(p1,relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
        table.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        for en in list(self.elist.keys()):
            eprop=self.elist[en]
            cp=eprop[0]
            if eprop[0]==1:
                cp=0
            elif eprop[0]==2:
                cp=17
            elif 3<=eprop[0]<=4:
                cp=cp-3
            elif 5<=eprop[0]<=10:
                cp=cp+7
            elif 11<=eprop[0]<=12:
                cp=cp-11
            elif 13<=eprop[0]<=18:
                cp=cp-1
            elif 19<=eprop[0]<=36:
                cp=cp-19
            elif 37<=eprop[0]<=54:
                cp=cp-37
            elif 55<=eprop[0]<=70:
                cp=cp-55
            elif 71<=eprop[0]<=86:
                cp=cp-69
            elif 87<=eprop[0]<=102:
                cp=cp-87
            elif 103<=eprop[0]<=118:
                cp=cp-101
            self.addelement(table,en,eprop[1],cp,eprop[2])
        self.activeElement = None
        
        #edge selection 
        f=tkinter.Frame(p1,relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
        f.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)  
        l=tkinter.Label(f,text="Peak Selections",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)

        fl=tkinter.Frame(f, background='#d4d0c8')
        fl.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=1)
        w=15
        bb=PmwTtkButtonBox.PmwTtkButtonBox(fl,labelpos='n',label_text='Peak Line Selection:',orient='horizontal',padx=3,frame_background='#d4d0c8',hull_background='#d4d0c8',label_background='#d4d0c8')
        for line in ['K','L','M']:
            b=bb.add(line,style='SBLUE.TButton',width=w)
            b.bind("<Button-1>",self.setPeakLine)
        bb.pack(side=tkinter.TOP,fill='both',padx=2,pady=5)        

        fr=tkinter.Frame(f, background='#d4d0c8')
        fr.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=1)
        #clear buttons
        bb=PmwTtkButtonBox.PmwTtkButtonBox(fr,labelpos='n',label_text='Peak Actions:',orient='horizontal',padx=3,frame_background='#d4d0c8',hull_background='#d4d0c8',label_background='#d4d0c8')
        bb.add('Clear Selected',command=self.clearCurPeakLine,style='ORANGE.TButton',width=w)
        bb.add('Clear All',command=self.clearAllPeakLine,style='FIREB.TButton',width=w)
        bb.pack(side=tkinter.TOP,fill='both',padx=2,pady=5)  
        
        #list of peaks
        p2=tkinter.Frame(peakPage, relief=tkinter.GROOVE,bd=2, background='#d4d0c8')
        p2.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
        l=tkinter.Label(p2,text="Active Peaks",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)
        self.peaklist=ScrollTree.ScrolledTreeViewBox(p2,width=100)
        self.peaklist.setMode('browse')
        self.peaklist.setColNames(("Peak",))
        self.peaklist.setColWidthAnchor([10,'w'])
        self.peaklist.setSelect(self.choosePeak)        
        self.peaklist.pack(side=tkinter.TOP,fill=tkinter.BOTH,expand=1,padx=2,pady=2)
        self.peaks=SortedCollection.SortedCollection(key=itemgetter(1))
        self.peaksus=[]

        #parameter page
        #paramPage=pymcanb.add('Parameters',page_background='#d4d0c8')
        q1=tkinter.Frame(paramPage, relief=tkinter.GROOVE,bd=2, background='#d4d0c8')
        q1.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)

        q2=tkinter.Frame(paramPage, relief=tkinter.GROOVE,bd=2, background='#d4d0c8')
        q2.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)

        g1=Pmw.Group(q1,tag_text='Fitting Region',hull_background='#d4d0c8',tag_background='#d4d0c8',ring_background='#d4d0c8')
        g1.interior().configure(background='#d4d0c8')
        g1.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')

        self.fitregionxmin=Pmw.EntryField(g1.interior(),labelpos='w',label_text='Fit Min Bin: ',validate='integer',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.fitregionxmin.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)
        self.fitregionxmin.setvalue(0)
        self.fitregionxmax=Pmw.EntryField(g1.interior(),labelpos='w',label_text='Fit Max Bin: ',validate='integer',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.fitregionxmax.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)
        self.fitregionxmax.setvalue(2048)
        self.parameterDict['xmin']=[self.fitregionxmax,False]
        self.parameterDict['xmax']=[self.fitregionxmax,False]

        g1a=tkinter.Frame(g1.interior(),background='#d4d0c8')
        g1a.pack(side=tkinter.TOP,fill='both',expand=1)

        self.avgfilterVar=tkinter.IntVar()
        self.avgfilterVar.set(1)
        self.avgfilter=tkinter.Scale(g1a,label='Averge Kernel',background='#d4d0c8',variable=self.avgfilterVar,width=20,length=150,from_=1,to=11,orient=tkinter.HORIZONTAL,resolution=1)
        self.avgfilter.pack(side=tkinter.LEFT,fill=tkinter.X,expand=1,padx=5,pady=5)

        self.avgfilterBlurVar=tkinter.DoubleVar()
        self.avgfilterBlurVar.set(1.0)
        self.avgfilterBlur=tkinter.Scale(g1a,label='Blur FWHM',background='#d4d0c8',variable=self.avgfilterBlurVar,width=20,length=150,from_=0.25,to=5,orient=tkinter.HORIZONTAL,resolution=0.05)
        self.avgfilterBlur.pack(side=tkinter.LEFT,fill=tkinter.X,expand=1,padx=5,pady=5)


        Pmw.alignlabels([self.fitregionxmin,self.fitregionxmax])

        g2=Pmw.Group(q2,tag_text='Background',hull_background='#d4d0c8',tag_background='#d4d0c8',ring_background='#d4d0c8')
        g2.interior().configure(background='#d4d0c8')
        g2.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')

        self.backType = Pmw.RadioSelect(g2.interior(), labelpos = 'w', buttontype='radiobutton', orient='horizontal', command = self.bkgCallback, label_text = 'Background Type:',hull_background='#d4d0c8',frame_background='#d4d0c8',label_background='#d4d0c8')
        for text in ('SNIP','Strip'):
            self.backType.add(text,background='#d4d0c8')
        self.backType.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)

        self.SNIPwidth=Pmw.Counter(g2.interior(),labelpos='w',label_text='SNIP Background Width:',datatype='numeric',entryfield_value=60,entry_width=20,hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        self.SNIPwidth.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)
    
        self.stripWidth=Pmw.Counter(g2.interior(),labelpos='w',label_text='Strip Background Width:',datatype='numeric',entryfield_value=1,entry_width=20,hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        self.stripWidth.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)
        
        self.stripInter=Pmw.EntryField(g2.interior(),labelpos='w',label_text='Strip Background Iterations: ',validate='integer',entry_width=20,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.stripInter.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)
        self.stripInter.setvalue(20000)

        self.parameterDict['xmin']=[self.backType,False]
        self.parameterDict['snipwidth']=[self.SNIPwidth,False]
        self.parameterDict['stripfilterwidth']=[self.stripWidth,False]
        self.parameterDict['stripiterations']=[self.stripInter,False]


        Pmw.alignlabels([self.SNIPwidth,self.stripWidth,self.stripInter,self.backType])
        self.backType.invoke('SNIP')



        g3=Pmw.Group(q1,tag_text='Peaks',hull_background='#d4d0c8',tag_background='#d4d0c8',ring_background='#d4d0c8')
        g3.interior().configure(background='#d4d0c8')
        g3.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')
        
        self.peakSTA = FitOptWidget(g3.interior(),'Short Tail Area:',w=w)
        self.peakSTS = FitOptWidget(g3.interior(),'Short Tail Slope:',w=w)
        self.peakLTA = FitOptWidget(g3.interior(),'Long Tail Area:',w=w)
        self.peakLTS = FitOptWidget(g3.interior(),'Long Tail Slope:',w=w)
        
        self.parameterDict['ST AreaR']=[self.peakSTA,False]
        self.parameterDict['ST SlopeR']=[self.peakSTS,False]
        self.parameterDict['LT AreaR']=[self.peakLTA,False]
        self.parameterDict['LT SlopeR']=[self.peakLTS,False]
        
        Pmw.alignlabels([self.peakSTA.fix,self.peakSTS.fix,self.peakLTA.fix,self.peakLTS.fix])
        
        g4=Pmw.Group(q2,tag_text='Detector',hull_background='#d4d0c8',tag_background='#d4d0c8',ring_background='#d4d0c8')
        g4.interior().configure(background='#d4d0c8')
        g4.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')
        
        self.detZero = FitOptWidget(g4.interior(),'Spectrometer Zero (eV):',w=w)
        self.detGain = FitOptWidget(g4.interior(),'Spectrometer Gain (eV/bin):',w=w)
        self.detWidth = FitOptWidget(g4.interior(),'Detector Width (eV):',w=w)
        self.detFano = FitOptWidget(g4.interior(),'Fano Factor:',w=w)
        self.detPU = FitOptWidget(g4.interior(),'PileUp Factor:',w=w)
        
        self.parameterDict['Zero']=[self.detZero,True]
        self.parameterDict['Gain']=[self.detGain,True]
        self.parameterDict['Noise']=[self.detWidth,True]
        self.parameterDict['Fano']=[self.detFano,False]
        self.parameterDict['Sum']=[self.detPU,False]

        Pmw.alignlabels([self.detZero.fix,self.detGain.fix,self.detWidth.fix,self.detFano.fix,self.detPU.fix])


        #attenuatorPage=pymcanb.add('Attenuators',page_background='#d4d0c8')

        q0=tkinter.Frame(attenuatorPage, background='#d4d0c8')
        q0.pack(side=tkinter.TOP,padx=2,pady=2, fill=tkinter.BOTH, expand=1)

        q1=tkinter.Frame(q0, relief=tkinter.GROOVE,bd=2, background='#d4d0c8')
        q1.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
        l=tkinter.Label(q1,text="Attenuators",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)

        h=Attenuator(q1,'','',header=True)
        self.attenuatorWidgets={}
        nlab=[]
        mlab=[]
        dlab=[]
        tlab=[]
        
        for a in ['Atmosphere','Window','Absorber','Filter1','Filter2','Filter3','BeamFilter0','Detector']:
            w = Attenuator(q1,a,default=a,materialList=self.materialDict.materials)
            self.attenuatorWidgets[a]=w
            nlab.append(w.use)
            mlab.append(w.material)
            dlab.append(w.density)
            tlab.append(w.thickness)            

        Pmw.alignlabels(nlab)
        Pmw.alignlabels(mlab)
        Pmw.alignlabels(dlab)
        Pmw.alignlabels(tlab)

        q2=tkinter.Frame(q0, relief=tkinter.GROOVE,bd=2, background='#d4d0c8')
        q2.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
        l=tkinter.Label(q2,text="Matrix",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)

        #use matrix
        self.matrixType = Pmw.RadioSelect(q2, labelpos = 'w', buttontype='radiobutton', command=self.matrixSelect, orient='horizontal', label_text = 'Matrix Type:', hull_background='#d4d0c8',frame_background='#d4d0c8',label_background='#d4d0c8')
        for text in ('None','Single','Dynamic'):
            self.matrixType.add(text,background='#d4d0c8')
        self.matrixType.pack(side=tkinter.TOP,padx=2,anchor=tkinter.W)
        #needs to call active/disabling callback
        
        
        fr =tkinter.Frame(q2, background='#d4d0c8')
        fr.pack(side=tkinter.TOP,fill='both',expand=1)
        
        #channel to dynamically allocate attenuators
        if self.chanDict==None:
            self.chanDict={'ChA':[2011,0],'ChB':[10,1],'ChC':[3,1],'ChD':[4055,0]}
        self.chanList=[]
        for i in list(self.chanDict.keys()): 
            if self.chanDict[i][1]==1: self.chanList.append(i)
        self.dynamicChan=myComboBox(fr,label_text='Data Channel for Dynamic Correction',selectioncommand=self.channelSelect,labelpos=tkinter.N,scrolledlist_items=self.chanList,listheight=100,history=0,hull_background='#d4d0c8',label_background='#d4d0c8')
        if len(self.chanList)>0: self.dynamicChan.selectitem(self.chanList[0])
        self.dynamicChan.pack(side=tkinter.TOP,padx=4,pady=8,anchor=tkinter.W)
        
        self.matrixAttenuators={}
                
        hwv=400
        j=Pmw.ScrolledFrame(fr,hull_width=hwv,hull_height=300,usehullsize=1,vertflex='expand',horizflex='expand')
        j.interior().configure(background='#d4d0c8')
        j.pack(side=tkinter.TOP,pady=2)
        self.Attint=tkinter.Frame(j.interior(),bd=2,relief=tkinter.SUNKEN,background='#d4d0c8')
        self.Attint.pack(side=tkinter.TOP,fill='both',expand='y')

        h=Attenuator(self.Attint,'','',header=True,interior=True)
        self.matrixType.invoke('None')
        
        #mateditorPage=pymcanb.add('Materials',page_background='#d4d0c8')

        q3=tkinter.Frame(mateditorPage, relief=tkinter.GROOVE,bd=2, background='#d4d0c8')
        q3.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
 
        q4=tkinter.Frame(mateditorPage, relief=tkinter.GROOVE,bd=2, background='#d4d0c8')
        q4.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
           
        
        l=tkinter.Label(q3,text="Material Editor",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)

        w=20
        bb=PmwTtkButtonBox.PmwTtkButtonBox(q3,labelpos='n',label_text='Edit Options',orient='horizontal',padx=3,frame_background='#d4d0c8',hull_background='#d4d0c8',label_background='#d4d0c8')
        bb.add('New Material',style='LGREEN.TButton',width=w,command=self.newMaterial)
        bb.add('Save Material',style='GREEN.TButton',width=w,command=self.editSaveMaterial)
        bb.pack(side=tkinter.TOP,padx=5,pady=5,anchor=tkinter.W)        
        bb=PmwTtkButtonBox.PmwTtkButtonBox(q3,labelpos='n',label_text='Edit Options',orient='horizontal',padx=3,frame_background='#d4d0c8',hull_background='#d4d0c8',label_background='#d4d0c8')
        bb.add('Clear/Load Database',style='SBLUE.TButton',width=w,command=self.clearLoadMatDatabase)
        bb.add('Load into Database',style='NAVY.TButton',width=w,command=self.addtoMatDatabase)
        bb.add('Save Database',style='BROWN.TButton',width=w,command=self.saveMatDatabase)
        bb.pack(side=tkinter.TOP,padx=5,pady=5,anchor=tkinter.W)        

        self.ed_material=myComboBox(q3,label_text='Material Name:',selectioncommand=self.ed_materialSelect,labelpos=tkinter.W,scrolledlist_items=list(self.materialDict.materials.keys()),listheight=100,history=0,hull_background='#d4d0c8',label_background='#d4d0c8')
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

        h=Compound(self.edCompint,header=True)
        
        w=Compound(self.edCompint)
        self.edCompounds.append(w)
        
        
        fr=tkinter.Frame(f, background='#d4d0c8')
        fr.pack(side=tkinter.LEFT)
        
        self.ed_defdensity=Pmw.EntryField(fr,labelpos='w',label_text="Default Density: ",validate='real',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.ed_defdensity.pack(side=tkinter.TOP,padx=2)
        self.ed_defthickness=Pmw.EntryField(fr,labelpos='w',label_text="Default Thickness: ",validate='real',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.ed_defthickness.pack(side=tkinter.TOP,padx=2)                

        Pmw.alignlabels([self.ed_defdensity,self.ed_defthickness])
        
        self.ed_comment=Pmw.EntryField(q3,labelpos='w',label_text="Material Comment: ",entry_width=50,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.ed_comment.pack(side=tkinter.LEFT,padx=2)
        
        Pmw.alignlabels([self.ed_material,self.ed_comment,self.ed_nummats])


        l=tkinter.Label(q4,text="Beam-Detector Properties",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)

        #area
        self.bd_detarea=Pmw.EntryField(q4,labelpos='w',label_text="Detector Area (mm2): ",validate='real',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.bd_detarea.pack(side=tkinter.TOP,padx=2,pady=4)
        #distance
        self.bd_detdistance=Pmw.EntryField(q4,labelpos='w',label_text="Detector Distance (mm): ",validate='real',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.bd_detdistance.pack(side=tkinter.TOP,padx=2,pady=4)
        #flux
        self.bd_flux=Pmw.EntryField(q4,labelpos='w',label_text="Incident Flux (ph/s): ",validate='real',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.bd_flux.pack(side=tkinter.TOP,padx=2,pady=4)
        #dwell
        self.bd_dwell=Pmw.EntryField(q4,labelpos='w',label_text="Dwell Time (ms): ",validate='real',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.bd_dwell.pack(side=tkinter.TOP,padx=2,pady=4)
        
        Pmw.alignlabels([self.bd_detarea,self.bd_detdistance,self.bd_flux,self.bd_dwell])

        if sys.platform != 'darwin':
            pymcanb.setnaturalsize()
            
        self.pyParamWin.geometry('')
        
        #populate defaults, or current config file
        if self.configFile == None:

            if getattr(sys, 'frozen', False):
                path = os.path.dirname(sys.executable)
                if sys.platform=='darwin':
                    if 'MacOS' in path: path = path.replace('MacOS','Resources')
            elif __file__:
                path = os.path.dirname(__file__)
        
            #path=os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))+os.sep+"pyMcaConfigs"+os.sep
            path=path+os.sep+"pyMcaConfigs"+os.sep

#            path=os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))+os.sep+"pyMcaConfigs"+os.sep
#            print path
            self.configFile=path+"defaultPyMCAConfig.cfg"

        self.parameters = PyCD.ConfigDict()
        self.readConfiguration()
        
        self.populateParameters()
        
    def raiseme(self,args):
        pass        

    def killpyParamWin(self):
        if self.closeCallBack!=None: self.closeCallBack()
        self.MCAzoomstack=[]
        self.pyParamWin.destroy()  

    def editNumCompounds(self,*args):
        while int(self.ed_nummats.getvalue()) < len(self.edCompounds):
            self.edCompounds[-1].widget.destroy()
            self.edCompounds.pop()
            
        while int(self.ed_nummats.getvalue()) > len(self.edCompounds):
            w=Compound(self.edCompint)
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
        self.ed_material._list.setlist(sorted(list(self.materialDict.materials.keys()),key=str.lower))
        for n in list(self.matrixAttenuators.values()):
            n.refresh(self.materialDict.materials)
        for o in list(self.attenuatorWidgets.values()):
            o.refresh(self.materialDict.materials)
        
    def newMaterial(self):
        new = pyMcaMaterials.MaterialItem()
        nn = tkinter.simpledialog.askstring('Material Properties','New Material Name: ',parent=self.master)        
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
        self.ed_material._list.setlist(sorted(list(self.materialDict.materials.keys()),key=str.lower))            
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
            w = Attenuator(self.Attint,'Matrix '+str(i+1),default='--',interior=True,materialList=self.materialDict.materials)
            self.matrixAttenuators['Matrix '+str(i+1)]=w
                
    def matrixSelect(self,sel):
        if sel=='None':
            #disable channels and clear attenuators
            self.dynamicChan.disable()
            for w in list(self.matrixAttenuators.values()):
                w.widget.destroy()
            self.matrixAttenuators={}
        
        if sel=='Single':
            self.dynamicChan.disable()
            for w in list(self.matrixAttenuators.values()):
                w.widget.destroy()
            self.matrixAttenuators={}
            #add one back
            w = Attenuator(self.Attint,'Matrix 1',default='--',interior=True,materialList=self.materialDict.materials)
            self.matrixAttenuators['Matrix 1']=w
            
        if sel=='Dynamic':
            self.dynamicChan.enable()
            for w in list(self.matrixAttenuators.values()):
                w.widget.destroy()
            self.matrixAttenuators={}
            
    def populateParameters(self):
        #peaks        
        for p in list(self.parameters['peaks'].keys()):
            self.addPeak(p,self.parameters['peaks'][p])
        
        self.fitregionxmin.setvalue(self.parameters['fit']['xmin'])
        self.fitregionxmax.setvalue(self.parameters['fit']['xmax'])

        if self.parameters['fit']['stripalgorithm']==1: self.backType.setvalue('SNIP')
        else: self.backtype.setvalue('Strip') 
        
        self.SNIPwidth.setvalue(self.parameters['fit']['snipwidth'])
        self.stripWidth.setvalue(self.parameters['fit']['stripwidth'])
        self.stripInter.setvalue(self.parameters['fit']['stripiterations'])
        
        self.peakSTA.setValue(self.parameters['peakshape']['st_arearatio'])
        self.peakSTA.setError(self.parameters['peakshape']['deltast_arearatio'])
        self.peakSTA.setFix(self.parameters['peakshape']['fixedst_arearatio'])        

        self.peakSTS.setValue(self.parameters['peakshape']['st_sloperatio'])
        self.peakSTS.setError(self.parameters['peakshape']['deltast_sloperatio'])
        self.peakSTS.setFix(self.parameters['peakshape']['fixedst_sloperatio'])

        self.peakLTA.setValue(self.parameters['peakshape']['lt_arearatio'])
        self.peakLTA.setError(self.parameters['peakshape']['deltalt_arearatio'])
        self.peakLTA.setFix(self.parameters['peakshape']['fixedlt_arearatio'])

        self.peakLTS.setValue(self.parameters['peakshape']['lt_sloperatio'])
        self.peakLTS.setError(self.parameters['peakshape']['deltalt_sloperatio'])
        self.peakLTS.setFix(self.parameters['peakshape']['fixedlt_sloperatio'])
                
        self.detZero.setValue(self.parameters['detector']['zero'],convert=True)
        self.detZero.setError(self.parameters['detector']['deltazero'],convert=True)
        self.detZero.setFix(self.parameters['detector']['fixedzero'])
        
        self.detGain.setValue(self.parameters['detector']['gain'],convert=True)
        self.detGain.setError(self.parameters['detector']['deltagain'],convert=True)
        self.detGain.setFix(self.parameters['detector']['fixedgain']) 

        self.detWidth.setValue(self.parameters['detector']['noise'],convert=True)
        self.detWidth.setError(self.parameters['detector']['deltanoise'],convert=True)
        self.detWidth.setFix(self.parameters['detector']['fixednoise'])

        self.detFano.setValue(self.parameters['detector']['fano'])
        self.detFano.setError(self.parameters['detector']['deltafano'])
        self.detFano.setFix(self.parameters['detector']['fixedfano'])

        self.detPU.setValue(self.parameters['detector']['sum'])
        self.detPU.setError(self.parameters['detector']['deltasum'])
        self.detPU.setFix(self.parameters['detector']['fixedsum'])

        #clear attenuators?
        self.matrixType.invoke("None")

        for a in list(self.attenuatorWidgets.keys()):
            if a in list(self.parameters['attenuators'].keys()):
                #print a
                try:
                    if self.parameters['attenuators'][a][0]==1:
                        self.attenuatorWidgets[a].use.setvalue(['Use'])
                    else:
                        self.attenuatorWidgets[a].use.setvalue([])
                except:
                    print('invalid use')

                #print a,self.attenuatorWidgets[a].use.getvalue()

                try:
                    self.attenuatorWidgets[a].material.selectitem(self.parameters['attenuators'][a][1],setentry=1)
                except:
                    print('invalid material')
                try:
                    self.attenuatorWidgets[a].density.setvalue(self.parameters['attenuators'][a][2])
                except:
                    print('invalid density')
                try:
                    self.attenuatorWidgets[a].thickness.setvalue(self.parameters['attenuators'][a][3])
                except:
                    print('invalid thickness')
        if "Matrix" in list(self.parameters['attenuators'].keys()) and self.parameters['attenuators']['Matrix'][0]==1:
            self.matrixType.invoke('Single')
            a=self.matrixAttenuators["Matrix 1"]
            try:
                a.material.selectitem(self.parameters['attenuators']["Matrix"][1],setentry=1)
            except:
                print('invalid material')
            try:
                a.density.setvalue(self.parameters['attenuators']["Matrix"][2])
            except:
                print('invalid density')
            try:
                a.thickness.setvalue(self.parameters['attenuators']["Matrix"][3])
            except:
                print('invalid thickness')
                
        if "smak_dynamic" in list(self.parameters.keys()):
            d = self.parameters['smak_dynamic']['Channel']
            self.matrixType.invoke("Dynamic")
            self.dynamicChan.selectitem(d,setentry=1)
            self.channelSelect(d)
            for (k,w) in list(self.matrixAttenuators.items()):
                try:
                    w.material.selectitem(self.parameters['smak_dynamic'][k][1],setentry=1)
                except:
                    print("invalid material")
                try:
                    w.density.setvalue(self.parameters['smak_dynamic'][k][2])
                except:
                    print('invalid density')
                try:
                    w.thickness.setvalue(self.parameters['smak_dynamic'][k][3])
                except:
                    print('invalid thickness')
                    
        if "concentrations" in list(self.parameters.keys()):
            self.bd_detarea.setvalue(float(self.parameters['concentrations']["area"])*100.)
            self.bd_detdistance.setvalue(float(self.parameters['concentrations']["distance"])*10.)
            self.bd_dwell.setvalue(float(self.parameters['concentrations']["time"])*1000.)
            self.bd_flux.setvalue(sci_str(float(self.parameters['concentrations']["flux"])))
        else:
            self.bd_detarea.setvalue(50.0)
            self.bd_detdistance.setvalue(10.0)
            self.bd_dwell.setvalue(50)
            self.bd_flux.setvalue(sci_str(1e9))        
                     
    def populateFittedParameters(self,fp):
        for p in list(fp.keys()):
            if p in list(self.parameterDict.keys()):
                #print p,fp[p]
                self.parameterDict[p][0].setValue(fp[p],convert=self.parameterDict[p][1])
        
    def getGUIParameters(self):
        #peaks
        self.parameters['peaks']={}
        for p in self.peaks:
            [E,L]=p[0].split('_')
            if E in list(self.parameters['peaks'].keys()):
                if isinstance(self.parameters['peaks'][E], list):
                    self.parameters['peaks'][E].append(L)
                else:
                    self.parameters['peaks'][E]=[self.parameters['peaks'][E],L]
            else:
                self.parameters['peaks'][E]=L
        
        self.parameters['fit']['energy'][0]=float(self.beamEnergy.getvalue())/1000.0        
        
        self.parameters['fit']['xmin']=int(self.fitregionxmin.getvalue())
        self.parameters['fit']['xmax']=int(self.fitregionxmax.getvalue())
        
        if self.backType.getvalue()=='SNIP':
            self.parameters['fit']['stripalgorithm']=1
        else:
            self.parameters['fit']['stripalgorithm']=0
            
        self.parameters['fit']['snipwidth']=int(self.SNIPwidth.getvalue())
        self.parameters['fit']['stripwidth']=int(self.stripWidth.getvalue())
        self.parameters['fit']['stripinterations']=int(self.stripInter.getvalue())
        
        self.parameters['peakshape']['st_arearatio']=float(self.peakSTA.getValue())
        self.parameters['peakshape']['deltast_arearatio']=float(self.peakSTA.getError())
        self.parameters['peakshape']['fixedst_arearatio']=self.peakSTA.getFix() 
        
        self.parameters['peakshape']['st_sloperatio']=float(self.peakSTS.getValue())
        self.parameters['peakshape']['deltast_sloperatio']=float(self.peakSTS.getError())       
        self.parameters['peakshape']['fixedst_sloperatio']=self.peakSTS.getFix()

        self.parameters['peakshape']['lt_arearatio']=float(self.peakLTA.getValue())
        self.parameters['peakshape']['deltalt_arearatio']=float(self.peakLTA.getError())
        self.parameters['peakshape']['fixedlt_arearatio']=self.peakLTA.getFix()

        self.parameters['peakshape']['lt_sloperatio']=float(self.peakLTS.getValue())
        self.parameters['peakshape']['deltalt_sloperatio']=float(self.peakLTS.getError())
        self.parameters['peakshape']['fixedlt_sloperatio']=self.peakLTS.getFix()

        self.parameters['detector']['zero']=self.detZero.getValue(convert=True)
        self.parameters['detector']['deltazero']=self.detZero.getError(convert=True)
        self.parameters['detector']['fixedzero']=self.detZero.getFix()

        self.parameters['detector']['gain']=self.detGain.getValue(convert=True)
        self.parameters['detector']['deltagain']=self.detGain.getError(convert=True)
        self.parameters['detector']['fixedgain']=self.detGain.getFix() 
        
        self.parameters['detector']['noise']=self.detWidth.getValue(convert=True)
        self.parameters['detector']['deltanoise']=self.detWidth.getError(convert=True)
        self.parameters['detector']['fixednoise']=self.detWidth.getFix()

        self.parameters['detector']['fano']=float(self.detFano.getValue())
        self.parameters['detector']['deltafano']=float(self.detFano.getError())
        self.parameters['detector']['fixedfano']=self.detFano.getFix()

        self.parameters['detector']['sum']=float(self.detPU.getValue())
        self.parameters['detector']['deltasum']=float(self.detPU.getError())
        self.parameters['detector']['fixedsum']=self.detPU.getFix()
        
        #attenuators
        att = {}
        mat={}
        for a in list(self.attenuatorWidgets.keys()):
            attValues=[0,0,0,0,1]
            if len(self.attenuatorWidgets[a].use.getvalue())>0 and self.attenuatorWidgets[a].use.getvalue()[0]=='Use':
                attValues[0]=1
            else:
                attValues[0]=0
            attValues[1] = self.attenuatorWidgets[a].material.getvalue()[0]
            if self.attenuatorWidgets[a].density.valid(): attValues[2] = float(self.attenuatorWidgets[a].density.getvalue())
            if self.attenuatorWidgets[a].thickness.valid(): attValues[3] = float(self.attenuatorWidgets[a].thickness.getvalue()) 
            att[a]=attValues
            if attValues[0]==1:
                mat[attValues[1]]=self.materialDict.materials[attValues[1]].get()
        #matrix
        att['Matrix']=[0,'--',0,0,45,45,0,90]
        
        sel = self.matrixType.getvalue()
        print(sel)
        
        if sel=='None':
            #no need to do anything different
            pass
        if sel=='Single':
            w=self.matrixAttenuators['Matrix 1']        
            att['Matrix'][0]=1
            att['Matrix'][1]=w.material.getvalue()[0]
            if w.density.valid(): att['Matrix'][2]=float(w.density.getvalue())
            if w.thickness.valid(): att['Matrix'][3]=float(w.thickness.getvalue()) 
        if sel=='Dynamic':
            #will be set in dynamic mode
            #but lets put the crap in the config file...
            pAtt={}
            pAtt['Channel']=self.dynamicChan.getvalue()[0]
            for (a,w) in list(self.matrixAttenuators.items()):
                attv=[1,0,0,0,1]
                attv[1]=w.material.getvalue()[0]
                if w.density.valid(): attv[2]=str(w.density.getvalue())
                if w.thickness.valid(): attv[3]=str(w.thickness.getvalue())
                pAtt[a] = attv
            self.parameters['smak_dynamic']=pAtt          
        
        if sel!='Dynamic' and 'smak_dynamic' in list(self.parameters.keys()):
            self.parameters.pop('smak_dynamic')
            
        self.parameters['attenuators']=att
        
        #write materials too
        for w in list(self.matrixAttenuators.values()):
            mat[w.material.getvalue()[0]]=self.materialDict.materials[w.material.getvalue()[0]].get()
            
        if '--' in list(mat.keys()):
            mat.pop('--',None)
            
        self.parameters['materials']=mat

        cdef={}
        if self.bd_detarea.valid(): cdef["area"]=float(self.bd_detarea.getvalue())/100.
        if self.bd_detdistance.valid(): cdef["distance"]=float(self.bd_detdistance.getvalue())/10.
        if self.bd_dwell.valid(): cdef["time"]=float(self.bd_dwell.getvalue())/1000.
        if self.bd_flux.valid(): cdef["flux"]=float(self.bd_flux.getvalue())
        self.parameters['concentrations']=cdef

        
    def setMatrixDefinition(self,num):
        #get attenuators
        num = int(num) 
        att=self.parameters['attenuators']
        attValues=[1,'--',0,0,1,45,45]
                
        if num<(len(self.matrixAttenuators)):            
            w=self.matrixAttenuators['Matrix '+str(num+1)]        
            attValues[1]=w.material.getvalue()[0]
            attValues[2]=float(w.density.getvalue())
            attValues[3]=float(w.thickness.getvalue()) 
        
        att['Matrix']=attValues
        self.parameters['attenuators']=att
        
    def readConfiguration(self,file=None):
        if file!=None:
            self.configFile=file
        self.parameters.clear()
        self.parameters.read(self.configFile)
        
        print(list(self.parameters.keys()))
        
    def saveConfiguration(self,fn):
        if fn==None: return
        self.configFile=fn
        self.parameters.write(self.configFile)
        
    def addelement(self,master,ename,rpos,cpos,etyp):
        #add an element button 1=noble, 2=alkali, 3=pseudo, 4=non, 5=metal, 6=lanth, 7=act
        if etyp==1: bc='PTgoldenrod.TButton'
        if etyp==2: bc='PTtan.TButton'
        if etyp==3: bc='PTorange.TButton'
        if etyp==4: bc='PTlight blue.TButton'
        if etyp==5: bc='PTdark green.TButton'
        if etyp==6: bc='PTrosy brown.TButton'
        if etyp==7: bc='PTdark red.TButton'
        b=Button(master,text=ename,width=3,style=bc)#,height=1
        b.grid(row=rpos,column=cpos)
        b.bind("<Button-1>",self.centerclick)
        self.atomDict[ename]=[b,0,bc,"s"+bc,"PTgray.TButton"]

    def centerclick(self,event):
        atom=event.widget.cget('text')
        state = self.atomDict[atom][1]        
        if state==0:
            self.resetAtomStates()
            self.atomDict[atom][1]=1        
            self.resetAtomStyles()
            self.atom=atom
        else:
            self.resetAtomStates()
            self.atomDict[atom][1]=0
            self.resetAtomStyles()
            self.atom=None

    def resetAtomStates(self):
        if self.atom==None: return
        if self.atomDict[self.atom][1]==1:
            self.atomDict[self.atom][1]=0
            
    def resetAtomStyles(self):
        for b in list(self.atomDict.values()):
            b[0].config(style=b[b[1]+2])           
        
    def setPeakLine(self,event):
        line = event.widget.cget('text')
        print(self.atom,line)
        if self.atom==None:
            print("need valid atom")
            return
        if self.elist[self.atom][0]<3 and line=="L":
            print("invalid line")
            return
        if self.elist[self.atom][0]<22 and line=="M":
            print("invalid line")
            return   

        self.addPeak(self.atom,line)

    def addPeak(self,atom,line):
        
        self.atomDict[atom][1]=2
        self.resetAtomStyles()

        ld = {"K":0.1,"L":0.2,"M":0.3}


        linetup = [atom+"_"+line,self.elist[atom][0]+ld[line]]
        print(linetup)
        if linetup not in self.peaks:
            self.peaks.insert(linetup)
            self.peaksus.append(linetup)
            ind=self.peaks.index(linetup)
            self.peaklist.insert((atom+"_"+line),ind)#listbox.insert(ind,atom+" "+line)
            #self.peaklist.listbox.select_clear()
        else:
            print("line already added")
        
    def choosePeak(self,arg):
        if arg !=[]:
            [ele,trans] = self.peaks[arg[0]][0].split('_')
            #print ele,trans
            #print(arg,ele,trans)
            #get energy
            lines = pEle.Element[ele][trans+' xrays']
            evs = {}
            bins ={}
            rate ={}
            for l in lines:
                evs[l] = pEle.Element[ele][l]['energy']*1000.0
                rate[l] = pEle.Element[ele][l]['rate']
                #cabibration to bin
                if float(self.detGain.getValue())>0:
                    bins[l] = evs[l]/float(self.detGain.getValue())
                else: 
                    bins[l] = evs[l]
            #remove any existing line markers
                    
            if self.graphwid==None: return                    
                    
            #print(len(self.graphwid.fluolines))                    
                    
            for gl in self.graphwid.fluolines:
                try:
                    self.graphwid.graphaxes.lines.remove(gl)
                except:
                    print("line removal exception")
            self.graphwid.fluolines=[]
            #add to plot
            for e in list(bins.keys()):
                if not self.graphwid.hasUnitsEnergy:
                    newline=self.graphwid.graphaxes.axvline(x=bins[e],color="lightgray")
                else:
                    newline=self.graphwid.graphaxes.axvline(x=evs[e],color="lightgray")
                self.graphwid.fluolines.append(newline)
            self.graphwid.canvas.draw()


    def clearCurPeakLine(self):
        ind=self.peaklist.curselection()
        if ind != []:
            ind=ind[0]
            self.peaklist.delete(ind)
            item = self.peaksus[ind]
            self.peaks.remove(item)
            self.peaksus.pop(ind)
            
            #clear all styles
            for b in list(self.atomDict.values()):
                b[1]=0            
            #add back styles
            for p in self.peaks:
                el = p[0].split()[0]
                self.atomDict[el][1]=2
            self.resetAtomStyles()

    def clearAllPeakLine(self):
        self.peaks.clear()
        self.peaklist.clear()#self.peaklist.listbox.delete(tkinter.ALL)  
        self.peaksus=[]
        for b in list(self.atomDict.values()):
            b[1]=0
        self.resetAtomStyles()
                            
    def bkgCallback(self,arg):
        #disable based on self.backType
        if self.backType.getvalue()=='SNIP':
            self.stripWidth.configure(entryfield_entry_state = tkinter.DISABLED)
#            self.stripWidth.configure(downarrow_state = tkinter.DISABLED)
#            self.stripWidth.configure(uparrow_state = tkinter.DISABLED)
            self.stripInter.configure(entry_state=tkinter.DISABLED)
            self.SNIPwidth.configure(entryfield_entry_state=tkinter.NORMAL)
 #           self.SNIPwidth.configure(downarrow_state = NORMAL)
 #           self.SNIPwidth.configure(uparrow_state = NORMAL)
        else:
            self.stripWidth.configure(entryfield_entry_state=tkinter.NORMAL)
  #          self.stripWidth.configure(downarrow_state = NORMAL)
  #          self.stripWidth.configure(uparrow_state = NORMAL)
            self.stripInter.configure(entry_state=tkinter.NORMAL)
            self.SNIPwidth.configure(entryfield_entry_state=tkinter.DISABLED)
   #         self.SNIPwidth.configure(downarrow_state = tkinter.DISABLED)
   #         self.SNIPwidth.configure(uparrow_state = tkinter.DISABLED)
