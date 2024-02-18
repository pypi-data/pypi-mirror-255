# -*- coding: utf-8 -*-
"""
Created on Mon May  8 10:09:30 2023

@author: f006sq8
"""
#standard
import math
import os
import tkinter

#third party
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from PIL import Image, ImageTk
import Pmw
from scipy.optimize import curve_fit, minimize

#local
import Display
import FaderClass
import FittingFunctions
import globalfuncs
from MasterClass import MasterClass
import MultiFitObj
import MyGraph
import PmwTtkButtonBox
import PmwTtkMenuBar
import sblite




class MegaXPlot:
    
    def __init__(self, imgwin, mapdata, ps):
        self.imgwin = imgwin
        self.mapdata = mapdata
        self.zmxyi = ps
        self.megaGraph = None
        self.megaCrossDialog=Pmw.Dialog(self.imgwin,title="Cross Plots",buttons=('OK','Cancel'),defaultbutton='Cancel',
                                            command=self.donemegaXdialog)
        h=self.megaCrossDialog.interior()
        h.configure(background='#d4d0c8')
        self.megaXgroup=[]
        f = tkinter.Frame(h)
        f.configure(background='#d4d0c8')
        f.pack(side=tkinter.TOP,padx=1,pady=1,expand='yes',fill='both')
        self.megaXgroup.append(FaderClass.stitchChannelGroup(f,self.mapdata.labels,'Plots',shift=None,extend=True,slide=True))
        self.megaXgroup.append(FaderClass.stitchChannelGroup(f,self.mapdata.labels,'Cluster',shift=None))
        self.megaXdensity=Pmw.RadioSelect(f,labelpos=tkinter.W,buttontype='radiobutton',label_text='Diagonal Plot: ',label_background='#d4d0c8',hull_background='#d4d0c8',frame_background='#d4d0c8')
        self.megaXdensity.add('Histogram',background='#d4d0c8')
        self.megaXdensity.add('Gaussian',background='#d4d0c8')
        self.megaXdensity.setvalue('Gaussian')
        self.megaXdensity.pack(side=tkinter.TOP,padx=2,pady=4)
        self.megaXyscale=Pmw.RadioSelect(f,labelpos=tkinter.W,buttontype='radiobutton',label_text=' ',label_background='#d4d0c8',hull_background='#d4d0c8',frame_background='#d4d0c8')
        self.megaXyscale.add('Linear',background='#d4d0c8')
        self.megaXyscale.add('Log-Y',background='#d4d0c8')
        self.megaXyscale.setvalue('Linear')
        self.megaXyscale.pack(side=tkinter.TOP,padx=2,pady=4)
        b=PmwTtkButtonBox.PmwTtkButtonBox(h,hull_background='#d4d0c8')
        b.add('Show Plot',command=self.doMegaXPlot,style='GREEN.TButton',width=10)
        b.pack(side=tkinter.LEFT,padx=5,pady=5)
        self.megaCrossDialog.show()
    
    def doMegaXPlot(self,*args):
        if self.megaXgroup[0].stitchch.getvalue()==():
            print('Select data channels to plot')
            globalfuncs.setstatus(self.status, 'Select data channels to plot.')
            return
        preview=[]
        for i in self.megaXgroup[0].stitchch.getvalue():
            dind = self.mapdata.labels.index(i)+2
            cfdata=self.mapdata.data.get(dind)
            if self.zmxyi[0:4] != [0, 0, -1, -1]:
                cfdata = cfdata[::-1, :]
                cfdata = cfdata[self.zmxyi[1]:self.zmxyi[3], self.zmxyi[0]:self.zmxyi[2]]
                cfdata = cfdata[::-1, :]
            preview.append(np.ravel(cfdata))
        if self.megaXgroup[1].stitchch.getvalue()==():
            hd=None
        else:
            dind = self.mapdata.labels.index(self.megaXgroup[1].stitchch.getvalue()[0]) + 2
            hd = self.mapdata.data.get(dind)
            if self.zmxyi[0:4] != [0, 0, -1, -1]:
                hd = hd[::-1, :]
                hd = hd[self.zmxyi[1]:self.zmxyi[3], self.zmxyi[0]:self.zmxyi[2]]
                hd = hd[::-1, :]
            hd=np.ravel(hd)
        if self.megaGraph is not None:
            plt.close(self.megaGraph.fig)
        self.megaGraph = sblite.PairGrid(preview, list(range(len(preview))), xlabels=list(self.megaXgroup[0].stitchch.getvalue()), diag_sharey=False, hue=hd)
        self.megaGraph = self.megaGraph.map_offdiag(plt.scatter, s=5)
        if self.megaXdensity.getvalue()=='Histogram':
            self.megaGraph = self.megaGraph.map_diag(plt.hist,yax=self.megaXyscale.getvalue(),limits=True,lowerlimit=float(self.megaXgroup[0].fadeCFvar.get()))#sblite.plot_scpkde)
        if self.megaXdensity.getvalue()=='Gaussian':
            self.megaGraph = self.megaGraph.map_diag(sblite.plot_scpkde,yax=self.megaXyscale.getvalue(),limits=True,lowerlimit=float(self.megaXgroup[0].fadeCFvar.get()))
        self.megaGraph = self.megaGraph.add_legend()
        plt.show(block=False)
    
    def donemegaXdialog(self,result):
           #cleanup
           self.megaCrossDialog.withdraw()

########################  Correlation Plot Routines
class CorrParams:
    def __init__(self, exportcorplot, useMaskforCorPlotData, corplotSQRT,zmxyi, dataFileBuffer,activeFileBuffer, dodt, mask, datachanCB, colormapCB, deadtimevalue, deadtimecorrection, DTICRchanval):
        self.exportcorplot = exportcorplot
        self.useMaskforCorPlotData = useMaskforCorPlotData
        self.corplotSQRT = corplotSQRT

        self.dataFileBuffer = dataFileBuffer
        self.activeFileBuffer = activeFileBuffer
        self.zmxyi = zmxyi
        self.dodt = dodt
        self.cpmask = mask
        self.datachanCB = datachanCB
        self.colormapCB = colormapCB      
        
        self.deadtimecorrection = deadtimecorrection
        self.deadtimevalue = deadtimevalue
        self.DTICRchanval=DTICRchanval
        
