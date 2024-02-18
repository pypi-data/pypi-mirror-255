# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 18:19:31 2023

@author: stewards
"""
#necessary first imports
import tkinter
import Pmw

#standard libraries
import math
import os
import sys
import threading


#third party
import matplotlib.colors as matcolors
import numpy as np
from PIL import Image, ImageTk
from PIL import _imaging
from scipy.optimize import curve_fit


#local imports
import ImCmap
import ImRadon
import MyGraph
import screencapture
import globalfuncs


global MINSIZE
global DEFAULT_HEIGHT
DEFAULT_HEIGHT=254
MINSIZE=300

#######################################
## Imaging Routines
#######################################



def preprocess(root,image, xxx_todo_changeme, cutoff, cutlo, one2onescale=0, convert=1,DEFAULT=0.0):
    (scalex,scaley)=xxx_todo_changeme
    global MINSIZE
    global DEFAULT_HEIGHT    
    assert len(image.shape) in (1, 2) or \
           len(image.shape) == 3 and image.shape[2] == 3, \
           "image not correct format"
    #themin=float(np.minimum.reduce(np.ravel(image)))
    #themax=float(np.maximum.reduce(np.ravel(image)))
    print (image.shape)
    themin=float(np.amin(np.ravel(image)))
    themax=float(np.amax(np.ravel(image)))
    
    if np.isnan(themin) or themin==np.inf: themin=0.0
    if np.isnan(themax) or themax==np.inf: themax=1.0e10
    if themax==0: themax=1.0
    print(themax, themin)    
    image=(image - themax*cutlo) / (themax*cutoff) * DEFAULT_HEIGHT 
#    image=(image - themax*cutlo) / (themax*cutoff-themax*cutlo) * DEFAULT_HEIGHT 
#    image=(image - themax*cutlo) / (themax-themax*cutlo) * DEFAULT_HEIGHT / cutoff
#    image=(image) / (themax) * DEFAULT_HEIGHT / cutoff
    image=np.where(np.greater(image,DEFAULT_HEIGHT),DEFAULT_HEIGHT,image)
    image=np.where(np.greater(image,0),image,0)

    ##print 'inpre:',themax,max(ravel(image))
    if convert: image=image.astype('b')
    ##print 'postb:',max(ravel(image))
    
    len_x, len_y=image.shape[:2]
    #print 'len',len_x,len_y
    if scalex is None:
        #if len_x < MINSIZE:
        scalex=(float(MINSIZE) / len_x) + 1 #+1
        #else:
        #    scalex=1
    if scaley is None:
        #if len_y < MINSIZE:
        scaley=(float(MINSIZE) / len_y) + 1 #+1
        #else:
        #    scaley=1
    if scalex<1: scalex=1
    if scaley<1: scaley=1
    #print '1st',scalex,scaley
    maxscalex=(float(root.winfo_screenheight())/float(len_x))-0 #int?
    maxscaley=(float(root.winfo_screenwidth())/float(len_y))-0
    #print 'max',maxscalex,maxscaley
    if one2onescale:
        if maxscalex<1: maxscalex=1
        if maxscaley<1: maxscaley=1
    #print 'pre',scalex,scaley
    if scalex>maxscalex:
        scalex=maxscalex
    if scaley>maxscaley:
        scaley=maxscaley
    if scalex!=scaley:
        temp=min((scalex,scaley))
        scalex=temp
        scaley=temp
    #print 'post',scalex,scaley
    return image, (scalex, scaley)

def save_ppm(ppm, fname=None):
    import tempfile
#    if fname is None:
#        fname=tempfile.mktemp('.ppm')
    td=tempfile.gettempdir()
    fname=td+'\\SMAK.ppm'
    f=open(fname, 'w')
    f.write(ppm)
    f.close()
    return fname

def array2ppm(image):
    # scaling
    if len(image.shape) == 2:
        # B&W:
        image=np.transpose(image)
        return "P5\n#PPM version of array\n%d %d\n255\n%s" % \
               (image.shape[1], image.shape[0], np.ravel(image).tobytes())
    else:
        # color
        image=np.transpose(image, (1, 0, 2))
        return "P6\n%d %d\n255\n%s" % \
               (image.shape[1], image.shape[0], np.ravel(image).tobytes())


class DisplayParams:
    def __init__(self,toggleVAR,viewFUNC,scaleVAR,scaleTextVAR, flipVAR,scaleFact,status,zooms):
        self.toggleVAR=toggleVAR
        self.viewFUNC=viewFUNC
        self.scaleVAR=scaleVAR
        self.scaleTextVAR=scaleTextVAR
        self.flipVAR=flipVAR
        self.scaleFact=scaleFact
        self.status=status
        self.zmxyi=zooms

#############################
##   Display Class
#############################

class Display:                                                                                  #func,name
    def __init__(self,master,toggleVAR,viewFUNC,scaleVAR,scaleTextVAR, flipVAR,main=1,tcrefresh=None,callback=[None,None,None,None,None],rowcb=None,show=True,sf=None,proc=None):
        self.master=master
        self.main=Pmw.MegaToplevel(master)
        self.main.title('Image Display')
        self.scalefact=sf
        #self.preprocess=proc
        if main:
            self.main.userdeletefunc(func=self.main.withdraw)
        if callback[0] is not None:
            self.main.userdeletefunc(func=self.closecallback)
        self.callback=callback
        self.rowcb=rowcb
        h=self.main.interior()
        self.viewFUNC=viewFUNC
        self.flipVAR=flipVAR
        self.toggleVAR=toggleVAR
        self.toggleAddPlotVAR=tkinter.IntVar()
        self.toggleAddPlotVAR.set(0)
        self.showMaskROI=tkinter.IntVar()
        self.showMaskROI.set(0)
        self.showMaskROIUpdates=tkinter.IntVar()
        self.showMaskROIUpdates.set(0)
        self.scaleVAR=scaleVAR
        self.scaleTextVAR=scaleTextVAR
        self.tcrefresh=tcrefresh
        self.viewscaleVAR=tkinter.IntVar()
        self.viewscaleVAR.set(0)
        self.FitLineProf=tkinter.StringVar()
        self.FitLineProf.set("None")
        self.MaskDrawType=tkinter.StringVar()
        self.MaskDrawType.set("Freeform")
        self.masktype=None
        self.apply45Calc=tkinter.IntVar()
        self.apply45Calc.set(0)
        self.savedPSF=np.zeros((3,3))
        #frame for image and intensity slider
        nf=tkinter.Frame(h,background='#d4d0c8')
        nf.pack(side=tkinter.TOP,fill='both')
        self.items=[]
        self.scaleitems=[]
        self.scaleframe=tkinter.Canvas(nf,bg='black',borderwidth=2,height=250,width=250, cursor='crosshair')
        self.scaleframe.pack(side=tkinter.LEFT,fill='both')

        self.imframe=tkinter.Canvas(self.scaleframe,bg='black',borderwidth=2, height=250, width=250, cursor='crosshair')
        self.imframe.bind(sequence="<Motion>", func=self.coordreport)
        self.imframe.bind(sequence="<Double-Button-1>",func=self.showlineplots)
        if sys.platform=='darwin':
            self.imframe.bind(sequence="<ButtonPress>",func=self.macbutton)
            self.imframe.bind(sequence="<ButtonRelease>",func=self.macbuttonrelease)
            self.imframe.bind(sequence="<Shift-Double-Button-1>",func=self.finishmapaverage)
        else:
            #bindings for averaging...
            self.imframe.bind(sequence="<Shift-Button-1>",func=self.mapaverage)
            self.imframe.bind(sequence="<Shift-Double-Button-1>",func=self.finishmapaverage)
            #bindings for zoom...
            self.imframe.bind(sequence="<Control-ButtonPress>",func=self.addzoompt)
            self.imframe.bind(sequence="<Control-ButtonRelease>",func=self.finishzoom)
            #bindings for x-section...
            self.imframe.bind(sequence="<Alt-ButtonPress>",func=self.startxsection)
            self.imframe.bind(sequence="<Alt-ButtonRelease>",func=self.finishxsection)
        self.editBindingB1(True)
        #binding for zoom shift
        self.main.bind(sequence="<Key-Up>",func=self.shiftzoompos)
        self.main.bind(sequence="<Key-Down>",func=self.shiftzoompos)        
        self.main.bind(sequence="<Key-Left>",func=self.shiftzoompos)
        self.main.bind(sequence="<Key-Right>",func=self.shiftzoompos)
        
##        self.imframe.pack(side=tkinter.LEFT,fill='both')#'both',expand=YES)
        self.scaleframewid=self.scaleframe.create_window(20,20,anchor='nw',window=self.imframe)
        #popup menu for image frame
        self.popmenu=tkinter.Menu(self.imframe,tearoff=0)
        self.popmenu.add_command(label='Swap X direction',command=self.swapxdir)
        self.popmenu.add_command(label='Swap Y direction',command=self.swapydir)
        self.popmenu.add_command(label='Swap XY axes',command=self.swapxydir)
        self.popmenu.add_separator()
        self.popmenu.add_checkbutton(label='Add to graphs',variable=self.toggleAddPlotVAR,command=tkinter.DISABLED)
        self.popmenu.add_separator()
        maskpopmenu=tkinter.Menu(self.popmenu,tearoff=0)
        maskpopmenu.add_radiobutton(label='Rectangle',command=tkinter.DISABLED,variable=self.MaskDrawType)
        maskpopmenu.add_radiobutton(label='Circle',command=tkinter.DISABLED,variable=self.MaskDrawType)
        maskpopmenu.add_radiobutton(label='Freeform',command=tkinter.DISABLED,variable=self.MaskDrawType)
        self.popmenu.add_cascade(label='Mask Type',menu=maskpopmenu)
        self.popmenu.add_checkbutton(label='View Mask ROI',variable=self.showMaskROI,command=self.updateROIDisp)
        self.popmenu.add_command(label='Mask Transform',command=self.maskAffinetransform)
        #self.popmenu.add_checkbutton(label='Do Updates w/ Mask ROI',variable=self.showMaskROIUpdates,command=tkinter.DISABLED)
        self.popmenu.add_separator()
        self.popmenu.add_command(label='Save Zoom as PSF',command=self.saveZasPSF)
        self.popmenu.add_separator()
        self.popmenu.add_checkbutton(label='View MCA',variable=self.toggleVAR,command=tkinter.DISABLED)
        self.popmenu.add_checkbutton(label='View Scales',variable=self.viewscaleVAR,command=self.updateDisp)
        self.popmenu.add_checkbutton(label='Apply 45 Correction',variable=self.apply45Calc,command=self.updateDisp)

        self.popmenu.add_separator()
        self.popmenu.add_command(label='Clear Zoom',command=self.clearzoom)
        self.popmenu.add_command(label='Edge Removal',command=self.edgezoom)
        self.popmenu.add_separator()
        self.popmenu.add_command(label='Set MAX scale',command=self.extendmax)
        self.popmenu.add_separator()
        fitpopmenu=tkinter.Menu(self.popmenu,tearoff=0)
        fitpopmenu.add_radiobutton(label='None',command=tkinter.DISABLED,variable=self.FitLineProf)
        fitpopmenu.add_radiobutton(label='Linear',command=tkinter.DISABLED,variable=self.FitLineProf)
        fitpopmenu.add_radiobutton(label='Gauss',command=tkinter.DISABLED,variable=self.FitLineProf)
        fitpopmenu.add_radiobutton(label='Gauss+Lin',command=tkinter.DISABLED,variable=self.FitLineProf)
        self.popmenu.add_cascade(label='Line Profile Fitting',menu=fitpopmenu)
        self.popmenu.add_separator()        
        self.popmenu.add_command(label='Save JPG',command=self.savejpgimage_menu)              
        if sys.platform=='darwin':
            self.imframe.bind(sequence="<Button-2>", func=self.showpopup)
        else:
            self.imframe.bind(sequence="<Button-3>", func=self.showpopup)
        fr=tkinter.Frame(nf,background='#d4d0c8')
        fr.pack(side=tkinter.LEFT,fill='both')
        lab=tkinter.Label(fr,text='Low',width=3,anchor=tkinter.N,background='#d4d0c8')
        lab.pack(side=tkinter.TOP,fill='both')
        self.intenvarlo=tkinter.DoubleVar()
        self.intenvarlo.set(0.00)
        self.curinlo=0.0
        self.intensitylo=tkinter.Scale(fr,variable=self.intenvarlo,background='#d4d0c8',width=10,from_=1.0, to=0.00,orient=tkinter.VERTICAL,resolution=0.01,command=self.updatescale)#length=250
        self.intensitylo.pack(side=tkinter.TOP,fill='both',expand=1)
        fr=tkinter.Frame(nf,background='#d4d0c8')
        fr.pack(side=tkinter.LEFT,fill='both')
        lab=tkinter.Label(fr,text='Hi',width=3,anchor=tkinter.N,background='#d4d0c8')
        lab.pack(side=tkinter.TOP,fill='both')
        self.intenvarhi=tkinter.DoubleVar()
        self.intenvarhi.set(1.0)
        self.curinhi=1.0
        self.intensityhi=tkinter.Scale(fr,variable=self.intenvarhi,background='#d4d0c8',width=10,from_=1.0, to=0.01,orient=tkinter.VERTICAL,resolution=0.01,command=self.updatescale)#length=250
        self.intensityhi.pack(side=tkinter.TOP,fill='both',expand=1)
        #colormap selection
        nf=tkinter.Frame(h,background='#d4d0c8')
        nf.pack(side=tkinter.TOP,fill='both')
        self.colmap=Pmw.ComboBox(nf,
                        scrolledlist_items=ImCmap.maplist,dropdown=1,
                        labelpos='w',label_text='Colormaps',history=0,listheight=300,
                        selectioncommand=self.updatescale,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.colmap.selectitem('Jet',setentry=1)        
        self.colmap.pack(side=tkinter.LEFT,fill='x')
        self.colinvert=Pmw.RadioSelect(nf,buttontype='checkbutton',labelpos='w',command=self.updatescale,hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        self.colinvert.add('Invert? ',background='#d4d0c8')
        self.colinvert.pack(side=tkinter.LEFT,fill='both')
        self.collog=Pmw.RadioSelect(nf,buttontype='checkbutton',labelpos='w',command=self.updatescale,hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        self.collog.add('Log Scale? ',background='#d4d0c8')
        self.collog.pack(side=tkinter.LEFT,fill='both')
        #coordinates
        botfr=tkinter.Frame(h,background='#d4d0c8')        
        self.xcoord=tkinter.Label(botfr,text="X=      ",width=15,bd=2,relief=tkinter.RIDGE,anchor=tkinter.W,fg='red',background='#d4d0c8')
        self.ycoord=tkinter.Label(botfr,text="Y=      ",width=15,bd=2,relief=tkinter.RIDGE,anchor=tkinter.W,fg='red',background='#d4d0c8')
        self.zcoord=tkinter.Label(botfr,text="Z=      ",width=15,bd=2,relief=tkinter.RIDGE,anchor=tkinter.W,fg='red',background='#d4d0c8')
        self.zcoord.pack(side=tkinter.RIGHT,fill=tkinter.X)
        self.ycoord.pack(side=tkinter.RIGHT,fill=tkinter.X)
        self.xcoord.pack(side=tkinter.RIGHT,fill=tkinter.X)
        botfr.pack(side=tkinter.TOP,fill=tkinter.X)
        #setup scales
        self.xsc=[0,1]        
        self.ysc=[0,1]
        self.linegraphpresent=0
        self.linegraph2present=0
        self.linegraph3present=0
        self.linegraph4present=0
        self.legendimageexists=0
        self.xdir=1
        self.ydir=1
        ##self.xyflip=0
        self.mapaveragestatus=0
        self.mapavgpltpts=[]
        self.mapavgallpts=[]
        self.mapavgpts2avg=[]
        self.mapavglines=None
        self.xsectline=None
        #in theory this is the one and only time I initialize these lists
        self.defineZoom()
        self.clearzoom()
        self.allowresize=0
        self.scalebarx=10
        self.scalebary=10
        self.scalemaxlist={}
        self.markerlist={}
        self.markerexport=[]
        self.PMlock=threading.Lock()
        self.fittextresult=None
        self.CMYKOn=0
        self.roipoly=None
        if not show: 
            self.main.destroy()

    def defineZoom(self):
        self.zmxyi=[0,0,-1,-1,0,0]
        self.zmxyc = [0,0,0,0]        

    def updateROIDisp(self):
        self.updateDisp()
        self.editBindingB1(True)

    def editBindingB1(self,status):
        #print self.showMaskROI.get(), status
        if not status:
            self.imframe.unbind(sequence="<Button-1>")
            return
        if self.showMaskROI.get() and status:
            self.imframe.bind(sequence="<Button-1>",func=self.startdragMask)
        else:
            self.imframe.unbind(sequence="<Button-1>")
        
    def macbutton(self,event):
        if event.num>1: return
        if event.state==1: self.mapaverage(event)
        if event.state==4: self.addzoompt(event)
        if event.state==16: self.startxsection(event)        

    def macbuttonrelease(self,event):
        if event.num>1: return
        if event.state==4+256: self.finishzoom(event)
        if event.state==16+256: self.finishxsection(event)
  
    def closecallback(self):
        self.callback[0](self.callback[1])
        self.main.destroy()

    def extendmax(self):
        if self.datlab in list(self.scalemaxlist.keys()):
            sval=self.scalemaxlist[self.datlab]
        else:
            sval=max(np.ravel(self.raw))
        self.extdialog=Pmw.Dialog(self.master,title='Set Maximum Count Rate for Channel: '+self.datlab,buttons=('OK','Cancel','Default'),
                                  command=self.extdialogdone,defaultbutton='OK')
        h=self.extdialog.interior()

        self.extnewmax=Pmw.EntryField(h,labelpos='w',label_text='Max Value: ',validate='real',entry_width=15)
        self.extnewmax.setvalue(sval)
        self.extnewmax.pack(side=tkinter.TOP,padx=5,pady=10)
        self.extdialog.show()

    def extdialogdone(self,result):
        if result=='Cancel':
            self.extdialog.withdraw()
            return
        if result=='Default':
            if self.datlab in list(self.scalemaxlist.keys()):
                del self.scalemaxlist[self.datlab]
                self.extnewmax.setvalue(max(np.ravel(self.raw)))
        if result=='OK':
            self.scalemaxlist[self.datlab]=float(self.extnewmax.getvalue())
            self.extdialog.withdraw()
            self.placePPMimage(self.raw)
            if self.legendimageexists: self.viewcolormap()
            
    def showpopup(self,event):
        self.popmenu.post(event.x_root,event.y_root)

    def swapxdir(self):
        self.xdir=self.xdir*-1
        #self.xsc=self.xsc[::-1]
        self.updatescale()
        if self.tcrefresh is not None: self.tcrefresh()

    def swapydir(self):
        self.ydir=self.ydir*-1
        #self.ysc=self.ysc[::-1]
        self.updatescale()
        if self.tcrefresh is not None: self.tcrefresh()
        
    def swapxydir(self):
        self.flipVAR.set(not self.flipVAR.get())
        self.updatescale()
        if self.tcrefresh is not None: self.tcrefresh()
        
    def coordreport(self,event):
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasy(event.y)
        (imz,xind,yind)=self.datalookup(x,y)
        imx=self.xsc[xind]
        imy=self.ysc[yind]
        xtext="X="+str(imx)
        ytext="Y="+str(imy)
        ztext="Z="+globalfuncs.valueclip_d(imz,6)#str(imz)
        xtext=xtext[:12]
        ytext=ytext[:12]
        ztext=ztext[:12]
        globalfuncs.setstatus(self.xcoord,xtext)
        globalfuncs.setstatus(self.ycoord,ytext)
        globalfuncs.setstatus(self.zcoord,ztext)
        

    def datalookup(self,x,y,offs=True):
        global zdrag,zdrug
        if offs: x,y=x-3,y-3
        else: x,y=x+2,y-2
        xind=int(x/self.pixscale[0])
        yind=int(y/self.pixscale[1])
        if self.flipVAR.get():
            t=xind
            xind=yind
            yind=t
        ##OLD: if not zdrag:
        ##if self.zmxyi!=[0,0,-1,-1] and not zdrag:
        if self.iamzoomed:
            xind=xind+self.zmxyi[4]
            yind=yind+self.zmxyi[5]
        if xind<0: xind=0
        if yind<0: yind=0
        if xind>=self.raw.shape[0]: xind=self.raw.shape[0]-1
        if yind>=self.raw.shape[1]: yind=self.raw.shape[1]-1
        if self.xdir==-1:
            xind=self.raw.shape[0]-xind-1
        if self.ydir==-1:
            yind=self.raw.shape[1]-yind-1
        z=self.raw[xind,yind]
        return z,xind,yind

    def datainvcoords(self,x,y,index=False):
        if not index:
            x=float(x)
            y=float(y)
            xind=globalfuncs.indexme(self.xsc,x)
            yind=globalfuncs.indexme(self.ysc,y)
        else:
            xind=x
            yind=y
        if self.xdir==-1:
            xind=self.raw.shape[0]-xind-1
        if self.ydir==-1:
            yind=self.raw.shape[1]-yind-1
        #zoom problems???
        if self.zmxyi[0:4]!=[0,0,-1,-1]:
            if xind<self.zmxyi[0] or xind>self.zmxyi[2]:
                xind=-100
            else:
                xind=xind-self.zmxyi[0]
            if yind<self.zmxyi[1] or yind>self.zmxyi[3]:
                yind=-100
            else:
                yind=yind-self.zmxyi[1]
        if self.flipVAR.get():
            t=xind
            xind=yind
            yind=t
        xp=int(xind*self.pixscale[0])+3
        yp=int(yind*self.pixscale[1])+3
        return xp,yp

    def showlineplots(self,event):
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        (imz,xind,yind)=self.datalookup(x,y)
        imx=self.xsc[xind]
        imy=self.ysc[yind]
        xtext="X="+str(imx)
        ytext="Y="+str(imy)
        xtext=xtext[:10]
        ytext=ytext[:10]
        #define new window if needed
        if not self.linegraphpresent:
            self.xyplotcolorind=0
            self.xyplotcoords=[]
            self.linegraphpresent=1
            self.newlineplot=Pmw.MegaToplevel(self.master)
            self.newlineplot.title('Line Plot View')
            self.newlineplot.userdeletefunc(func=self.killlineplot)           
            h=self.newlineplot.interior()
            #JOY Q
            self.graphx=MyGraph.MyGraph(h,whsize=(4.5,4),side=tkinter.LEFT,padx=2,graphpos=[[.15,.1],[.9,.9]])
            #self.graphx.legend_configure(hide=1)
            #self.graphx.pack(side=tkinter.LEFT,expand=1,fill='both',padx=2)
            self.graphy=MyGraph.MyGraph(h,whsize=(4.5,4),side=tkinter.LEFT,padx=2,graphpos=[[.15,.1],[.9,.9]])
            #self.graphy.legend_configure(hide=1)
            #self.graphy.pack(side=tkinter.LEFT,expand=1,fill='both',padx=2)
        else:
            if self.toggleAddPlotVAR.get()==0:#clear old
                for gtype in (self.graphx,self.graphy):
                    gtype.cleargraphs()
                self.xyplotcolorind=0
                self.xyplotcoords=[]

##                glist=gtype.element_names()
##                if glist != ():
##                    for g in glist:
##                        gtype.element_delete(g)
            else:
                self.xyplotcolorind+=1
        #extract data
        if self.zmxyi[2]!=-1 and self.zmxyi[3]!=-1:
            xv=self.raw[self.zmxyi[0]:self.zmxyi[2],yind] 
            yv=self.raw[xind,self.zmxyi[1]:self.zmxyi[3]]
            xord=self.xsc[self.zmxyi[0]:self.zmxyi[2]]
            yord=self.ysc[self.zmxyi[1]:self.zmxyi[3]]
        else:            
            xv=self.raw[:,yind] 
            yv=self.raw[xind,:]
            xord=self.xsc
            yord=self.ysc
        #make graphs
        self.xyplotcoords.append([xtext,ytext])
        self.graphx.setTitle(xtext)
        #self.graphx.configure(title=xtext)
        colors=['green', 'cyan', 'white', 'orange','magenta', 'blue','brown']        
        colorplot=colors[self.xyplotcolorind%len(colors)]
        if self.toggleAddPlotVAR.get()==1:
            #JOY Q
            self.callback[3](xp=imx,yp=imy,color=matcolors.get_named_colors_mapping()[colorplot])
        self.graphx.plot(tuple(xord),tuple(xv),text='XV'+str(self.xyplotcolorind),color=colorplot)
        self.graphx.addMarker(imx,color='red')
        #self.graphx.line_create('XV',xdata=tuple(xord),ydata=tuple(xv),symbol='',color='green')        
        #self.graphx.line_create('XC',xdata=(imx,imx),ydata=(min(xv),max(xv)),symbol='',color='red')
#!        if self.xdir==-1:
#!            self.graphx.xaxis_configure(descending=1)
#!        else:
#!            self.graphx.xaxis_configure(descending=0)            
        #self.graphy.configure(title=ytext)
        self.graphy.setTitle(ytext)
        self.graphy.plot(tuple(yord),tuple(yv),text='YV'+str(self.xyplotcolorind),color=colorplot)
        self.graphy.addMarker(imy,color='red')
        #self.graphy.line_create('YV',xdata=tuple(yord),ydata=tuple(yv),symbol='',color='green')
        #self.graphy.line_create('YC',xdata=(imy,imy),ydata=(min(yv),max(yv)),symbol='',color='red')
#!        if self.ydir==-1:
#!            self.graphy.xaxis_configure(descending=1)
#!        else:
#!            self.graphy.xaxis_configure(descending=0)
        self.graphx.draw()
        self.graphy.draw()
        self.newlineplot.show()
        #for spectrum callback
        if self.callback[2] is not None:
            self.callback[2](self.mapindex[xind,yind])
        #for MCA viewing...
        if self.toggleVAR.get()==1:
            #get array position of clicked pixel...
            pixno=self.mapindex[xind,yind]#self.raw.shape[0]*(self.raw.shape[1]-yind-1)+xind
            self.viewFUNC(pixno,[],mcadir=1)

    def killlineplot(self):
        self.linegraphpresent=0
        self.newlineplot.destroy()

    def killlineplot2(self):
        self.linegraph2present=0
        self.newlineplot2.destroy()

    def killlineplot3(self):
        self.linegraph3present=0
        self.newlineplot3.destroy()

    def killlineplot4(self):
        self.linegraph4present=0
        self.newlineplot4.destroy()

    def getcolumn(self,event):
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        (imz,xind,yind)=self.datalookup(x,y)
        imy=self.ysc[yind]
        print(yind,imy,len(self.ysc)-yind-1)
        self.editBindingB1(True)#self.imframe.unbind(sequence="<Button-1>")
        if self.rowcb is not None:
            self.rowcb(len(self.ysc)-yind-1)

    def getrow(self,event):
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        (imz,xind,yind)=self.datalookup(x,y)
        imx=self.xsc[xind]
        print(xind,imx,len(self.xsc)-xind-1)
        self.editBindingB1(True)#self.imframe.unbind(sequence="<Button-1>")
        if self.rowcb is not None:
            self.rowcb(xind,forward=1)

    def mapaverage(self,event):
        self.domask=0
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        if self.mapaveragestatus==2:
            #clear
            self.mapavgpltpts=[]
            self.mapavgallpts=[]
            self.mapavgpts2avg=[]
            self.mapaveragestatus=0
            #delete line if present
            if self.mapavglines is not None:
                canvas.delete(self.mapavglines)
                self.mapavglines=None
                self.master.update_idletasks()
        (z,xi,yi)=self.datalookup(x,y)
        if self.MaskDrawType.get()=='Freeform':
            self.mapavgpltpts.append(x)
            self.mapavgpltpts.append(y)
            if len(self.mapavgpltpts)==2:
                self.mapavgpltpts.append(x)
                self.mapavgpltpts.append(y)
            self.mapavgallpts.append((xi,yi))
            #print 'sh-click',xi,yi
            #create new line if needed
            if not self.mapaveragestatus:
                self.mapavglines=canvas.create_line(tuple(self.mapavgpltpts),fill='white')
            else:
                canvas.coords(self.mapavglines,tuple(self.mapavgpltpts))
            self.mapaveragestatus=1
        if self.MaskDrawType.get()=='Rectangle':
            if self.mapaveragestatus==1:
                if len(self.mapavgpltpts)==4:
                    #add
                    self.mapavgpltpts[2]=x
                    self.mapavgpltpts[3]=self.mapavgpltpts[1]
                    self.mapavgpltpts.append(x)
                    self.mapavgpltpts.append(y)
                    self.mapavgpltpts.append(self.mapavgpltpts[0])
                    self.mapavgpltpts.append(y)
                    self.mapavgpltpts.append(self.mapavgpltpts[0])
                    self.mapavgpltpts.append(self.mapavgpltpts[1])
                    (x0,y0)=self.mapavgallpts[0]
                    self.mapavgallpts.append((xi, y0))
                    self.mapavgallpts.append((xi, yi))
                    self.mapavgallpts.append((x0, yi))
                else:
                    #edit last
                    self.mapavgpltpts[2]=x
                    self.mapavgpltpts[3]=self.mapavgpltpts[1]
                    self.mapavgpltpts[4]=x
                    self.mapavgpltpts[5]=y
                    self.mapavgpltpts[6]=self.mapavgpltpts[0]
                    self.mapavgpltpts[7]=y
                    self.mapavgpltpts[8]=self.mapavgpltpts[0]
                    self.mapavgpltpts[9]=self.mapavgpltpts[1]
                    (x0,y0)=self.mapavgallpts[0]
                    self.mapavgallpts[1]=(xi, y0)
                    self.mapavgallpts[2]=(xi, yi)
                    self.mapavgallpts[3]=(x0, yi)
            else:
                self.mapavgpltpts.append(x)
                self.mapavgpltpts.append(y)
                if len(self.mapavgpltpts)==2:
                    self.mapavgpltpts.append(x)
                    self.mapavgpltpts.append(y)
                self.mapavgallpts.append((xi,yi))
            if not self.mapaveragestatus:
                self.mapavglines=canvas.create_line(tuple(self.mapavgpltpts),fill='white')
            else:
                canvas.coords(self.mapavglines, tuple(self.mapavgpltpts))
            self.mapaveragestatus=1
        if self.MaskDrawType.get()=='Circle':
            if self.mapaveragestatus == 1:
                (xi0, yi0)=self.mapavgallpts[0]
                x0=self.mapavgpltpts[0]
                y0=self.mapavgpltpts[1]
                delx=(x-x0)**2
                dely=(y-y0)**2
                radius=math.sqrt(delx+dely)
                radiusi=math.sqrt((xi-xi0)**2+(yi-yi0)**2)
                self.mapavgallpts[1]=radiusi
                self.mapavgpltpts[2]=x0-radius
                self.mapavgpltpts[3]=y0-radius
                self.mapavgpltpts[4]=x0+radius
                self.mapavgpltpts[5]=y0+radius
                #print radius,radiusi
            else:
                self.mapavgpltpts.append(x)
                self.mapavgpltpts.append(y)
                if len(self.mapavgpltpts)==2:
                    self.mapavgpltpts.append(x)
                    self.mapavgpltpts.append(y)
                    self.mapavgpltpts.append(x)
                    self.mapavgpltpts.append(y)
                self.mapavgallpts.append((xi, yi))
                self.mapavgallpts.append(0)
            if not self.mapaveragestatus:
                self.mapavglines=canvas.create_oval(tuple(self.mapavgpltpts[2:]),width=1,outline='white')
            else:
                canvas.coords(self.mapavglines, tuple(self.mapavgpltpts[2:]))
            self.mapaveragestatus=1

    def finishmapaverage(self,event):
        #add point
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        (z,xi,yi)=self.datalookup(x,y)
        if self.MaskDrawType.get()=='Freeform':
            self.mapavgpltpts.append(x)
            self.mapavgpltpts.append(y)
            self.mapavgpltpts.append(self.mapavgpltpts[0])
            self.mapavgpltpts.append(self.mapavgpltpts[1])
            #print 'sh-click',xi,yi
            canvas.coords(self.mapavglines,tuple(self.mapavgpltpts))
        if self.MaskDrawType.get()=='Rectangle':
            pass #all good -- we're already done
        if self.MaskDrawType.get() == 'Circle':
            print(self.mapavgallpts)
        #find points
        self.mapavgpts2avg=[]
        exportmask=[]
        len_x, len_y=self.raw.shape[:2]
        for i in range(len_x):
            for j in range(len_y):
                if self.MaskDrawType.get() == 'Circle':
                    if self.domask and self.mask[i,j]:
                        if globalfuncs.point_inside_circle(i,j,self.mapavgallpts):
                            self.mapavgpts2avg.append(self.raw.shape[0]*(self.raw.shape[1]-j-1)+i)
                            exportmask.append([i,j])
                    elif not self.domask:
                        if globalfuncs.point_inside_circle(i,j,self.mapavgallpts):
                            self.mapavgpts2avg.append(self.raw.shape[0]*(self.raw.shape[1]-j-1)+i)
                            exportmask.append([i,j])
                else:
                    if self.domask and self.mask[i,j]:
                        if globalfuncs.point_inside_polygon(i,j,self.mapavgallpts):
                            self.mapavgpts2avg.append(self.raw.shape[0]*(self.raw.shape[1]-j-1)+i)
                            exportmask.append([i,j])
                    elif not self.domask:
                        if globalfuncs.point_inside_polygon(i,j,self.mapavgallpts):
                            self.mapavgpts2avg.append(self.raw.shape[0]*(self.raw.shape[1]-j-1)+i)
                            exportmask.append([i,j])
        print('maskpts',len(exportmask))
        #display average
        self.viewFUNC(self.mapavgpts2avg,exportmask,multi=1)
        #set status                    
        self.mapaveragestatus=2

    def makeNewPoints(self,data=None):
        new=[]
        if data==None:
            d=self.mapavgallpts
        else:
            d=data
        #print self.mapavgallpts
        #print self.mapavgpltpts
        if self.masktype=='Circle':
            cords=self.datainvcoords(d[0][0],d[0][1],index=True)
            new.append(cords[0])
            new.append(cords[1])
            cords2=self.datainvcoords(d[0][0]+d[1], d[0][1], index=True)
            radius=abs(cords2[0]-cords[0])
            #print radius
            new.append(cords[0] - radius)
            new.append(cords[1] - radius)
            new.append(cords[0] + radius)
            new.append(cords[1] + radius)
        else:
            for i in d:
                cords=self.datainvcoords(i[0],i[1],index=True)
                new.append(cords[0])
                new.append(cords[1])
        #print new
        return new

    def showROIpoly(self):
        if self.mapavgallpts == []: return
        if self.masktype=='Circle':
            properpts=self.makeNewPoints()
            self.roipoly=self.imframe.create_oval(tuple(properpts[2:]), outline='white', stipple='gray50')
        else:
            properpts=self.makeNewPoints()
            self.roipoly=self.imframe.create_polygon(tuple(properpts),outline='white',stipple='gray50')

    def applyDeltaROIpoly(self,delta,co=False):
        print(delta)
        newpts=[]
        i=0
        if not co:   #NO CIRCLE HERE YET
            ardata=self.mapavgpltpts
            for v in ardata:
                if i%2==0:
                    newpts.append(v+delta[0])
                else:
                    newpts.append(v+delta[1])
                i+=1
        else:
            ardata=self.mapavgallpts
            if self.masktype == 'Circle':
                newpts=list(ardata)
                newpts[0]=(ardata[0][0]+delta[0],ardata[0][1]+delta[1])
            else:
                for v in ardata:
                    newpts.append((v[0]+delta[0],v[1]+delta[1]))
        if co:
            self.imframe.delete(self.roipoly)
            if self.masktype=='Circle':
                properpts=self.makeNewPoints(data=newpts)
                self.roipoly=self.imframe.create_oval(tuple(properpts[2:]), outline='red', stipple='gray50')
            else:
                properpts=self.makeNewPoints(data=newpts)
                self.roipoly=self.imframe.create_polygon(tuple(properpts),outline='red',stipple='gray50')
        else: #NO CIRCLE HERE YET
            if self.masktype=='Circle':
                pass
            else:
                self.imframe.delete(self.roipoly)
                self.roipoly=self.imframe.create_polygon(tuple(newpts),outline='red',stipple='gray50')
        return newpts

    def maskAffinetransform(self):
        #check for mask
        if self.mapavgallpts==[]:
            print('no mask present')
            return
        self.affmaskdialog=Pmw.Dialog(self.master, title='Perform Mask Affine Transform',
                                    buttons=('OK', 'Cancel', 'Default'),
                                    command=self.affmaskdialogdone, defaultbutton='Cancel')
        h=self.affmaskdialog.interior()

        self.mafftransx=Pmw.EntryField(h, labelpos='w', label_text='Translate X: ', validate='real', entry_width=15, value=0)
        self.mafftransx.pack(side=tkinter.TOP, padx=5, pady=10)
        self.mafftransy=Pmw.EntryField(h, labelpos='w', label_text='Translate Y: ', validate='real', entry_width=15, value=0)
        self.mafftransy.pack(side=tkinter.TOP, padx=5, pady=10)
        self.maffscale=Pmw.EntryField(h, labelpos='w', label_text='Scale: ', validate='real', entry_width=15, value=1)
        self.maffscale.pack(side=tkinter.TOP, padx=5, pady=10)
        self.maffrotate=Pmw.EntryField(h, labelpos='w', label_text='Rotation: ', validate='real', entry_width=15, value=0)
        self.maffrotate.pack(side=tkinter.TOP, padx=5, pady=10)
        Pmw.alignlabels([self.mafftransx,self.mafftransy,self.maffscale,self.maffrotate])
        self.affmaskdialog.show()

    def affmaskdialogdone(self,result):
        if result=='Cancel':
            self.affmaskdialog.withdraw()
            return
        if result=='Default':
            init=[0,0,1,0]
            wid=[self.mafftransx,self.mafftransy,self.maffscale,self.maffrotate]
            for v,w in zip(init,wid):
                w.setvalue(v)
            return
        #do work (result=='ok')
        aftransvals=[]
        for w in [self.mafftransx,self.mafftransy,self.maffscale,self.maffrotate]:
            aftransvals.append(float(w.getvalue()))
        self.affmaskdialog.withdraw()
        #if circle, then treat differently...
        if self.masktype=='Circle':
            #easier transformation -- rotation is irrelevant
            self.mapavgallpts[0]=(self.mapavgallpts[0][0]+aftransvals[0],self.mapavgallpts[0][1]+aftransvals[1])
            self.mapavgallpts[1]=self.mapavgallpts[1]*aftransvals[2]
        else:
            #more complicated
            #calculate center
            pc=globalfuncs.polygon_centroid(self.mapavgallpts)
            #transform center to origin
            ctrans=[-pc[0],-pc[1],1,0]
            cbtrans=[pc[0], pc[1], 1, 0]
            centered=globalfuncs.perform_affine_transform(self.mapavgallpts,ctrans)
            #do affine
            transformed=globalfuncs.perform_affine_transform(centered,aftransvals)
            #translate back
            self.mapavgallpts=globalfuncs.perform_affine_transform(transformed,cbtrans)
        #update display and mask
        #print self.mapavgallpts
        self.mapavgpts2avg=[]
        exportmask=[]
        len_x, len_y=self.raw.shape[:2]
        for i in range(len_x):
            for j in range(len_y):
                if self.masktype == 'Circle':
                    if globalfuncs.point_inside_circle(i, j, self.mapavgallpts):
                        self.mapavgpts2avg.append(self.raw.shape[0] * (self.raw.shape[1] - j - 1) + i)
                        exportmask.append([i, j])
                else:
                    if globalfuncs.point_inside_polygon(i, j, self.mapavgallpts):
                        self.mapavgpts2avg.append(self.raw.shape[0] * (self.raw.shape[1] - j - 1) + i)
                        exportmask.append([i, j])
        # display average
        print('AFFmaskpts',len(exportmask))
        self.viewFUNC(self.mapavgpts2avg, exportmask, multi=2)
        self.updateDisp()

    def setList(self, list1, list2):
        if len(list1) == len(list2):
            for i in range(len(list2)):
                list1[i] = list2[i]
        else:
            print("Lists not same length")

    def edgezoom(self,disp=1):
        self.zoomline=None
        ##self.iamzoomed+=1
        ##self.zmxyi=[self.iamzoomed,self.iamzoomed,self.raw.shape[0]-1-self.iamzoomed,self.raw.shape[1]-1-self.iamzoomed]
        if not self.iamzoomed:
            globalfuncs.setList(self.zmxyi,[1,1,self.raw.shape[0]-2,self.raw.shape[1]-2,0,0])
        else:
            globalfuncs.setList(self.zmxyi,[self.zmxyi[0]+1,self.zmxyi[1]+1,self.zmxyi[2]-1,self.zmxyi[3]-1,0,0])
        self.iamzoomed=1            
        globalfuncs.setList(self.zmxyc,[0,0,0,0])
        if disp:
            #update display
            try:
                self.placePPMimage(self.raw)
            except:
                pass
            if self.tcrefresh is not None: self.tcrefresh()        

    def clearzoom(self,disp=1):
        global zdrag,zdrug
        zdrag=0
        zdrug=0
        self.zoomline=None
        globalfuncs.setList(self.zmxyi, [0,0,-1,-1,0,0])
        globalfuncs.setList(self.zmxyc, [0,0,0,0])
        self.iamzoomed=0
        self.editBindingB1(True)
        if disp:
            #update display
            try:
                self.placePPMimage(self.raw)
            except:
                pass
            if self.tcrefresh is not None: self.tcrefresh()

    def addzoompt(self,event):
        global zdrag,zdrug
        zdrag=1
        zdrug=0
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        globalfuncs.setList(self.zmxyc,[x,y,x,y])
        (z,xi,yi)=self.datalookup(x,y)
        if self.iamzoomed:
            self.zmxyi[4]=self.zmxyi[0]
            self.zmxyi[5]=self.zmxyi[1]           
            self.zmxyi[0]=xi
            self.zmxyi[1]=yi
            self.zmxyi[2]=0
            self.zmxyi[3]=0
        else:
            globalfuncs.setList(self.zmxyi,[xi,yi,0,0,xi,yi])
        #print x,y,self.zmx0,self.zmy0
        #create zoom line
        self.zoomline=self.imframe.create_rectangle(tuple(self.zmxyc),width=2,outline='grey50')
        #create binding
        self.imframe.bind(sequence="<Motion>",func=self.zoomdrag)

    def zoomdrag(self,event):
        global zdrag,zdrug
        zdrug=1
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        self.zmxyc[2]=x
        self.zmxyc[3]=y
        (z,xi,yi)=self.datalookup(x,y)
        self.zmxyi[2]=xi
        self.zmxyi[3]=yi
        #update zoom line
        self.imframe.coords(self.zoomline,tuple(self.zmxyc))
        self.coordreport(event)
        
    def finishzoom(self,event):
        global zdrag,zdrug
        if zdrag:
            self.imframe.unbind(sequence="<Motion>")
            self.imframe.bind(sequence="<Motion>", func=self.coordreport)
            #delete zoom line
            self.imframe.delete(self.zoomline)
            if zdrug:
                #print self.zmxyc,self.zmxyi
                if self.zmxyi[0]>self.zmxyi[2]:
                    self.zmxyi[0],self.zmxyi[2]=self.zmxyi[2],self.zmxyi[0]
                self.zmxyi[4]=self.zmxyi[0]
                if self.zmxyi[1]>self.zmxyi[3]:
                    self.zmxyi[1],self.zmxyi[3]=self.zmxyi[3],self.zmxyi[1] 
                self.zmxyi[5]=self.zmxyi[1]
                #update display
                #print self.zmxyc,self.zmxyi
                self.placePPMimage(self.raw)
                if self.tcrefresh is not None: self.tcrefresh()
        zdrag=0
        zdrug=0
        self.iamzoomed=1

    def shiftzoompos(self,event):
        if not self.iamzoomed:
            print('no zoom')
            return
        if event.keysym=='Up':
            if self.zmxyi[1]!=0:
                self.zmxyi[1]=self.zmxyi[1]-1
                self.zmxyi[3]=self.zmxyi[3]-1
            else:
                return
        if event.keysym=='Down':
            if self.zmxyi[3]!=len(self.ysc):
                self.zmxyi[1]=self.zmxyi[1]+1
                self.zmxyi[3]=self.zmxyi[3]+1
            else:
                return
        if event.keysym=='Left':
            if self.zmxyi[0]!=0:
                self.zmxyi[0]=self.zmxyi[0]-1
                self.zmxyi[2]=self.zmxyi[2]-1
            else:
                return
        if event.keysym=='Right':
            if self.zmxyi[2]!=len(self.xsc):
                self.zmxyi[0]=self.zmxyi[0]+1
                self.zmxyi[2]=self.zmxyi[2]+1
            else:
                return            
        self.placePPMimage(self.raw)
        if self.tcrefresh is not None: self.tcrefresh()

    def startdragMask(self,event):
        global mdrag,mdrug
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        (z,xi,yi)=self.datalookup(x,y)
        if self.masktype=='Circle':
            if not globalfuncs.point_inside_circle(xi,yi,self.mapavgallpts):
                return
        else:
            if not globalfuncs.point_inside_polygon(xi,yi,self.mapavgallpts):
                return
        mdrag=1
        mdrug=0
        self.mdxyc=[x,y,x,y,xi,yi,xi,yi]
        self.applyDeltaROIpoly([0,0],co=True)
        self.imframe.bind(sequence="<Motion>",func=self.mroidrag)
        self.editBindingB1(False)
        self.imframe.bind(sequence="<Button-1>",func=self.finishmroidrag)
        
    def mroidrag(self,event):
        global mdrag,mdrug
        mdrug=1
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        (z,xi,yi)=self.datalookup(x,y)
        self.mdxyc[2]=x
        self.mdxyc[3]=y
        self.mdxyc[6]=xi
        self.mdxyc[7]=yi
        delta=[self.mdxyc[2]-self.mdxyc[0],self.mdxyc[3]-self.mdxyc[1]]
        deltai=[self.mdxyc[6]-self.mdxyc[4],self.mdxyc[7]-self.mdxyc[5]]
        #move object
        newallpts=self.applyDeltaROIpoly(deltai,co=True)
        self.coordreport(event)
        if self.showMaskROIUpdates.get(): 
            return
            newmapavgpts2avg=[]
            exportmask=[]
            len_x, len_y=self.raw.shape[:2]
            for i in range(len_x):
                for j in range(len_y):
                    if self.masktype=='Circle':
                        if globalfuncs.point_inside_circle(i, j, newallpts):
                            self.mapavgpts2avg.append(self.raw.shape[0] * (self.raw.shape[1] - j - 1) + i)
                            exportmask.append([i, j])
                    else:
                        if globalfuncs.point_inside_polygon(i,j,newallpts):
                            newmapavgpts2avg.append(self.raw.shape[0]*(self.raw.shape[1]-j-1)+i)
                            exportmask.append([i,j])
            self.viewFUNC(newmapavgpts2avg,exportmask,multi=3)
        
    def finishmroidrag(self,event):
        global mdrag,mdrug
        if mdrag:
            self.imframe.unbind(sequence="<Motion>")
            self.imframe.bind(sequence="<Motion>", func=self.coordreport)
            if mdrug:
                #do the move and calculate!
                delta=[self.mdxyc[2]-self.mdxyc[0],self.mdxyc[3]-self.mdxyc[1]]
                deltai=[self.mdxyc[6]-self.mdxyc[4],self.mdxyc[7]-self.mdxyc[5]]

                #self.mapavgpltpts=self.applyDeltaROIpoly(delta)
                self.mapavgallpts=self.applyDeltaROIpoly(deltai,co=True)

                self.mapavgpts2avg=[]
                exportmask=[]
                len_x, len_y=self.raw.shape[:2]
                for i in range(len_x):
                    for j in range(len_y):
                        if self.masktype=='Circle':
                            if globalfuncs.point_inside_circle(i, j, self.mapavgallpts):
                                self.mapavgpts2avg.append(self.raw.shape[0] * (self.raw.shape[1] - j - 1) + i)
                                exportmask.append([i, j])
                        else:
                            if globalfuncs.point_inside_polygon(i,j,self.mapavgallpts):
                                self.mapavgpts2avg.append(self.raw.shape[0]*(self.raw.shape[1]-j-1)+i)
                                exportmask.append([i,j])
                #display average
                self.viewFUNC(self.mapavgpts2avg,exportmask,multi=2)

        self.editBindingB1(True)       
        mdrag=0
        mdrug=0        

    def startxsection(self,event):
        print('XS')
        global xdrag, xdrug
        #print 'start'
        #delete zoom line
        if self.xsectline is not None:
            self.imframe.delete(self.xsectline)
        xdrag=1
        xdrug=0
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        self.xsxyc=[x,y,x,y]
        (z,xi,yi)=self.datalookup(x,y)
        self.xsxyi=[xi,yi,0,0]
        #create xsection line
        self.xsectline=self.imframe.create_line(tuple(self.xsxyc),width=2,fill='grey50')
        #create binding
        self.imframe.bind(sequence="<Motion>",func=self.xsectdrag)

    def xsectdrag(self,event):
        #print 'moving'
        global xdrag,xdrug
        xdrug=1
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        self.xsxyc[2]=x
        self.xsxyc[3]=y
        (z,xi,yi)=self.datalookup(x,y)
        self.xsxyi[2]=xi
        self.xsxyi[3]=yi
        #update zoom line
        self.imframe.coords(self.xsectline,tuple(self.xsxyc))
        self.coordreport(event)

    def finishxsection(self,event):
       # print 'finishing'
        global xdrag,xdrug
        if xdrag:
            self.imframe.unbind(sequence="<Motion>")
            self.imframe.bind(sequence="<Motion>", func=self.coordreport)
            if xdrug:
                #do the xsection!
                #calculate slope/intercept
                try:
                    slope=float(self.xsxyi[1]-self.xsxyi[3])/float(self.xsxyi[0]-self.xsxyi[2])
                except:
                    print('vertical line')
                    return
                b=self.xsxyi[1]-slope*self.xsxyi[0]
                #make grids
                dx=self.xsxyi[2]-self.xsxyi[0]
                dx=dx/abs(dx)
                dy=self.xsxyi[3]-self.xsxyi[1]
                dy=dy/abs(dy)
                print(slope,b,dx,dy)
                #print nx,ny
                gridxi=list(range(int(self.xsxyi[0]),int(self.xsxyi[2]+1),int(dx)))
                gridyi=list(range(int(self.xsxyi[1]),int(self.xsxyi[3]+1),int(dy)))


                if self.callback[4]==None: 
                    print ('no xs calc function')
                    return
                xv,yv,nxs = self.callback[4](gridxi,gridyi,self.xsc,self.ysc,slope,b)

                # for i in gridxi:
                #     gridxc.append(self.xsc[i])
                #     newc=slope*i+b
                #     ip=int(math.ceil(newc))
                #     im=int(math.floor(newc))
                #     f1=newc-im
                #     f2=ip-newc
                #     t=ip-im
                #     #print i,newc,ip,im
                #     #print f1,f2,t
                #     if t!=0:
                #         gridyc.append((self.ysc[im]*f1+self.ysc[ip]*f2)/t)
                #         gridz.append((self.raw[i,im]*f1+self.raw[i,ip]*f2)/t)
                #     else:
                #         gridyc.append(self.ysc[int(newc)])
                #         gridz.append(self.raw[i,int(newc)])
                #     griddc.append(math.sqrt((gridxc[len(gridxc)-1]-gridxc[0])**2+(gridyc[len(gridyc)-1]-gridyc[0])**2))
                # #repeat for y's
                # for i in gridyi:
                #     try:
                #         newc=(i-b)/slope
                #     except:
                #         continue
                #     gridyc.append(self.ysc[i])
                #     ip=int(math.ceil(newc))
                #     im=int(math.floor(newc))
                #     f1=newc-im
                #     f2=ip-newc
                #     t=ip-im
                #     #print i,newc,ip,im
                #     #print f1,f2,t
                #     if t!=0:
                #         gridxc.append((self.xsc[im]*f1+self.xsc[ip]*f2)/t)
                #         gridz.append((self.raw[im,i]*f1+self.raw[ip,i]*f2)/t)
                #     else:
                #         gridxc.append(self.xsc[int(newc)])
                #         gridz.append(self.raw[int(newc),i])
                #     griddc.append(math.sqrt((gridxc[len(gridxc)-1]-gridxc[0])**2+(gridyc[len(gridyc)-1]-gridyc[0])**2))
                # #order
                # ind=np.argsort(griddc)
                # xv=np.take(griddc,ind,axis=0)
                # yv=np.take(gridz,ind,axis=0)
                
                
                #do plot
                #define new window if needed
                if not self.linegraph2present:
                    self.linegraph2present=1
                    self.newlineplot2=Pmw.MegaToplevel(self.master)
                    self.newlineplot2.title('Line Plot View')
                    self.newlineplot2.userdeletefunc(func=self.killlineplot2)           
                    h=self.newlineplot2.interior()
                    #JOY Q
                    self.graphx2=MyGraph.MyGraph(h,whsize=(4.5,4),graphpos=[[.15,.1],[.9,.9]])
                    #self.graphx2.legend_configure(hide=1)
                    #self.graphx2.pack(side=tkinter.LEFT,expand=1,fill='both',padx=2)
                else:
                    #clear old
                    self.newlineplot2.title('Line Plot View')
                    self.graphx2.cleargraphs()
##                    for gtype in (self.graphx2,):
##                        glist=gtype.element_names()
##                        if glist != ():
##                            for g in glist:
##                                gtype.element_delete(g)            
                #make graphs
                #self.graphx2.configure(title=xtext)
                #self.graphx2.line_create('XV',xdata=tuple(xv),ydata=tuple(yv),symbol='',color='green')        
                if nxs==1:
                    self.graphx2.plot(tuple(xv),tuple(yv),color='green',text='XV')
                else:
                    colors=['green', 'cyan', 'white', 'orange','magenta', 'blue','brown']        
                    i=0
                    for pd in yv:
                        colorplot=colors[i%len(colors)]
                        self.graphx2.plot(tuple(xv),tuple(pd),color=colorplot,text='XV'+str(i))
                        i+=1

                self.graphx2.draw()
                self.newlineplot2.show()
                 
        xdrag=0
        xdrug=0
        #FIT?
        print(self.FitLineProf.get())
        if self.FitLineProf.get()!="None":
            #passdata=[]
            #for i in range(len(xv)):
            #    passdata.append((xv[i],yv[i]))
            if self.FitLineProf.get()=="Linear":
                initguess=(0,min(yv))
                fe=globalfuncs.linearFit
                fe2=globalfuncs.lineareqn
                print("fitting linear...",initguess)
            if self.FitLineProf.get()=="Gauss":               
                initguess=(1,(xv[-1]-xv[0])/2+xv[0],(xv[-1]-xv[0])/4,min(yv))
                fe=globalfuncs.gaussFit
                fe2=globalfuncs.gausseqn
                print("fitting gauss...",initguess)
            if self.FitLineProf.get()=="Gauss+Lin":
                initguess=(1,(xv[-1]-xv[0])/2+xv[0],(xv[-1]-xv[0])/4,0,min(yv))
                fe=globalfuncs.gausslineFit
                fe2=globalfuncs.gausseqnline
                print("fitting gauss+linear...",initguess)                
            try:
                #result=leastSquaresFit(fe,initguess,passdata)#globalfuncs.gausseqnline,globalfuncs.lineareqn
                result,cov=curve_fit(fe,xv,yv,p0=initguess)
                fp=result
            except:
                fp=(0,0,1,0,0)
                print("err")
            print("fit: ",fp)
            if self.FitLineProf.get()[0]=='G': print('FWHM: ',2.35482*fp[2])
            gfit=fe2(fp,xv)
            #self.graphx2.line_create('XVf',xdata=tuple(xv),ydata=tuple(gfit),symbol='',color='red')   
            self.graphx2.plot(tuple(xv),tuple(gfit),text='XVf',color='red')
            self.graphx2.draw()
            print("done")            

    def saveZasPSF(self):
        if self.zmxyi[2]!=-1 and self.zmxyi[3]!=-1:
            self.savedPSF=self.raw[self.zmxyi[0]:self.zmxyi[2],self.zmxyi[1]:self.zmxyi[3]] 
            print('done',self.savedPSF.shape)
        else:      
            print("should use zoomed area please....")
            self.savedPSF=np.zeros((3,3))
            return

    def placeData(self,data,mapindex,status,scales=(None,None),xax=None,yax=None,domask=0,mask=[],datlab='',returnonly=False,forceColor=None,sc=True):
        if sc is True:
            if self.scalefact is None:
                self.imgSF=1.0
            else:
                self.imgSF=float(self.scalefact.get()[:-1])
        else:
            self.imgSF=1.0
        self.raw=data
        self.datlab=datlab
        self.mapindex=mapindex
        self.mainstatus=status
        self.xsc=xax
        self.ysc=yax[::-1]
        self.domask=domask
        self.mask=mask
        self.forceColor=forceColor
        img=self.placePPMimage(data,scales,returnonly=returnonly)
        if self.legendimageexists:
            self.viewcolormap()
        return img
##        future?
##        plt.matshow(data)
##        plt.show()

    def updateDisp(self,*args):
        self.placePPMimage(self.raw)

    def placePPMimage(self,data,scales=(None,None),movie=0,frame=0,returnonly=False,forceData=False):
##        t=time.process_time()
        self.xsectline=None
        globalfuncs.setstatus(self.mainstatus,"WORKING...")

        if not returnonly:
            if (movie and frame):
                self.main.title('Image Display of '+self.datlab+' '+str(frame*10))
            else:
                self.main.title('Image Display of '+self.datlab)

        if not forceData:
            #take section?
            if self.zmxyi[2]!=-1 and self.zmxyi[3]!=-1:
                if not movie:
                    data=self.raw[self.zmxyi[0]:self.zmxyi[2],self.zmxyi[1]:self.zmxyi[3]]
                else:
                    data=self.raw[self.framecount,self.zmxyi[0]:self.zmxyi[2],self.zmxyi[1]:self.zmxyi[3]]                
            else:
                if not movie:
                    data=self.raw
                else:
                    data=self.raw[self.framecount,:,:]
            #reverse scales if needed.
            data=data[::self.xdir,::self.ydir]
            #take log if needed
            if self.collog.getvalue()!=():
                data=np.log(abs(data)+1)
            #scale image
            hival=self.intenvarhi.get()
            if self.datlab in list(self.scalemaxlist.keys()):
                #JOY Q
                hival=self.scalemaxlist[self.datlab]/max(np.ravel(data))*self.intenvarhi.get()
            image, (scalex,scaley)=preprocess(self.master,data, scales, hival,cutlo=self.intenvarlo.get())
            if self.apply45Calc.get()==1: scalex=scalex*math.sqrt(2)

            #check for scale
            if self.imgSF!=1:
#                image=skrescale(image,(self.imgSF,self.imgSF),mode='edge')
                scalex=scalex*self.imgSF
                scaley=scaley*self.imgSF
            self.pixscale=(scalex,scaley)
            #check for mask
            if self.domask and len(self.mask)!=0:
                if self.zmxyi[2]!=-1 and self.zmxyi[3]!=-1:
                    image=image*(self.mask[self.zmxyi[0]:self.zmxyi[2],self.zmxyi[1]:self.zmxyi[3]])
                else:
                    image=image*self.mask
                image=image.astype('b')
            #check for flip
            if self.flipVAR.get(): image=np.transpose(image)

            if 1:
                pilim=ImRadon.toimage(np.transpose(image),pal=self.getcolormap(),cmin=0,skip=1)
                if returnonly:
                    self.saveobj.append(pilim)
                else:
                    self.savobj=pilim                
            else:       
                #apply colormap
                image=self.applycolormap(image)
                #convert to ppm
                ppm=globalfuncs.array2ppm(image)
                self.savobj=ppm
                pilim=Image.open(globalfuncs.save_ppm(ppm))
            (w,h)=pilim.size
    #        self.oimage=PhotoImage(file=save_ppm(ppm))
    #        wo, ho=self.oimage.width(), self.oimage.height()
            if returnonly: 
                return pilim
        else:
            pilim=data
            (w,h)=pilim.size
            (scalex,scaley)=self.pixscale
#        self.image=self.image.zoom(scalex, scaley)
        #self.image.configure(width=int(w*scalex), height=int(h*scaley))
        pilim=pilim.resize((int(w*scalex),int(h*scaley)))
        self.image=ImageTk.PhotoImage(pilim)
        #clear
        if self.items !=[] : self.imframe.delete(self.items.pop())
        #remove scales if present
        for i in self.scaleitems:
            self.scaleframe.delete(i)
        self.scaleitems=[]        
        #rescale canvas and slider
        if self.viewscaleVAR.get():
            #add edge
            self.scaleframe.config(height=int(h*scaley)+40,width=int(w*scalex)+80)
            self.scaleframe.coords(self.scaleframewid,20,20)
            #find edge coords:
            if self.zmxyi[0:4]==[0,0,-1,-1]:
                hsc=globalfuncs.frange(self.xsc[0],self.xsc[-1],(self.xsc[-1]-self.xsc[0])/5)
                vsc=globalfuncs.frange(self.ysc[0],self.ysc[-1],(self.ysc[-1]-self.ysc[0])/5)
            else:
                hsc=globalfuncs.frange(self.xsc[self.zmxyi[0]],self.xsc[self.zmxyi[2]],(self.xsc[self.zmxyi[2]]-self.xsc[self.zmxyi[0]])/5)
                vsc=globalfuncs.frange(self.ysc[self.zmxyi[1]],self.ysc[self.zmxyi[3]],(self.ysc[self.zmxyi[3]]-self.ysc[self.zmxyi[1]])/5)
            #add scales
            if self.flipVAR.get():
                temp=hsc
                hsc=vsc
                vsc=temp
            #worry about sig figs?
            hsclab=[]
            vsclab=[]
            for i in hsc:
                hsclab.append(str(i))
            for i in vsc:
                vsclab.append(str(i))
            itpos=23
            tpos=itpos
            hvp=20+int(w*scaley)+5
            for s in vsclab:
                self.scaleitems.append(self.scaleframe.create_text(hvp+4,tpos+7,text=s,fill='white',anchor='w'))
                self.scaleitems.append(self.scaleframe.create_line(hvp,tpos,hvp+8,tpos,fill='white'))
                tpos=tpos+int(h*scaley)/5
            #vert
            self.scaleitems.append(self.scaleframe.create_line(hvp,itpos,hvp,tpos-int(h*scaley)/5,fill='white'))
            tpos=itpos
            for s in hsclab:
                self.scaleitems.append(self.scaleframe.create_text(tpos+3,10,text=s,fill='white',anchor='w'))
                self.scaleitems.append(self.scaleframe.create_line(tpos,10,tpos,18,fill='white'))
                tpos=tpos+int(w*scaley)/5            
            #horz
            self.scaleitems.append(self.scaleframe.create_line(itpos,18,tpos-int(w*scaley)/5,18,fill='white'))
        else:
            self.scaleframe.config(height=int(h*scaley)+0,width=int(w*scalex)+0)
            self.scaleframe.coords(self.scaleframewid,0,0)
        self.imframe.config(height=int(h*scaley),width=int(w*scalex))
        self.items.append(self.imframe.create_image((int(w*scalex+scalex))/2,(int(h*scaley+scaley))/2,anchor='center', image=self.image))

        #add scalebar if necessary
        if self.scaleVAR.get(): self.addscalebartodisplay()
        if not self.scaleVAR.get(): self.removescalebarfromdisplay()
        #add markers?
        self.addallmarkers()
        if self.showMaskROI.get(): self.showROIpoly()
        else:
            if self.roipoly!=None:
                self.imframe.delete(self.roipoly)
                self.roipoly=None
        self.main.update_idletasks()
        g=self.main.geometry()
        newg=str(self.main.winfo_reqwidth())+'x'+str(self.main.winfo_reqheight())+'+'+g.split('+')[1]+'+'+g.split('+')[2]
        self.main.geometry(newg)
        self.main.update_idletasks()

        #check for update on colormap
        if self.legendimageexists: self.viewcolormap()
        
        globalfuncs.setstatus(self.mainstatus,"Ready")
##        print (time.process_time()-t)

    def placescalebardialog(self):
        #ask for mouse input
        if tkinter.messagebox.askokcancel('Scale Bar','Click on desired position of scalebar'):
            #bind canvas
            self.editBindingB1(False)
            self.imframe.bind(sequence='<Button-1>',func=self.placescalebar)

    def placescalebar(self,event):
        #remove binding
        self.editBindingB1(True)#self.imframe.unbind(sequence='<Button-1>')
        self.scalebarx=event.x
        self.scalebary=event.y
        self.placePPMimage(self.raw)
        if self.tcrefresh is not None: self.tcrefresh()

    def defaultscalebar(self):
        self.scalebarx=10
        self.scalebary=10
        self.placePPMimage(self.raw)
        if self.tcrefresh is not None: self.tcrefresh()        

    def addscalebartodisplay(self):
        #calculate size
        w, h=self.image.width(), self.image.height()
        sbwp=w*.1
        first=self.xsc[self.zmxyi[0]]
        last=self.xsc[self.zmxyi[2]]
        sbwm=abs(first-last)*.1*1000
        if self.apply45Calc.get()==1: sbwm=sbwm*math.sqrt(2)
        scl=sbwp/sbwm
        sbwr=globalfuncs.chop(sbwm,0.1)
        sbwp=sbwr*scl
        #print sbwp,sbwm
        self.sbid=self.imframe.create_rectangle(self.scalebarx,self.scalebary,self.scalebarx+sbwp,self.scalebary+10,fill='white')
        if self.scaleTextVAR.get(): self.sbtext=self.imframe.create_text(self.scalebarx+10+sbwp,self.scalebary+5,anchor=tkinter.W,fill='white',text=str(int(sbwr)))

    def removescalebarfromdisplay(self):
        try:
            self.sbid.delete()
        except:
            pass
        try:
            self.sbtext.delete()
        except:
            pass

    def startPMgetpos(self):        
        self.editBindingB1(False)
        self.imframe.bind(sequence='<Button-1>',func=self.exportPMpos)

    def exportPMpos(self,event):
        #remove binding
        self.editBindingB1(True)#self.imframe.unbind(sequence='<Button-1>')
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        (imz,xind,yind)=self.datalookup(x,y)
        imx=self.xsc[xind]
        imy=self.ysc[yind]
        self.markerexport=[imx,imy]
        self.PMlock.release()

    def markerupdate(self,obj,add=1): #self.markerlist{}
        #see if obj in list
        if obj in list(self.markerlist.keys()):
            #delete
            if self.markerlist[obj] is not None: self.imframe.delete(self.markerlist[obj])
            self.markerlist[obj]=None
        if not add: return
        #find pos (xpos,ypos)
        (xp,yp)=self.datainvcoords(obj.xpos.getvalue(),obj.ypos.getvalue())
        mref=None
        #add new obj #color
            #markertypes=['sm circle','big circle','sm square','big square','sm triangle','big triangle','text'] marker.getvalue()[0]
        if obj.marker.getvalue()[0]=='text':
            #text placement
            mref=self.imframe.create_text(xp,yp,anchor=tkinter.W,fill=obj.color,text=obj.textfield.getvalue())
        else:
            ms=obj.marker.getvalue()[0].split()[0]
            mt=obj.marker.getvalue()[0].split()[1]
            sz=4
            if ms=='big': sz=8
            if mt=='emptycircle':
                mref=self.imframe.create_oval(xp-sz,yp-sz,xp+sz,yp+sz,outline=obj.color)
            if mt=='circle':
                mref=self.imframe.create_oval(xp-sz,yp-sz,xp+sz,yp+sz,fill=obj.color)
            if mt=='emptysquare':
                mref=self.imframe.create_rectangle(xp-sz,yp-sz,xp+sz,yp+sz,outline=obj.color)
            if mt=='square':
                mref=self.imframe.create_rectangle(xp-sz,yp-sz,xp+sz,yp+sz,fill=obj.color)
            if mt=='triangle':
                mref=self.imframe.create_polygon(xp-sz,yp-sz,xp+sz,yp-sz,xp,yp+sz,fill=obj.color,outline='black')
        if mref is not None: self.markerlist[obj]=mref

    def addallmarkers(self):
        for m in list(self.markerlist.keys()):
            if self.markerlist[m] is not None: self.markerupdate(m)
          
    def updatescale(self,*args):
        if args!=() and len(args)==1:
            if args[0] not in ImCmap.maplist:                
                if self.curinhi==self.intenvarhi.get() and self.curinlo==self.intenvarlo.get():
                    return
        self.curinhi=self.intenvarhi.get()
        self.curinlo=self.intenvarlo.get()
        try:
            self.placePPMimage(self.raw)
        except:
            print('No data')
        if self.legendimageexists:
            self.viewcolormap()
        #self.tcrefresh()   

    def applycolormap(self,image,raw=False):
        #apply color map dictionary
        mapselect=self.colmap.getvalue()[0]
        try:
            colormap=ImCmap.maps[mapselect]
        except:
            colormap=ImCmap.maps['Jet']
        len_x, len_y=image.shape[:2]
        colored=np.zeros((len_x,len_y,3),dtype=np.float32)
        for i in range(len_x):
            for j in range(len_y):
                if not self.CMYKOn:
                    if self.colinvert.getvalue()==():
                        colored[i,j,0]=colormap[int(image[i,j])][0]*255
                        colored[i,j,1]=colormap[int(image[i,j])][1]*255
                        colored[i,j,2]=colormap[int(image[i,j])][2]*255
                    else:
                        colored[i,j,0]=colormap[255-int(image[i,j])][0]*255
                        colored[i,j,1]=colormap[255-int(image[i,j])][1]*255
                        colored[i,j,2]=colormap[255-int(image[i,j])][2]*255
                else:
                    if self.colinvert.getvalue()==():
                        colored[i,j,0]+=colormap[int(image[i,j])][0]*128
                        colored[i,j,1]+=colormap[int(image[i,j])][1]*128
                        colored[i,j,2]+=colormap[int(image[i,j])][2]*128
                        colored[i,j,0]+=colormap[int(image[i,j])][1]*128
                        colored[i,j,1]+=colormap[int(image[i,j])][2]*128
                        colored[i,j,2]+=colormap[int(image[i,j])][0]*128
                    else:
                        colored[i,j,0]+=colormap[255-int(image[i,j])][0]*128
                        colored[i,j,1]+=colormap[255-int(image[i,j])][1]*128
                        colored[i,j,2]+=colormap[255-int(image[i,j])][2]*128
                        colored[i,j,0]+=colormap[255-int(image[i,j])][1]*128
                        colored[i,j,1]+=colormap[255-int(image[i,j])][2]*128
                        colored[i,j,2]+=colormap[255-int(image[i,j])][0]*128
                    
            
        #return image
        if not raw: colored=colored.astype('b')
        return colored

    def getcolormap(self,asText=False):
        #apply color map dictionary
        if self.forceColor is None:
            mapselect=self.colmap.getvalue()[0]
        else:
            mapselect=self.forceColor
        try:
            colormap=ImCmap.maps[mapselect]
        except:
            colormap=ImCmap.maps['Jet']
        colormap=np.array(colormap)*255
        if self.colinvert.getvalue()!=(): colormap=colormap[::-1,:]

        if self.CMYKOn:
            temp=np.zeros(colormap.shape,dtype=np.float32)
            temp[:,0]=(colormap[:,0]+colormap[:,1])/2
            temp[:,1]=(colormap[:,1]+colormap[:,2])/2
            temp[:,2]=(colormap[:,2]+colormap[:,0])/2
            colormap=temp
        if asText:
            return colormap.astype('i')
        colormap=colormap.astype('b')
        return colormap

    def savejpgimage_menu(self):
        #need filename
        #get file name
        fn=globalfuncs.trimdirext(self.datlab+'.jpg')
        fn=globalfuncs.ask_save_file(fn,'')
        if fn=='':
            print('Save cancelled')
            #globalfuncs.setstatus(self.status,'Save cancelled')
            return
        if fn[-4:].lower()!='.jpg': fn=fn+'.jpg'
        #globalfuncs.setstatus(self.status,"Saving image display...")
        self.savejpgimage(fn)
        #globalfuncs.setstatus(self.status,"Image display saved in: "+fn)

    def savejpgimage(self,fn):
        #save image
        self.main.lift()
        self.master.update()
        #if sys.platform=="darwin":
        #    sf=os.path.splitext(fn)[0]+".png"

        #    self.saveHDimage(sf)
        #    return

        if not self.scaleVAR.get():
##            try:
##                self.savobj.save(fn)
##            except:
            rx=int(self.imframe.winfo_rootx())
            ry=int(self.imframe.winfo_rooty())
            rw=int(self.imframe.winfo_width())
            rh=int(self.imframe.winfo_height())
            screencapture.capture(rx,ry,rw,rh,fn)
            #im=ImageGrab.grab((rx,ry,rx+rw,ry+rh))
            #im.save(fn) 
        else:
            rx=int(self.imframe.winfo_rootx())
            ry=int(self.imframe.winfo_rooty())
            rw=int(self.imframe.winfo_width())
            rh=int(self.imframe.winfo_height())
            screencapture.capture(rx,ry,rw,rh,fn)
            #im=ImageGrab.grab((rx,ry,rx+rw,ry+rh))
            #im.save(fn)            

    def saveHDimage(self,fn):
        #save image
        #p=ImageFile.Parser()
        #p.feed(self.savobj)
        #im=p.close()
        #(w,h)=im.size
        #scale=int(round(300./w))
        #im=im.resize((w*scale,h*scale))
        im=self.savobj.copy()
        im=im.convert('RGB')
        screencapture.saveMe(im,fn)

        try:
            self.savobj.save(fn)
            return 0
        except:
            return 1

    def savecmlegendimage(self,fn):
        #if on windows:
        self.legendimwin.lift()
        self.master.update()
        if os.sys.platform=='win32':
            rx=int(self.legendimwin.winfo_rootx())
            ry=int(self.legendimwin.winfo_rooty())
            rw=int(self.legendimwin.winfo_width())
            rh=int(self.legendimwin.winfo_height())
            screencapture.capture(rx,ry,rw,rh,fn)
            #im=ImageGrab.grab((rx,ry,rx+rw,ry+rh))
            #im.save(fn)
        else:
            rx=int(self.legendimwin.winfo_rootx())
            ry=int(self.legendimwin.winfo_rooty())
            rw=int(self.legendimwin.winfo_width())
            rh=int(self.legendimwin.winfo_height())
            screencapture.capture(rx,ry,rw,rh,'pic.jpg')
            #p=ImageFile.Parser()
            #p.feed(self.tcmaplegend)
            #im=p.close()
            #im.save(fn)

    def savexyplot(self):
        #return data for clipboard
        text=''
        for i in range(self.xyplotcolorind+1):
            datay=[]
            datax=[]

            #xpos=self.graphx.titletext#.configure('title')
            #ypos=self.graphy.titletext#configure('title')
            [xpos,ypos]=self.xyplotcoords[i]
  
            temp=self.graphx.get_xdata('XV'+str(i))#element_configure('XV','xdata')
            datax.append(temp)
            temp=self.graphx.get_ydata('XV'+str(i))#element_configure('XV','ydata')
            datay.append(temp)
            text=text+xpos+'\t\t\t'
            temp=self.graphy.get_xdata('YV'+str(i))#element_configure('YV','xdata')
            datax.append(temp)
            temp=self.graphy.get_ydata('YV'+str(i))#element_configure('YV','ydata')
            datay.append(temp)
            text=text+ypos+'\t\t\t'
            text=text+'\n'
            #parse list now
            pdatax=[]
            pdatay=[]
            alllen=[]
            maxlen=0
            for i in range(len(datax)):
                temp=datax[i]
                pdatax.append(temp)#split(temp))
                temp=datay[i]
                temp2=temp#split(temp)
                if maxlen<len(temp2):maxlen=len(temp2)
                alllen.append(len(temp2))
                pdatay.append(temp2)
            #setup text
            for j in range(maxlen):
                for i in range(len(pdatax)):
                    if j<alllen[i]:
                        text=text+str(pdatax[i][j])+'\t'+str(pdatay[i][j])+'\t\t'
                    else:
                        text=text+'\t\t\t'
                text=text+'\n'
            text=text+'\n\n\n'

        #return data
        return text

    def savexyplotxs(self):
        #return data for clipboard
        text=''
        datay=[]
        datax=[]
        temp=self.graphx2.get_xdata('XV')#element_configure('XV','xdata')
        if temp is not None:
            datax.append(temp)
        temp=self.graphx2.get_ydata('XV')#element_configure('XV','ydata')
        if temp is not None:
            datay.append(temp)
        text=text+'\n'

        prefix=['XV','EV']
        for p in prefix:
            active=True
            i=0
            while active:
                temp=self.graphx2.get_xdata(p+str(i))#element_configure('XV','xdata')
                if temp is None:
                    active=False
                    continue
                if temp is not None: datax.append(temp)
                temp=self.graphx2.get_ydata(p+str(i))#element_configure('XV','ydata')
                if temp is not None: datay.append(temp)
                i+=1
            text=text+'\n'


        #parse list now
        pdatax=[]
        pdatay=[]
        alllen=[]
        maxlen=0
        for i in range(len(datax)):
            temp=datax[i]
            pdatax.append(temp)#split(temp))
            temp=datay[i]
            temp2=temp#split(temp)
            if maxlen<len(temp2):maxlen=len(temp2)
            alllen.append(len(temp2))
            pdatay.append(temp2)
        #setup text
        for j in range(maxlen):
            for i in range(len(pdatax)):
                if j<alllen[i]:
                    text=text+str(pdatax[i][j])+'\t'+str(pdatay[i][j])+'\t\t'
                else:
                    text=text+'\t\t\t'
            text=text+'\n'
        #return data
        return text

    def savexyplotxs3(self):
        #return data for clipboard
        text=''
        datay=[]
        datax=[]
        active=True
        i=0
        while active:
            temp=self.graphx3.get_xdata('EV'+str(i))#element_configure('XV','xdata')
            if temp is None:
                active=False
                continue
            if temp is not None: datax.append(temp)
            temp=self.graphx3.get_ydata('EV'+str(i))#element_configure('XV','ydata')
            if temp is not None: datay.append(temp)
            i+=1
        text=text+'\n'

        #parse list now
        pdatax=[]
        pdatay=[]
        alllen=[]
        maxlen=0
        for i in range(len(datax)):
            temp=datax[i]
            pdatax.append(temp)#split(temp))
            temp=datay[i]
            temp2=temp#split(temp)
            if maxlen<len(temp2):maxlen=len(temp2)
            alllen.append(len(temp2))
            pdatay.append(temp2)
        #setup text
        for j in range(maxlen):
            for i in range(len(pdatax)):
                if j<alllen[i]:
                    text=text+str(pdatax[i][j])+'\t'+str(pdatay[i][j])+'\t\t'
                else:
                    text=text+'\t\t\t'
            text=text+'\n'
        #return data
        return text

    def savexyplotxs4(self):
        #return data for clipboard
        text=''
        datay=[]
        datax=[]


        return text

    def savexyplotelip(self,labels=None):
        #return data for clipboard
        text=''
        datayd={}
        datax=[]
        
        for d in labels:
            datay=[]
            temp=self.graphx2.get_xdata(d+'XV')#element_configure('XV','xdata')
            if temp is not None and datax == []:
                datax.append(temp)
                text+='dist\t'
            temp=self.graphx2.get_ydata(d+'XV')#element_configure('XV','ydata')
            if temp is not None:
                datay.append(temp)
                text+=d+'val\t'
            temp=self.graphx2.get_ydata(d+'XVp')#element_configure('XV','ydata')
            if temp is not None:
                datay.append(temp)
                text+=d+'err+\t'
            temp=self.graphx2.get_ydata(d+'XVm')#element_configure('XV','ydata')
            if temp is not None:
                datay.append(temp)                
                text+=d+'err-\t\t'
            datayd[d]=datay
        text=text+'\n'

        #setup text
        for j in range(len(datax[0])):
            text+=str(datax[0][j])+'\t'
            for d in labels:
                text=text+str(datayd[d][0][j])+'\t'+str(datayd[d][1][j])+'\t'+str(datayd[d][2][j])+'\t\t'
            text=text+'\n'
        #return data
        return text

    def viewcolormap(self):
        #form array of linear slope
        linear=list(range(255,-1,-1))
        bar=[]
        for i in range(25):
            bar.append(linear)
        #colormap it
        bar=np.array(bar)
        bar=np.transpose(bar)
        cmap=self.applycolormap(bar,raw=True)
        cmap=np.array(cmap)
        cmap=np.array(cmap,dtype=np.uint8)
        ppm=Image.fromarray(cmap,mode='RGB')
        #make image of it
        #cmap=cmap.astype('b')

        #ppm=ImRadon.toimage(np.transpose(cmap),cmin=0,skip=1)
        self.cmaplegend=ppm
        self.legendimage=ImageTk.PhotoImage(ppm)
        #ppm=globalfuncs.array2ppm(cmap)
        #self.cmaplegend=ppm        
        #self.legendimage=tkinter.PhotoImage(file=globalfuncs.save_ppm(ppm))

        w, h=self.legendimage.width(), self.legendimage.height()
        scalex=1
        scaley=1
        print (w,h)
        #self.legendimage=self.legendimage.zoom(scalex, scaley)
        #self.legendimage.configure(width=w*scalex, height=h*scaley)
        #create window if needed
        if not self.legendimageexists:
            self.legendimwin=Pmw.MegaToplevel(self.master)
            self.legendimwin.title('Legend Display')
            self.legendimwin.userdeletefunc(func=self.killlegendimwin)
            hf=self.legendimwin.interior()
            hf.config(bg='black')
            self.legendimframe=tkinter.Canvas(hf,bg='black',borderwidth=2,relief=tkinter.FLAT, height=250, width=250, cursor='crosshair',highlightcolor='black',highlightbackground='black',selectbackground='black',selectforeground='black')
            self.legendimframe.pack(side=tkinter.LEFT,fill=tkinter.X)
            self.legenditems=[]
            #numbers
            ltf=tkinter.Frame(hf,bg='black')
            ltf.pack(side=tkinter.LEFT,fill='both')
            self.legmax=tkinter.Label(ltf,text="",anchor=tkinter.W,fg='white',bg='black')
            self.legmin=tkinter.Label(ltf,text="",anchor=tkinter.W,fg='white',bg='black')
            self.legmin.pack(side=tkinter.BOTTOM,fill=tkinter.X)
            self.legmax.pack(side=tkinter.TOP,fill=tkinter.X)
            self.legendimageexists=1
        #clear        
        if self.legenditems !=[] : self.legendimframe.delete(self.legenditems.pop())
        #rescale canvas and slider
        self.legendimframe.config(height=h*scaley,width=w*scalex)
        self.legenditems.append(self.legendimframe.create_image((w*scalex+scalex)/2,(h*scaley+scaley)/2,anchor='center', image=self.legendimage))
        hisc=self.intenvarhi.get()       
        #zoom issue...
        if self.zmxyi[2]!=-1 and self.zmxyi[3]!=-1:
            data=self.raw[self.zmxyi[0]:self.zmxyi[2],self.zmxyi[1]:self.zmxyi[3]]
        else:
            data=self.raw        
        if self.datlab in list(self.scalemaxlist.keys()):
            hisc=self.scalemaxlist[self.datlab]/max(np.ravel(data))*self.intenvarhi.get()
        try:
            globalfuncs.setstatus_d(self.legmin,str(max(np.ravel(data))*self.intenvarlo.get()),4)
            globalfuncs.setstatus_d(self.legmax,str(max(np.ravel(data))*hisc),4)
        except:
            print('hmm')

    def killlegendimwin(self):
        self.legendimageexists=0
        self.legendimwin.destroy()


class Movie(Display):
    def placeMovie(self,data,mapindex,status,scales=(None,None),xax=None,yax=None,datlab='',pause=0.2,frames=None):

        self.datlab=datlab
        self.mapindex=mapindex
        self.mainstatus=status
        self.xsc=xax
        self.ysc=yax[::-1]
        self.domask=0
        self.mask=[]
        self.raw=data
        self.movieRepeat=1
        self.movieDirection=1
        self.pause=pause
        self.frames=tkinter.Frames
        self.imframe.unbind(sequence="<Button-1>")
        self.imframe.unbind(sequence="<Shift-Button-1>")
        if sys.platform=='darwin':
            self.imframe.unbind(sequence="<ButtonPress>")
            self.imframe.unbind(sequence="<ButtonRelease>")
            self.imframe.bind(sequence="<ButtonPress>",func=self.macmoviebutton)
        else:
            self.imframe.unbind(sequence="<Control-ButtonPress>")
            self.imframe.unbind(sequence="<Alt-ButtonPress>")
            self.imframe.unbind(sequence="<Control-ButtonRelease>")
            self.imframe.unbind(sequence="<Alt-ButtonRelease>")        
            self.imframe.bind(sequence="<Button-1>",func=self.movieStop)
            self.imframe.bind(sequence="<Shift-Button-1>",func=self.movieReverse)
            self.imframe.bind(sequence="<Control-Button-1>",func=self.movieSpeedDown)
            self.imframe.bind(sequence="<Alt-Button-1>",func=self.movieSpeedUp)
        self.framecount=0
        self.advanceFrame()

    def macmoviebutton(self,event):
        if event.state==0: self.movieStop(event)
        if event.state==1: self.movieReverse(event)
        if event.state==4: self.movieSpeedDown(event)
        if event.state==16: self.movieSpeedUp(event)

    def advanceFrame(self):
        scales=(None,None)
        if self.frames is not None:
            self.placePPMimage(self.raw[self.framecount,:,:],scales,movie=1,frame=self.frames[self.framecount])
        else:
            self.placePPMimage(self.raw[self.framecount,:,:],scales,movie=1)
        self.framecount=self.framecount+self.movieDirection
        if self.framecount>=self.raw.shape[0]:
            self.framecount=0
        if self.framecount<0:
            self.framecount=self.raw.shape[0]-1
        if self.movieRepeat:
            #JOY Q
            self.master.after(int(self.pause*1000),self.advanceFrame)

    def movieStop(self,event):
        self.imframe.bind(sequence="<Button-1>",func=self.movieStart)
        self.movieRepeat=0

    def movieStart(self,event):
        self.imframe.bind(sequence="<Button-1>",func=self.movieStop)
        self.movieRepeat=1
        self.advanceFrame()

    def movieSpeedUp(self,event):
        self.pause=self.pause/2.
        print(self.pause)

    def movieSpeedDown(self,event):
        self.pause=self.pause*2.
        print(self.pause)
        
    def movieReverse(self,event):
        self.movieDirection=-self.movieDirection

    def datalookup(self,x,y):
        global zdrag,zdrug
        x,y=x-3,y-3
        xind=int(x/self.pixscale[0])
        yind=int(y/self.pixscale[1])
        if self.flipVAR.get():
            t=xind
            xind=yind
            yind=t
        ##OLD: if not zdrag:
        ##if self.zmxyi!=[0,0,-1,-1] and not zdrag:
        if self.iamzoomed:
            xind=xind+self.zmxyi[0]
            yind=yind+self.zmxyi[1]
        if xind<0: xind=0
        if yind<0: yind=0
        if xind>=self.raw.shape[0]: xind=self.raw.shape[0]-1
        if yind>=self.raw.shape[1]: yind=self.raw.shape[1]-1
        if self.xdir==-1:
            xind=self.raw.shape[0]-xind-1
        if self.ydir==-1:
            yind=self.raw.shape[1]-yind-1
        z=self.raw[self.framecount,xind,yind]
        return z,xind,yind
 