class CorrelationPlot(MasterClass):

    def _create(self):
        
        self.corplotcolors=['black','green',5,'0.75']
        #make window
        self.win=Pmw.MegaToplevel(self.imgwin)
        self.win.title('Correlation Plotter')
        self.win.userdeletefunc(func=self.killcorplot)
        h=self.win.interior()    
        #Menu bar
        menubar=PmwTtkMenuBar.PmwTtkMenuBar(h)
        if os.sys.platform=='win32': menubar.component('hull').configure(bg='#d4d0c8')
        #file menu
        self.CPPlotType=tkinter.StringVar()
        self.CPColorRegion=tkinter.StringVar()
        #self.CPColorRegion.set(0)
        menubar.addmenu('File','')
        menubar.addmenuitem('File','command',label='Export',command=self.localexportcorplot)
        menubar.addmenuitem('File','command',label='3D Plot',command=self.corplot3d)
        menubar.addmenu('Color','')
        menubar.addmenuitem('Color','command',label='Swap Colors',command=self.corplotcolorswap)
        menubar.addcascademenu('Color','ColorTheme')        
        menubar.addmenuitem('ColorTheme','radiobutton',label='None',command=self.checkcorplot,variable=self.CPColorRegion)
        menubar.addmenuitem('ColorTheme','radiobutton',label='Highlight Mask',command=self.checkcorplot,variable=self.CPColorRegion)
        menubar.addmenuitem('ColorTheme','radiobutton',label='Cluster',command=self.checkcorplot,variable=self.CPColorRegion)
        menubar.addmenuitem('ColorTheme','radiobutton',label='MultiFile',command=self.checkcorplot,variable=self.CPColorRegion)
        menubar.addmenuitem('ColorTheme','separator')
        menubar.addmenuitem('ColorTheme','checkbutton',label='Only show Mask Data',command=self.checkcorplot,variable=self.ps.useMaskforCorPlotData)
        self.CPColorRegion.set('None')
        menubar.addcascademenu('Color','Density Plots')
        menubar.addmenuitem('Density Plots','radiobutton',label='Off',command=self.checkcorplot,variable=self.CPPlotType)
        menubar.addmenuitem('Density Plots','radiobutton',label='Density',command=self.checkcorplot,variable=self.CPPlotType)
        menubar.addmenuitem('Density Plots','radiobutton',label='LogDensity',command=self.checkcorplot,variable=self.CPPlotType)
        self.CPPlotType.set('Off')
        menubar.addmenu('Error','')
        menubar.addmenuitem('Error','checkbutton',label='Show Sqrt Line',command=self.checkcorplot,variable=self.ps.corplotSQRT)
        menubar.addmenuitem('Error','command',label='Mask Above Sqrt Line',command=self.corplotmaskSQRT)        
        menubar.addmenu('Analysis','')
        menubar.addmenuitem('Analysis','command',label='Do ICR-OCR Deadtime',command=self.corplotDTfit)
        menubar.addmenuitem('Analysis','command',label='Regression',command=self.corplotRegress)
        menubar.addmenuitem('Analysis','command',label='Multi-Regression',command=self.corplotMultRegress)
        menubar.addmenuitem('Analysis','separator')
        menubar.addmenuitem('Analysis','command',label='Close Mask',command=self.finishmaskmenu)

        menubar.pack(side=tkinter.TOP,fill=tkinter.X)        
        bf=tkinter.Frame(h,background='#d4d0c8')
        bf.pack(side=tkinter.TOP,fill='both')
        lf=tkinter.Frame(bf,background='#d4d0c8')
        lf.pack(side=tkinter.LEFT,fill='both')
        #sca sections
        xf=tkinter.Frame(lf,background='#d4d0c8')
        xf.pack(side=tkinter.TOP,fill='both')
        self.cpxchan=Pmw.ScrolledListBox(xf,labelpos='n',label_text='X Data Channels',listbox_height=5,
                        selectioncommand=self.checkcorplotx,listbox_exportselection=0,listbox_takefocus=tkinter.TRUE,
                        hull_background='#d4d0c8',label_background='#d4d0c8')
        #bind to move
        self.cpxchan.bind(sequence="<Up>", func=self.arrowcpxchan)
        self.cpxchan.bind(sequence="<Down>", func=self.arrowcpxchan)
        self.cpxchan.pack(side=tkinter.LEFT,fill='both')
        self.cpxchan.setlist(self.mapdata.labels)
        self.cpxvar=tkinter.DoubleVar()
        self.cpxvar.set(1.0)
        self.cpxintensity=tkinter.Scale(xf,variable=self.cpxvar,from_=1.0, to=0.01,background='#d4d0c8',orient=tkinter.VERTICAL,resolution=0.01,length=150,command=self.checkcorplot)
        self.cpxintensity.pack(side=tkinter.LEFT,fill='both')        
        yf=tkinter.Frame(lf,background='#d4d0c8')
        yf.pack(side=tkinter.TOP,fill='both')
        self.cpychan=Pmw.ScrolledListBox(yf,labelpos='n',label_text='Y Data Channels',listbox_height=5,
                        selectioncommand=self.checkcorploty,listbox_exportselection=0,listbox_takefocus=tkinter.TRUE,
                        hull_background='#d4d0c8',label_background='#d4d0c8')
        #bind to move
        self.cpychan.bind(sequence="<Up>", func=self.arrowcpychan)
        self.cpychan.bind(sequence="<Down>", func=self.arrowcpychan)
        self.cpychan.pack(side=tkinter.LEFT,fill='both')
        self.cpychan.setlist(self.mapdata.labels)
        self.cpyvar=tkinter.DoubleVar()
        self.cpyvar.set(1.0)
        self.cpyintensity=tkinter.Scale(yf,variable=self.cpyvar,from_=1.0, to=0.01,background='#d4d0c8',orient=tkinter.VERTICAL,resolution=0.01,length=150,command=self.checkcorplot)
        self.cpyintensity.pack(side=tkinter.LEFT,fill='both')
        zf=tkinter.Frame(lf,background='#d4d0c8')
        zf.pack(side=tkinter.TOP,fill='both',pady=5)
        b=PmwTtkButtonBox.PmwTtkButtonBox(zf,label_text="Plot Actions",orient='vertical',labelpos='n',hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        w=15
        b.add('Update Plot',command=self.checkcorplot,style='GREEN.TButton',width=tkinter.W)
        b.add('Plot MultiFile',command=self.updateMulticorplot,style='LGREEN.TButton',width=tkinter.W)
        b.pack(side=tkinter.TOP,padx=2,pady=6)
        b=PmwTtkButtonBox.PmwTtkButtonBox(zf,label_text="Mask Actions",labelpos='n',hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        w=15
        b.add('Define Mask',command=self.definecpmask,style='MBLUE.TButton',width=tkinter.W)
        b.add('Set Slope Mask',command=self.defineSlopecpmask,style='RBLUE.TButton',width=tkinter.W)
        b.pack(side=tkinter.TOP,padx=2,pady=2)
        b=PmwTtkButtonBox.PmwTtkButtonBox(zf,hull_background='#d4d0c8')
        w=15
        b.add('Set Mask to All',command=self.setAllcpmask,style='LGREEN.TButton',width=tkinter.W)
        b.add('Clear Mask',command=self.clearcpmask,style='FIREB.TButton',width=tkinter.W)
        b.pack(side=tkinter.TOP,padx=2,pady=2)
        rf=tkinter.Frame(bf,background='#d4d0c8')
        rf.pack(side=tkinter.LEFT,fill='both')
        #graph section
        self.cpgraph=MyGraph.MyGraph(rf,side=tkinter.LEFT,motioncallback=self.cpcoordreport)#,plotbackground='black',height=400,width=550)
        #self.cpgraph.legend_configure(hide=1)
        #self.cpgraph.pack(side=tkinter.LEFT,expand=1,fill='both',padx=2)
        #self.cpgraph.bind(sequence="<Motion>", func=self.cpcoordreport)
        #status        
        botfr=tkinter.Frame(h,background='#d4d0c8')
        botfr.pack(side=tkinter.TOP,fill=tkinter.X)        
        self.cpstatus=tkinter.Label(botfr,text="",bd=2,relief=tkinter.RAISED,anchor=tkinter.W,fg='blue',background='#d4d0c8')
        self.cpstatus.pack(side=tkinter.LEFT,fill=tkinter.X,expand=1)
        globalfuncs.setstatus(self.cpstatus,"Ready")
        self.cpxcoord=tkinter.Label(botfr,text="X=      ",width=15,bd=2,relief=tkinter.RIDGE,anchor=tkinter.W,fg='red',background='#d4d0c8')
        self.cpycoord=tkinter.Label(botfr,text="Y=      ",width=15,bd=2,relief=tkinter.RIDGE,anchor=tkinter.W,fg='red',background='#d4d0c8')
        self.cpycoord.pack(side=tkinter.RIGHT,fill=tkinter.X)
        self.cpxcoord.pack(side=tkinter.RIGHT,fill=tkinter.X)
 

    def corplot3d(self):
        self.CvCwin=Pmw.Dialog(self.imgwin,buttons=('Plot','Close',),title='3D Plot',command=self.CvCaction)
        h=self.CvCwin.interior()
        self.CvCp1=Pmw.ComboBox(h,labelpos='n',label_text='X Data:',history=0,selectioncommand=tkinter.DISABLED)
        self.CvCp2=Pmw.ComboBox(h,labelpos='n',label_text='Y Data:',history=0,selectioncommand=tkinter.DISABLED)
        self.CvCp3=Pmw.ComboBox(h,labelpos='n',label_text='Z Data:',history=0,selectioncommand=tkinter.DISABLED)            
        self.CvCp1.pack(side=tkinter.TOP,fill='both',pady=5,padx=5)
        self.CvCp2.pack(side=tkinter.TOP,fill='both',pady=5,padx=5)
        self.CvCp3.pack(side=tkinter.TOP,fill='both',pady=5,padx=5)
        third=[]
        third.append('None')
        third.extend(self.mapdata.labels)
        self.CvCp1.setlist(third)
        self.CvCp2.setlist(third)
        self.CvCp3.setlist(third)
        self.CvCp1.selectitem('None')
        self.CvCp2.selectitem('None')
        self.CvCp3.selectitem('None')

    def CvCaction(self,result):
        if result=="Plot":
            if self.CvCp3.getvalue()[0]=='None':
                print('need all valid')
                return
            else:
                self.plot3DCvC()
        if result=="Close":
            self.CvCwin.withdraw()
            self.CvCwin=None

    def plot3DCvC(self):
        xind=self.mapdata.labels.index(self.CvCp1.getvalue()[0])+2
        yind=self.mapdata.labels.index(self.CvCp2.getvalue()[0])+2
        zind=self.mapdata.labels.index(self.CvCp3.getvalue()[0])+2
        xdata=self.mapdata.data.get(xind)
        ydata=self.mapdata.data.get(yind)
        zdata=self.mapdata.data.get(zind)
        if self.ps.zmxyi[2]!=-1 and self.ps.zmxyi[3]!=-1:
            xdata=xdata[::-1,:]
            ydata=ydata[::-1,:]
            zdata=zdata[::-1,:]
            xdata=xdata[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
            ydata=ydata[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
            zdata=zdata[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
            xdata=xdata[::-1,:]
            ydata=ydata[::-1,:]
            zdata=zdata[::-1,:]
        
        xd=np.ravel(xdata)
        yd=np.ravel(ydata)
        zd=np.ravel(zdata)

##        nodtx=0
##        nodty=0
##        if self.cpxchan.getvalue()[0] in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodtx=1
##        if self.cpychan.getvalue()[0] in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodty=1
##        if self.dodt.get()==1 and not nodtx:
##            #DT: corFF=FF*exp(tau*1e-6*ICR)
##            icr=np.ravel(tdata[:,:,self.DTICRchanval])
##            dtcor=exp(float(self.deadtimevalue.getvalue())*1e-6*icr)
##            xv=xv*dtcor        
##        if self.dodt.get()==1 and not nodty:
##            #DT: corFF=FF*exp(tau*1e-6*ICR)
##            icr=np.ravel(tdata[:,:,self.DTICRchanval])
##            dtcor=exp(float(self.deadtimevalue.getvalue())*1e-6*icr)
##            yv=yv*dtcor      

        fig=plt.figure()
        ax=Axes3D(fig)
        ax.scatter(xd,yd,zd)
        ax.set_xlabel(self.CvCp1.getvalue()[0])
        ax.set_ylabel(self.CvCp2.getvalue()[0])
        ax.set_zlabel(self.CvCp3.getvalue()[0])

        plt.show()

    #put this back in main smak
    # def startcorplot(self):
    #     #show corplot window if needed
    #     globalfuncs.setstatus(self.status,"Ready")
    #     if self.corplotexist:
    #         self.win.show()
    #     elif self.hasdata:
    #         self.corplotexist=1
    #         self.createcorplot()
    #     else:
    #         print('No Data')
    #         globalfuncs.setstatus(self.status,'No Data')

 

    def killcorplot(self):
        self.kill()

    def corplotmaskSQRT(self):
        if self.cpxchan.getvalue()==() or self.cpychan.getvalue()==():
            return
        self.clearcpmask()
        
        globalfuncs.setstatus(self.cpstatus,"Calculating Mask...")
        
        xind=self.mapdata.labels.index(self.cpxchan.getvalue()[0])+2
        yind=self.mapdata.labels.index(self.cpychan.getvalue()[0])+2
        sqrtdata=np.ravel(self.mapdata.data.get(xind))#[:,:,xind])
        ydata=np.ravel(self.mapdata.data.get(yind))#[:,:,yind])
        
        sqrtdata=np.sort(sqrtdata)
        ysort=np.sort(ydata)
        try:
            sqrtx=list(range(0,int(sqrtdata[-1]),int(sqrtdata[-1]/50.)))
        except:
            sqrtx=list(range(0,int(sqrtdata[-1]),1))
        sqrtx=list(map(float,sqrtx))
        sqrtx=np.array(sqrtx)
        sqrtxdata=np.sqrt(sqrtx)

        for i in range(0,len(sqrtx)):
            self.ps.cpmask.maskx.append(sqrtx[i])
            self.ps.cpmask.masky.append(sqrtxdata[i])
            self.ps.cpmask.maskpts.append((sqrtx[i],sqrtxdata[i]))
##        #add last
##        self.ps.cpmaskx.append(sqrtx[-1])
##        self.ps.cpmasky.append(sqrtdata[-1])
##        self.ps.cpmaskpts.append((sqrtx[-1],sqrtdata[-1]))            
        #add corners
        ymax=max((ysort[-1],sqrtdata[-1]))
        self.ps.cpmask.maskx.append(sqrtdata[-1])
        self.ps.cpmask.masky.append(ymax)
        self.ps.cpmask.maskpts.append((sqrtdata[-1],ymax))
        self.ps.cpmask.maskx.append(sqrtdata[0])
        self.ps.cpmask.masky.append(ymax)
        self.ps.cpmask.maskpts.append((sqrtdata[0],ymax))
        self.ps.cpmask.maskx.append(self.ps.cpmask.maskx[0])
        self.ps.cpmask.masky.append(self.ps.cpmask.masky[0])
                                  
        #if mask exist, remove...
        self.cpgraph.removeplot('MASK')
##        glist=self.cpgraph.element_names()
##        if 'MASK' in glist:
##            self.cpgraph.element_delete('MASK') 
        #self.cpgraph.line_create('MASK',xdata=tuple(self.ps.cpmaskx),ydata=tuple(self.ps.cpmasky),pixels=2,linewidth=1,color='red')
        self.cpgraph.plot(tuple(self.ps.cpmask.maskx),tuple(self.ps.cpmask.masky),text='MASK',symbol='o',size=6,color='red')
        self.cpgraph.draw()
        print("finding")
        #find points
        self.ps.cpmask.mask=np.ones((self.mapdata.data.shape[0],self.mapdata.data.shape[1]),dtype=np.float32)
        len_x, len_y = self.mapdata.data.shape[:2]
        xind=self.mapdata.labels.index(self.cpxchan.getvalue()[0])+2
        yind=self.mapdata.labels.index(self.cpychan.getvalue()[0])+2
        for i in range(len_x):
            print(i)
            for j in range(len_y):
                dx=self.mapdata.data.get(xind)[i,j]#[i,j,xind]
                dy=self.mapdata.data.get(yind)[i,j]#[i,j,yind]
                if not globalfuncs.point_inside_polygon(dx,dy,self.ps.cpmask.maskpts):
                    self.ps.cpmask.mask[i,j]=0
        globalfuncs.setstatus(self.cpstatus,"SQRT Mask complete")

    #this should all be in main?
    # def useImageasMask(self):
    #     globalfuncs.setstatus(self.status,"Ready")
    #     if not self.hasdata:
    #         print('No Data')
    #         globalfuncs.setstatus(self.status,'No Data')
    #         return
    #     if self.datachan.get()==():
    #         return        
    #     datind=self.mapdata.labels.index(self.datachan.getvalue()[0])+2
    #     data=self.mapdata.data.get(datind)#[:,:,datind]
    #     self.ps.cpmask=np.where(data>0,1,0)
    #     globalfuncs.setstatus(self.status,"Mask complete")        

    # def invertMaskSelection(self):
    #     globalfuncs.setstatus(self.status,"Ready")
    #     if not self.hasdata:
    #         print('No Data')
    #         globalfuncs.setstatus(self.status,'No Data')
    #         return
    #     if self.ps.cpmask == []:
    #         print('No selection in mask')
    #         globalfuncs.setstatus(self.status, 'No selection in mask')
    #         return
    #     newmask = 1-self.ps.cpmask
    #     self.ps.cpmask=newmask
    #     self.domapimagefromscaselect()

    # def createNewChannelFromMask(self):
    #     globalfuncs.setstatus(self.status,"Ready")
    #     if not self.hasdata:
    #         print('No Data')
    #         globalfuncs.setstatus(self.status,'No Data')
    #         return
    #     if len(self.ps.cpmask)==0:
    #         print('No Mask')
    #         globalfuncs.setstatus(self.status,'No mask to use.')
    #         return
    #     #check name
    #     name=tkinter.simpledialog.askstring(title='Add Mask as Channel',prompt="Enter new name for channel.")
    #     newname=globalfuncs.fixlabelname(name)
    #     if newname in self.mapdata.labels:
    #         print('Enter unique channel name')
    #         globalfuncs.setstatus(self.status,'Enter unique channel name')
    #         return
    #     self.savedeconvcalculation(self.ps.cpmask,newname)
    #     globalfuncs.setstatus(self.status,"Done")        

    # def addMaskToChannel(self):
    #     globalfuncs.setstatus(self.status,"Ready")
    #     if not self.hasdata:
    #         print('No Data')
    #         globalfuncs.setstatus(self.status,'No Data')
    #         return
    #     if self.datachan.get()==():
    #         return
    #     if len(self.ps.cpmask)==0:
    #         print('No Mask')
    #         globalfuncs.setstatus(self.status,'No mask to use.')
    #         return
    #     datind=self.mapdata.labels.index(self.datachan.getvalue()[0])+2
    #     data=self.mapdata.data.get(datind)#[:,:,datind]
    #     #find power of 2...
    #     factor=globalfuncs.powernext(int(max(np.ravel(data))))
    #     self.mapdata.data.put(datind,data+self.ps.cpmask*float(factor))
    #     self.domapimagefromscaselect()

    # def delMaskToChannel(self):
    #     globalfuncs.setstatus(self.status,"Ready")
    #     if not self.hasdata:
    #         print('No Data')
    #         globalfuncs.setstatus(self.status,'No Data')
    #         return
    #     if self.datachan.get()==():
    #         return
    #     if len(self.ps.cpmask)==0:
    #         print('No Mask')
    #         globalfuncs.setstatus(self.status,'No mask to use.')
    #         return
    #     datind=self.mapdata.labels.index(self.datachan.getvalue()[0])+2
    #     data=self.mapdata.data.get(datind)#[:,:,datind]
    #     data=np.where(self.ps.cpmask>0,0,data)
    #     self.mapdata.data.put(datind,data)
    #     self.domapimagefromscaselect()

    def definecpmask(self):
        #bind plot window, single click to start, double to end
        self.addpointtomaskEventCatch=self.cpgraph.canvas.mpl_connect('button_press_event',self.catchmaskclick)
        #self.finishmaskEventCatch=self.cpgraph.canvas.mpl_connect('button_dblclick_event',self.catchmaskclick)
        #self.finishmaskEventCatch=self.cpgraph.canvas.mpl_connect('button_dblclick_event',self.catchmaskclick)
        self.win.focus_set()
        self.win.bind('<End>',self.finishmaskkey)
        globalfuncs.setstatus(self.cpstatus,"Click on graph to add mask point, double click to end")

    def defineSlopecpmask(self):
        if self.cpxchan.getvalue()==() or self.cpychan.getvalue()==():
            return
        slope=tkinter.simpledialog.askfloat(title='Correlation Mask',prompt='Enter the slope to mask',initialvalue=1.0)
        if slope=='':
            print('mask cancelled')
            return
        delta=tkinter.simpledialog.askfloat(title='Correlation Mask',prompt='Enter the slope tolerance to mask',initialvalue=0.2)
        if delta=='':
            print('mask cancelled')
            return
        self.clearcpmask()
        globalfuncs.setstatus(self.cpstatus,"Calcualting Mask...")
        xind=self.mapdata.labels.index(self.cpxchan.getvalue()[0])+2
        yind=self.mapdata.labels.index(self.cpychan.getvalue()[0])+2
        xdata=np.ravel(self.mapdata.data.get(xind)[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]])
        ydata=np.ravel(self.mapdata.data.get(yind)[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]])
        xmax=max(xdata)
        ymax=max(ydata)
        mcr=5000000
        self.ps.cpmask.maskx.append(0)
        self.ps.cpmask.masky.append(0)
        self.ps.cpmask.maskx.append(mcr)
        self.ps.cpmask.masky.append(mcr*(slope-delta))
        self.ps.cpmask.maskx.append(mcr)
        self.ps.cpmask.masky.append(mcr*(slope+delta))
        self.ps.cpmask.maskx.append(0)
        self.ps.cpmask.masky.append(0)
        plotx=[]
        ploty=[]

        for x,y in zip(self.ps.cpmask.maskx,self.ps.cpmask.masky):
            self.ps.cpmask.maskpts.append((x,y))
            px=x
            py=y
            s = py / mcr
            if px>xmax:
                px=xmax
                py=s*px
            if py>ymax:
                py=ymax
                px=py/s

            plotx.append(px)
            ploty.append(py)
        # if mask exist, remove...
        self.cpgraph.removeplot('MASK')
        self.cpgraph.plot(tuple(plotx),tuple(ploty),text='MASK',symbol='o',size=6,color='red')
        self.cpgraph.draw()
        self.ps.cpmask.mask=self.findcpmaskpoints(self.ps.activeFileBuffer)
        globalfuncs.setstatus(self.cpstatus, "Slope Mask complete")

    def setAllcpmask(self):
        if self.ps.cpmask.maskpts==[]:
            print('no mask to copy')
            return
        if not tkinter.messagebox.askyesno("Set Mask", "Set all files to current mask?"):
            print('mask set all cancelled')
            return
        for nbuf in list(self.ps.dataFileBuffer.keys()):
            buf=self.ps.dataFileBuffer[nbuf]
            if self.cpxchan.getvalue()[0] not in buf['data'].labels:
                print('x selection not in ',nbuf)
                continue
            if self.cpychan.getvalue()[0] not in buf['data'].labels:
                print('y selection not in ',nbuf)
                continue
            self.ps.dataFileBuffer[nbuf]['mask']=self.findcpmaskpoints(nbuf)

    def findcpmaskpoints(self,bname):
        print('finding mask points in ',bname)
        buf=self.ps.dataFileBuffer[bname]
        if buf['zoom'][0:4] != [0, 0, -1, -1]:
            cpmask = np.zeros((buf['data'].data.shape[0], buf['data'].data.shape[1]), dtype=np.float32)
            newone = np.ones(buf['data'].data.get(0)[buf['zoom'][1]:buf['zoom'][3],
                          buf['zoom'][0]:buf['zoom'][2]].shape, dtype=np.float32)
            cpmask = cpmask[::-1, :]
            cpmask[buf['zoom'][1]:buf['zoom'][3],buf['zoom'][0]:buf['zoom'][2]] = newone
            cpmask = cpmask[::-1, :]
        else:
            cpmask = np.ones((buf['data'].data.shape[0], buf['data'].data.shape[1]), dtype=np.float32)

        len_x, len_y = buf['data'].data.shape[:2]
        xnodt = 0
        ynodt = 0
        if self.cpxchan.getvalue()[0] in ['ICR', 'I0', 'I1', 'I2', 'I0STRM', 'I1STRM', 'I2STRM']: xnodt = 1
        if self.cpychan.getvalue()[0] in ['ICR', 'I0', 'I1', 'I2', 'I0STRM', 'I1STRM', 'I2STRM']: ynodt = 1
        xind = buf['data'].labels.index(self.cpxchan.getvalue()[0]) + 2
        yind = buf['data'].labels.index(self.cpychan.getvalue()[0]) + 2
        xdat = buf['data'].data.get(xind)  # [:,:,xind]
        ydat = buf['data'].data.get(yind)  # [:,:,yind]
        if self.ps.dodt.get() == 1 and not xnodt:
            # DT: corFF=FF*exp(tau*1e-6*ICR)
            icr = buf['data'].data.get(self.ps.DTICRchanval)  # [:,:,self.DTICRchanval]
            dtcor = np.exp(float(self.ps.deadtimevalue.getvalue()) * 1e-6 * icr)
            xdat = xdat * dtcor
        if self.ps.dodt.get() == 1 and not ynodt:
            # DT: corFF=FF*exp(tau*1e-6*ICR)
            icr = buf['data'].data.get(self.ps.DTICRchanval)  # [:,:,self.DTICRchanval]
            dtcor = np.exp(float(self.ps.deadtimevalue.getvalue()) * 1e-6 * icr)
            ydat = ydat * dtcor
        for i in range(len_x):
            for j in range(len_y):
                if not globalfuncs.point_inside_polygon(xdat[i, j], ydat[i, j], self.ps.cpmask.maskpts):
                    cpmask[i, j] = 0
        return cpmask

    def clearcpmask(self,replot=True):
        #clear mask
        self.ps.cpmask.clear()
        
        
        globalfuncs.setstatus(self.cpstatus,"Mask cleared")
        if self.CPColorRegion.get()=="Highlight Mask":
            self.checkcorplot()
            return
        self.cpgraph.removeplot('MASK')
        self.cpgraph.draw()
##        glist=self.cpgraph.element_names()
##        if 'MASK' in glist:
##            self.cpgraph.element_delete('MASK')         
##        #revive image?
        globalfuncs.setstatus(self.cpstatus,"Mask cleared")

    def catchmaskclick(self,event):
        if event.dblclick: self.finishmask(event)
        else: self.addpointtomask(event)
      
    def addpointtomask(self,event):
        print(event.xdata,event.ydata)
        if event.xdata is None or event.ydata is None:
            print("out of graph")
            return       
        self.ps.cpmask.maskx.append(event.xdata)
        self.ps.cpmask.masky.append(event.ydata)
        self.ps.cpmask.maskpts.append((event.xdata,event.ydata))
        #if mask exist, remove...
        self.cpgraph.removeplot('MASK')
##        glist=self.cpgraph.element_names()
##        if 'MASK' in glist:
##            self.cpgraph.element_delete('MASK') 
        #self.cpgraph.line_create('MASK',xdata=tuple(self.ps.cpmask.maskx),ydata=tuple(self.ps.cpmask.masky),pixels=2,linewidth=1,color='red')
        self.cpgraph.plot(tuple(self.ps.cpmask.maskx),tuple(self.ps.cpmask.masky),text='MASK',symbol='o',size=6,color='red')
        self.cpgraph.draw()

    def finishmaskkey(self,event):
        print('esc event')
        self.finishmask(event,cap=0)

    def finishmaskmenu(self):
        self.finishmask(None, cap = 0)

    def finishmask(self,event,cap=1):
        if cap:
            if event.xdata is not None and event.ydata is not None:
                self.ps.cpmask.maskx.append(event.xdata)
                self.ps.cpmask.masky.append(event.ydata)
        self.ps.cpmask.maskx.append(self.ps.cpmask.maskx[0])
        self.ps.cpmask.masky.append(self.ps.cpmask.masky[0])
        #if mask exist, remove...
        self.cpgraph.removeplot('MASK')
##        glist=self.cpgraph.element_names()
##        if 'MASK' in glist:
##            self.cpgraph.element_delete('MASK') 
        #self.cpgraph.line_create('MASK',xdata=tuple(self.ps.cpmask.maskx),ydata=tuple(self.ps.cpmask.masky),pixels=2,linewidth=1,color='red')
        #unbind graph
        #self.cpgraph.canvas.mpl_disconnect(self.finishmaskEventCatch)
        #self.finishmaskEventCatch=None
        self.cpgraph.canvas.mpl_disconnect(self.addpointtomaskEventCatch)
        self.addpointtomaskEventCatch=None
        #self.cpgraph.canvas.mpl_disconnect(self.finishmaskEventCatch2)
        #self.finishmaskEventCatch2=None
        self.win.unbind("<End>")
        
        globalfuncs.setstatus(self.cpstatus,"Finding mask points")
        #find points
        self.ps.cpmask.mask = self.findcpmaskpoints(self.ps.activeFileBuffer)

        if self.CPColorRegion.get()=="Highlight Mask":
            self.checkcorplot()
        self.cpgraph.plot(tuple(self.ps.cpmask.maskx),tuple(self.ps.cpmask.masky),text='MASK',symbol='o',size=6,color='red')
        self.cpgraph.draw()

        globalfuncs.setstatus(self.cpstatus,"Mask complete")

    def cpcoordreport(self,event):
        #(x,y)=self.cpgraph.invtransform(event.x,event.y)
        xtext="X="+str(event.xdata)
        ytext="Y="+str(event.ydata)
        xtext=xtext[:12]
        ytext=ytext[:12]
        globalfuncs.setstatus(self.cpxcoord,xtext)
        globalfuncs.setstatus(self.cpycoord,ytext)

    def checkcorplotx(self, *args):
        self.cpxchan.focus_set()
        self.checkcorplot()

    def checkcorploty(self, *args):
        self.cpychan.focus_set()
        self.checkcorplot()

    def corplotRegress(self):
        if self.cpxchan.getvalue()==() or self.cpychan.getvalue()==():
            return
        xind=self.mapdata.labels.index(self.cpxchan.getvalue()[0])+2
        yind=self.mapdata.labels.index(self.cpychan.getvalue()[0])+2
        xdata=self.mapdata.data.get(xind)
        ydata=self.mapdata.data.get(yind)
        cpm=self.ps.cpmask.mask
        if len(self.ps.cpmask.mask)==0:
            cpm=np.zeros((self.mapdata.data.shape[0],self.mapdata.data.shape[1]),dtype=np.float32)
        if self.ps.zmxyi[2]!=-1 and self.ps.zmxyi[3]!=-1:
            xdata=xdata[::-1,:]
            ydata=ydata[::-1,:]
            xdata=xdata[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
            ydata=ydata[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
            xdata=xdata[::-1,:]
            ydata=ydata[::-1,:]
            cpm=cpm[::-1,:]
            cpm=cpm[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
            cpm=cpm[::-1,:]
        if self.CPColorRegion.get()=="Highlight Mask":
            xdata=xdata[np.where(cpm>0)]
            ydata=ydata[np.where(cpm>0)]
        xv=np.ravel(xdata)
        yv=np.ravel(ydata)
        #passdata=[]
        #for i in range(len(xv)):
        #    passdata.append((xv[i],yv[i]))
        text="Fitting correlations..."
        if self.CPColorRegion.get()=="Highlight Mask": text="Fitting correlation in masked area..."
        globalfuncs.setstatus(self.cpstatus,text)
        initguess=(1,0)  #slope, int
        try:
            #result=leastSquaresFit(globalfuncs.lineareqn,initguess,passdata)
            result,cov=curve_fit(globalfuncs.perform_affine_transform,xv,yv,p0=initguess)
            fp=result
            cfit=globalfuncs.lineareqn(fp,xv)
        except:
            fp=None
        #make line for plot:
        
        #calculate r2
        if fp is None:
            r2=0
            fp=(0,0)
        else:
            m=np.mean(yv)
            sstot=sum((yv-m)**2)
            sserr=sum((yv-cfit)**2)
            r2=1-sserr/sstot
        #plot it
        self.checkcorplot()
        #self.cpgraph.line_create('CP',xdata=tuple(xv),ydata=tuple(cfit),symbol='none',linewidth=1,pixels=1,color='red')        
        self.cpgraph.plot(tuple(xv),tuple(cfit),text='CV',color='red')        
        self.cpgraph.draw()
        
        globalfuncs.setstatus(self.cpstatus,"CORRPLOT: slope="+str(fp[0])+"   int="+str(fp[1])+"   R2="+str(r2))
        print("CORRPLOT: slope="+str(fp[0])+" int="+str(fp[1])+" R2="+str(r2))

    def corplotMultRegress(self):
        if self.cpxchan.getvalue()==() or self.cpychan.getvalue()==():
            return
        maxN=tkinter.simpledialog.askinteger(title='Multi Regression ',prompt='Enter number of slopes to fit:',initialvalue=2)
        if maxN<1: maxN=1
        xind=self.mapdata.labels.index(self.cpxchan.getvalue()[0])+2
        yind=self.mapdata.labels.index(self.cpychan.getvalue()[0])+2
        xdata=self.mapdata.data.get(xind)
        ydata=self.mapdata.data.get(yind)
        cpm=self.ps.cpmask.mask
        if len(self.ps.cpmask.mask)==0:
            cpm=np.zeros((self.mapdata.data.shape[0],self.mapdata.data.shape[1]),dtype=np.float32)
        if self.ps.zmxyi[2]!=-1 and self.ps.zmxyi[3]!=-1:
            xdata=xdata[::-1,:]
            ydata=ydata[::-1,:]
            xdata=xdata[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
            ydata=ydata[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
            xdata=xdata[::-1,:]
            ydata=ydata[::-1,:]
            cpm=cpm[::-1,:]
            cpm=cpm[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
            cpm=cpm[::-1,:]
        if self.CPColorRegion.get()=="Highlight Mask":
            xdata=xdata[np.where(cpm>0)]
            ydata=ydata[np.where(cpm>0)]
        xv=np.ravel(xdata)
        yv=np.ravel(ydata)
        #passdata=[]
        #for i in range(len(xv)):
        #    passdata.append((xv[i],yv[i]))
        text="Fitting correlations..."
        if self.CPColorRegion.get()=="Highlight Mask": text="Fitting correlation in masked area..."
        globalfuncs.setstatus(self.cpstatus,text)
        fitobj=MultiFitObj(xv,yv,maxN)
        
#        try:
            #result=leastSquaresFit(globalfuncs.lineareqn,initguess,passdata)
        result=minimize(fitobj.eqn,fitobj.initguess,method = 'Nelder-Mead')
        fp=result.x
        print(result.message)
        print(fp)
        fitobj.calc(fp)
#        except:
#            print result.message
#            fp=None
        #make line for plot:
        
        #plot it
        self.checkcorplot()
        #self.cpgraph.line_create('CP',xdata=tuple(xv),ydata=tuple(cfit),symbol='none',linewidth=1,pixels=1,color='red')        
        if fp is None: return
        i=1
        mt=''
        for xfit,cfit in zip(fitobj.xpvs,fitobj.yfit):
            self.cpgraph.plot(tuple(xfit),tuple(cfit),text='CV'+str(i),color='red')  
            mt+="m"+str(i)+": "+str(fp[i-1])+"    "
            i+=1
        self.cpgraph.draw()
        
        globalfuncs.setstatus(self.cpstatus,"MULTCORRPLOT: "+mt)
        print("MULTCORRPLOT: "+mt)
        
    def corplotDTfit(self):
        if self.cpxchan.getvalue()==() or self.cpychan.getvalue()==():
            return
        xind=self.mapdata.labels.index(self.cpxchan.getvalue()[0])+2
        yind=self.mapdata.labels.index(self.cpychan.getvalue()[0])+2
        xdata=self.mapdata.data.get(xind)
        ydata=self.mapdata.data.get(yind)
        if self.ps.zmxyi[2]!=-1 and self.ps.zmxyi[3]!=-1:
            xdata=xdata[::-1,:]
            ydata=ydata[::-1,:]
            xdata=xdata[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
            ydata=ydata[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
            xdata=xdata[::-1,:]
            ydata=ydata[::-1,:]
        xv=np.ravel(xdata)
        xv=np.sort(xv)
        yv=np.ravel(ydata)
        yv=np.sort(yv)
        #passdata=[]
        #for i in range(len(xv)):
        #    passdata.append((xv[i],yv[i]))
        globalfuncs.setstatus(self.cpstatus,"Fitting deadtimes...")            
        #fit the deadtime curves!  use SCA=kappa*ICR*exp(-ICR*tau) taus in usec
        initguess=(0.5,1,0)  #kappa,tau(usec)
        try:
            #result=leastSquaresFit(dteqn,initguess,passdata)
            result,cov=curve_fit(FittingFunctions.dteqnFit,xv,yv,p0=initguess)
            fp=result
        except:
            fp=(0,0,0)
        dtfit=FittingFunctions.dteqn(fp,xv)
        #plot it
        self.checkcorplot()
        #self.cpgraph.line_create('DT',xdata=tuple(xv),ydata=tuple(dtfit),symbol='none',linewidth=1,pixels=1,color='orange')        
        self.cpgraph.plot(tuple(xv),tuple(dtfit),text='DT',color='orange')        
        self.cpgraph.draw()
        
        #call up deatime dialog and place fitted value in.            
        self.ps.deadtimevalue = self.ps.deadtimecorrection(iv=fp[1])
        #self.ps.deadtimevalue.setvalue()
        #self.ps.deadtimecorrection.hide() #deadtimedialog.withdraw()
        globalfuncs.setstatus(self.cpstatus,"DEADTIME: "+str(fp[1]))

    def assembleCorBuffData(self,xch,ych,bufn,xmax,ymax):
        #check for existence of channels
        buf = self.ps.dataFileBuffer[bufn]
        if xch not in buf['data'].labels:
            return False,[]
        if ych not in buf['data'].labels:
            return False,[]
        xind = buf['data'].labels.index(xch) + 2
        yind = buf['data'].labels.index(ych) + 2
        xdata = buf['data'].data.get(xind)
        ydata = buf['data'].data.get(yind)

        if self.ps.dodt.get() == 1: icr = self.mapdata.data.get(self.ps.DTICRchanval)
        if buf['zoom'][2] != -1 and buf['zoom'][3] != -1:
            xdata = xdata[::-1, :]
            ydata = ydata[::-1, :]
            xdata = xdata[buf['zoom'][1]:buf['zoom'][3], buf['zoom'][0]:buf['zoom'][2]]
            ydata = ydata[buf['zoom'][1]:buf['zoom'][3], buf['zoom'][0]:buf['zoom'][2]]
            xdata = xdata[::-1, :]
            ydata = ydata[::-1, :]
            if self.ps.dodt.get() == 1:
                icr = icr[::-1, :]
                icr = icr[buf['zoom'][1]:buf['zoom'][3], buf['zoom'][0]:buf['zoom'][2]]
                icr = icr[::-1, :]

        if self.ps.dodt.get() == 1: icr = np.ravel(icr)

        xv = np.ravel(xdata)
        yv = np.ravel(ydata)

        nodtx = 0
        nodty = 0
        if xch in ['ICR', 'I0', 'I1', 'I2', 'I0STRM', 'I1STRM', 'I2STRM']: nodtx = 1
        if ych in ['ICR', 'I0', 'I1', 'I2', 'I0STRM', 'I1STRM', 'I2STRM']: nodty = 1
        if self.ps.dodt.get() == 1 and not nodtx:
            # DT: corFF=FF*exp(tau*1e-6*ICR)
            # icr=self.mapdata.data.get(self.DTICRchanval)#np.ravel(tdata[:,:,self.DTICRchanval])
            dtcor = np.exp(float(self.ps.deadtimevalue.getvalue()) * 1e-6 * icr)
            xv = xv * dtcor
        if self.ps.dodt.get() == 1 and not nodty:
            # DT: corFF=FF*exp(tau*1e-6*ICR)
            # icr=self.mapdata.data.get(self.DTICRchanval)#np.ravel(tdata[:,:,self.DTICRchanval])
            dtcor = np.exp(float(self.ps.deadtimevalue.getvalue()) * 1e-6 * icr)
            yv = yv * dtcor

            # normalize to max w/ sliders
        xvm = max(xv) * xmax
        yvm = max(yv) * ymax
        remx = np.where(np.greater(xv, xvm), 0, 1)
        remy = np.where(np.greater(yv, yvm), 0, 1)
        remtot = remx * remy

        return True,[xv,yv,remtot]

    def updateMulticorplot(self, *args):
        #plot the corplot for all open files...
        if self.cpxchan.getvalue()==() or self.cpychan.getvalue()==():
            return

        if self.multiCorGraph is not None:
            plt.close(self.multiCorGraph.fig)
        self.multiCorGraph = sblite.GridPlot(len(list(self.ps.dataFileBuffer.keys())), layout_pad=2.75)
        for i,bufn in enumerate(self.ps.dataFileBuffer.keys()):
            valid, retvals = self.assembleCorBuffData(self.cpxchan.getvalue()[0], self.cpychan.getvalue()[0],
                                                      bufn, self.cpxintensity.get(), self.cpyintensity.get())
            if not valid:
                print()
                'CP channels not found in data file', bufn
                continue
            xvi = retvals[0]*retvals[2]
            yvi = retvals[1]*retvals[2]
            self.multiCorGraph = self.multiCorGraph.add([xvi, yvi],
                                                        [self.cpxchan.getvalue()[0], self.cpychan.getvalue()[0]],
                                                        bufn, plt.scatter, s=2)
        plt.show(block=False)

    def updatezoom(self, zoom):
        self.ps.zmxyi = zoom 

    def checkcorplot(self, *args, **kwargs):
        if 'dtval' in kwargs:
            self.ps.DTICRchanval = kwargs['dtval']
        #check to make sure both axes are selected...
        if self.cpxchan.getvalue()==() or self.cpychan.getvalue()==():
            return
        self.ps.dataFileBuffer[self.ps.activeFileBuffer]['zoom']=self.ps.zmxyi
        valid,retvals = self.assembleCorBuffData(self.cpxchan.getvalue()[0], self.cpychan.getvalue()[0], self.ps.activeFileBuffer,self.cpxintensity.get(),self.cpyintensity.get())
        if not valid:
            print('CP channels not found in data file')
            return
        xv=retvals[0]
        yv=retvals[1]
        remtot=retvals[2]

        cpm=self.ps.cpmask.mask
        if len(self.ps.cpmask.mask)==0:
            cpm=np.zeros((self.mapdata.data.shape[0],self.mapdata.data.shape[1]),dtype=np.float32)        
        if self.ps.zmxyi[2]!=-1 and self.ps.zmxyi[3]!=-1:
            cpm=cpm[::-1,:]
            cpm=cpm[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
            cpm=cpm[::-1,:]
        cpm=np.ravel(cpm)
        #remove graph if present
        self.cpgraph.cleargraphs()
##        glist=self.cpgraph.element_names()
##        if glist != ():
##            for g in glist:
##                self.cpgraph.element_delete(g) 
        #make new
#!      Change colors doesn't quite work as hoped yet...
        globalfuncs.setstatus(self.cpstatus,"calculating plot...")
        try:
            self.cpgraph.changeBackColor(self.corplotcolors[0])
        except:
            print("background color not changing as expected.")
        self.cpgraph.setLabels(self.cpxchan.getvalue()[0],self.cpychan.getvalue()[0])
        #self.cpgraph.xaxis_configure(title=self.cpxchan.getvalue()[0])
        #self.cpgraph.yaxis_configure(title=self.cpychan.getvalue()[0])
        #self.cpgraph.line_create('XY',xdata=tuple(xv*remtot),ydata=tuple(yv*remtot),symbol='circle',linewidth=0,pixels=1,color=self.corplotcolors[1])
        if self.CPPlotType.get()=='Density':
            self.cpgraph.hexplot(tuple(xv*remtot),tuple(yv*remtot),text='XY',symbol='.',size=self.corplotcolors[2],linewidth=0,color=self.corplotcolors[1])
        elif self.CPPlotType.get()=='LogDensity':
            self.cpgraph.hexplot(tuple(xv*remtot),tuple(yv*remtot),text='XY',symbol='.',size=self.corplotcolors[2],linewidth=0,color=self.corplotcolors[1],log=1)
        else:
            if self.CPColorRegion.get()!="Cluster":
                if self.CPColorRegion.get()=="MultiFile":
                    #iterate and calculate...
                    palette = sblite.color_palette(n_colors=len(list(self.ps.dataFileBuffer.keys())))
                    cpmulticolors = palette.as_hex() #['#665191','#a05195','#d45087','#f95d6a','#ff7c43','#ffa600']
                    i=0
                    for bufn in list(self.ps.dataFileBuffer.keys()):
                        if self.ps.activeFileBuffer==bufn:
                            continue
                        valid, retvals = self.assembleCorBuffData(self.cpxchan.getvalue()[0], self.cpychan.getvalue()[0],
                                                             bufn, self.cpxintensity.get(),self.cpyintensity.get())
                        if not valid:
                            print('CP channels not found in data file',bufn)
                            continue
                        xvi = retvals[0]
                        yvi = retvals[1]
                        remtoti = retvals[2]
                        self.cpgraph.plot(tuple(xvi*remtoti),tuple(yvi*remtoti),text='XY'+str(i),symbol='.',size=self.corplotcolors[2],linewidth=0,color=cpmulticolors[i%6])
                        i+=1
                if self.ps.useMaskforCorPlotData.get()==1:
                    self.cpgraph.plot(tuple((xv*remtot)[np.where(cpm>0)]),tuple((yv*remtot)[np.where(cpm>0)]),text='XY',symbol='.',size=self.corplotcolors[2],linewidth=0,color=self.corplotcolors[1])
                else:
                    self.cpgraph.plot(tuple(xv*remtot),tuple(yv*remtot),text='XY',symbol='.',size=self.corplotcolors[2],linewidth=0,color=self.corplotcolors[1])
            else:
                i=self.mapdata.labels.index(self.ps.datachanCB(0)) #self.datachan.getvalue()[0])
                fd=self.mapdata.data.get(i+2)
                if self.ps.zmxyi[2]!=-1 and self.ps.zmxyi[3]!=-1:
                    fd=fd[::-1,:]
                    fd=fd[self.ps.zmxyi[1]:self.ps.zmxyi[3],self.ps.zmxyi[0]:self.ps.zmxyi[2]]
                    fd=fd[::-1,:]
                fd=np.ravel(fd)
                u = 1
                m = max(fd)
                b = np.mod(fd,1)
                if m>128: 
                    u=0
                    print (1)
                if sum(abs(b))>0: 
                    u=1
                    print (2)
                if len(np.where(self.mapdata.data.get(i+2)<0)[0])>1: 
                    u=0
                    print (3)
                if u==0:
                    print('Not valid cluster')
                    self.cpgraph.plot(tuple(xv*remtot),tuple(yv*remtot),text='XY',symbol='.',size=self.corplotcolors[2],linewidth=0,color=self.corplotcolors[1])
                else:
                    cpcmap=self.ps.colormapCB(asText=True)
                    for i in range(int(m)+1):
                        cvind=int(float(i)/m*255.)
                        cvrgb=cpcmap[cvind]
                        cvhex='#%02x%02x%02x' % tuple(cvrgb)
                        self.cpgraph.plot(tuple((xv*remtot)[np.where(fd==i)]),tuple((yv*remtot)[np.where(fd==i)]),text='XY2',symbol='.',size=self.corplotcolors[2],linewidth=0,color=cvhex)              
                    
            if self.CPColorRegion.get()=="Highlight Mask":
                self.cpgraph.plot(tuple((xv*remtot)[np.where(cpm>0)]),tuple((yv*remtot)[np.where(cpm>0)]),text='XY2',symbol='.',size=self.corplotcolors[2],linewidth=0,color='cyan')
        #check for sqrt
        if self.ps.corplotSQRT.get():
            sqrtdata=xv.copy()
            sqrtdata=sqrtdata*remtot
            sqrtdata=np.sort(sqrtdata)
            step = int(sqrtdata[-1]/50.)
            if step==0: step=1
            sqrtx=list(range(0,int(sqrtdata[-1]),step))
            sqrtdata=np.sqrt(sqrtx)
            #self.cpgraph.line_create('SQRT',xdata=tuple(sqrtx),ydata=tuple(sqrtdata),symbol='none',linewidth=1,pixels=1,color='yellow')
            self.cpgraph.plot(tuple(sqrtx),tuple(sqrtdata),text='SQRT',color='yellow')
        self.cpgraph.draw()
        globalfuncs.setstatus(self.cpstatus,"Ready")
        
    def corplotcolorswap(self):
        if self.corplotcolors==['black','green',5,'0.75']:
            self.corplotcolors=['white','black',1,'0.2']
        else:
            self.corplotcolors=['black','green',5,'0.75']
        self.checkcorplot()

    def localexportcorplot(self):
        text = self.assemblecordata()
        self.ps.exportcorplot(text)
    
    def assemblecordata(self):
        #return correlation plot data
        text=''
        datay=[]
        datax=[]
        temp=self.cpgraph.get_xdata('XY')#element_configure('XY','xdata')
        datax.append(temp)
        temp=self.cpgraph.get_ydata('XY')#element_configure('XY','ydata')
        datay.append(temp)
        text=text+self.cpxchan.getvalue()[0]+'\t'+self.cpychan.getvalue()[0]+'\n'
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


    #these move between channels in the correlation plotter 
    def arrowcpxchan(self,event):
        dlist=self.cpxchan.get()
        ind=dlist.index(self.cpxchan.getvalue()[0])
        if event.keysym == 'Down':
            ind=ind+1
        if event.keysym == 'Up':
            ind=ind-1
        if ind<0: ind=0
        if ind>len(dlist)-1: ind=len(dlist)-1
        self.cpxchan.setvalue(dlist[ind])
        self.cpxchan.see(ind)
        self.checkcorplotx()

    def arrowcpychan(self,event):
        dlist=self.cpychan.get()
        ind=dlist.index(self.cpychan.getvalue()[0])
        if event.keysym == 'Down':
            ind=ind+1
        if event.keysym == 'Up':
            ind=ind-1
        if ind<0: ind=0
        if ind>len(dlist)-1: ind=len(dlist)-1
        self.cpychan.setvalue(dlist[ind])
        self.cpychan.see(ind)
        self.checkcorploty()