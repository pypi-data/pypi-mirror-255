#standard
import itertools
import math
import os
import random
import sys
import tkinter

#third party
import cv2 as cv
import numpy as np
import Pmw
from scipy.optimize import curve_fit
from scipy.optimize import minimize
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from sklearn.metrics import r2_score
import sortedcontainers

#local
import ConcentrationStandardClass
import globalfuncs
from MasterClass import MasterClass
import MomentMathClass
import MultiFitObj
import mucal
import MyGraph
import PmwTtkButtonBox
import PmwTtkNoteBook
import PmwTtkRadioSelect
import ScrollTree


class MultiMassCalibrationWindowParams():
    def __init__(self, useMask, useWater, status, isStatCalcMultiFile, activeFileBuffer, dataFileBuffer, datachan, partROIThresh, nullMaskCalc, domapimage,maindisp, usemaskinimage, showmap, filedir, SAMmasks=None):
        self.useMask = useMask
        self.status = status
        self.useWater = useWater
        self.isStatCalcMultiFile = isStatCalcMultiFile
        self.activeFileBuffer = activeFileBuffer
        self.dataFileBuffer = dataFileBuffer
        self.datachan = datachan
        self.partROIThresh = partROIThresh
        self.nullMaskCalc = nullMaskCalc
        self.domapimage = domapimage
        self.maindisp = maindisp
        self.usemaskinimage = usemaskinimage
        self.showmap = showmap
        self.SAMmasks = SAMmasks
        self.filedir=filedir

class MultiMassCalibrationWindow(MasterClass):
    def _params(self):
        self.partStatuseMask=self.ps.useMask



    def initcalc(self):

        self.partStatuseWater=self.ps.useWater
        self.partstatROIflag=0
        #check for multi and same channels in all files?
        bufs=[]
        commonchanlist=list(self.mapdata.labels)
        if self.ps.isStatCalcMultiFile.get():
            for buf in list(self.ps.dataFileBuffer.values()):
                if self.ps.datachan.get()[0] not in buf['data'].labels:
                    print('Threshold channel ',self.ps.datachan.get()[0],' does not exist in ',buf['name'])
                    continue
                bufs.append(buf['name'])
                commonchanlist=[e for e in commonchanlist if e in buf['data'].labels]
        else:
            bufs=[self.ps.activeFileBuffer]
        if len(bufs)==0 or len(commonchanlist)==0:
            print('No data channels in common between data files...')
            return
        self.partroilist=[]
        self.pstatdict={}

        if self.partStatuseMask:
            curch=self.ps.datachan.getvalue()[0]
            curind=self.mapdata.labels.index(curch)
            u=1
            m=max(np.ravel(self.mapdata.data.get(curind+2)))+1
            b=np.mod(np.ravel(self.mapdata.data.get(curind+2)),1)
            if m>31: u=0
            if sum(abs(b))>0: u=0
            if len(np.where(self.mapdata.data.get(curind+2)<0)[0])>1: u=0
            if u==0:
                if not tkinter.messagebox.askokcancel('Masked Statistics','Current selected data does not appear to be a mask set.  Continue?'):
                    globalfuncs.setstatus(self.ps.status,'Masked Statistics cancelled')
                    return -1

            for bufn in bufs:
                globalfuncs.setstatus(self.ps.status,"Calculating mask areas from "+self.ps.datachan.getvalue()[0]+" in "+bufn)
                buf=self.ps.dataFileBuffer[bufn]
                datind=buf['data'].labels.index(self.ps.datachan.getvalue()[0])+2
                data=buf['data'].data.get(datind)#[:,:,datind]
                mn=globalfuncs.powernext(int(max(np.ravel(data))))/2
                mn=globalfuncs.powerrange(mn)

                nn=0
                for n in mn:
                    if nn==0 and self.ps.nullMaskCalc.get()==0:
                        nn+=1
                        continue
                    f=self.decodeCHANmask(data,n)
                    item = PartROIlistItem([n+1,'ROI '+str(nn),f,nn,bufn,False,None])
                    self.partroilist.append(item)
                    nn+=1
        elif self.ps.SAMmasks is not None:
            nn=0
            for m in self.ps.SAMmasks:
                item = PartROIlistItem([nn+1, 'ROI '+str(nn+1),m,nn+1,bufs[0],False,None])
                self.partroilist.append(item)
                nn+=1
                self.partStatuseMask=1
                self.ps.useMask=1
        else:
            for bufn in bufs:
                globalfuncs.setstatus(self.ps.status,"Calculating particle contours from "+self.ps.datachan.getvalue()[0]+" in "+bufn)
                buf=self.ps.dataFileBuffer[bufn]
                datind=buf['data'].labels.index(self.ps.datachan.getvalue()[0])+2
                data=buf['data'].data.get(datind)#[:,:,datind]
                data=np.array(data,dtype=np.float32)
                inp=data#cv.fromarray(data)
                out=data#cv.fromarray(data)
                #inp8=cv.CreateMat(inp.rows,inp.cols,cv.CV_8UC1)
                inp8 = inp.astype(np.uint8)
                #cv.Convert(inp,inp8)
                #out8=cv.CreateMat(inp.rows,inp.cols,cv.CV_8UC1)
                #out8=np.array(inp.rows,inp.cols,cv.CV_8UC1)
                out8 = out.astype(np.uint8)
                #storage=cv.CreateMemStorage()
                #self.contoursSeq=cv.findContours(inp8,cv.CV_RETR_CCOMP,cv.CV_CHAIN_APPROX_SIMPLE)
                self.contoursSeq =cv.findContours(inp8,cv.RETR_CCOMP,cv.CHAIN_APPROX_SIMPLE)[0]


                #f=self.contoursSeq
                n=0
                #while f is not None:
                for f in self.contoursSeq:
                    #check area
                    mask=np.asarray(self.makeROImask(f,np.zeros(buf['data'].data.get(0).shape)))
                    s=sum(np.ravel(mask))
                    if s>=self.ps.partROIThresh:
                        n+=1
                        #print(n)
                        item = PartROIlistItem([n,'ROI '+str(n),f,n,bufn,False,None])
                        self.partroilist.append(item)
                    #r=random.randint(0,255)
                    #cv.DrawContours(inp8,f,cv.RGB(r,r,r),cv.RGB(r,r,r),0,cv.CV_FILLED)
                    #f=f.h_next()
        #        self.savedeconvcalculation(np.asarray(inp8),'cont')

                    
        globalfuncs.setstatus(self.ps.status,"Calculation complete")

        #now create dialog...
        self.partStatuseMask=self.ps.useMask
        self.partStatuseWater=self.ps.useWater
        self.partstatROIflag=0

        return commonchanlist

    def _buildpstatlist(self):
        self.pstatlistlines={}

        i=1
        for r in self.partroilist:
            buf=self.ps.dataFileBuffer[r.buffer]
            xcds=buf['data'].data.get(1)  # [:,:,1]
            ycds=buf['data'].data.get(0)  # [:,:,0]

            if self.partStatuseMask:
                mask=r.mask
            else:
                mask=np.asarray(self.makeROImask(r.mask,np.zeros(buf['data'].data.get(0).shape)))
            d=MomentMathClass.MomentClass(xcds,ycds,mask,all=3)
            area=d.A
            xcp=d.medx
            ycp=d.medy

            #these are pixels from the bottom left corner...
            xc=xcp#x0+xcp*xs
            yc=ycp#y0+ycp*ys
            if r.isSelected:
                seltxt="X"
            else:
                seltxt=" "
            if r.link is not None:
                linktxt=r.link
            else:
                linktxt=" "
            #Old Version
            #newitem=self.pstatlist.insert((seltxt,r.buffer,r.label,linktxt,area,globalfuncs.valueclip_d(xc,5),globalfuncs.valueclip_d(yc,5)))

            #Tracy Request
            newitem=self.pstatlist.insert((seltxt,r.buffer,r.label,linktxt,area,globalfuncs.valueclip_d(xc,0),globalfuncs.valueclip_d(yc,0)))
            l={}
            l['area']=area
            l['xcenter']=xc
            l['ycenter']=yc
            self.pstatdict[r.buffer+"*"+r.label]=l
            self.pstatlistlines[r.label]=newitem
            
            if i%10==0: print (i)
            i+=1

    def _create(self):
        self._params()
        commonchanlist=self.initcalc()
        if commonchanlist == -1: return
        #now create dialog...
        self.win=Pmw.MegaToplevel(self.imgwin)
        self.win.title('Quantitative Calibration')
        self.win.userdeletefunc(func=self.kill)
        
        hm=self.win.interior()
        hm.configure(background='#d4d0c8')
        
        if True: #sys.platform=='darwin':
            #mac specific layout as notebook has weird behavior?
 
            #h2=Pmw.ScrolledFrame(hm,usehullsize=1,vertflex='fixed',horizflex='fixed',hscrollmode='static',vscrollmode='static',hull_width=1200,hull_height=1100)
            h2=Pmw.ScrolledFrame(hm,usehullsize=1,vertflex='fixed',horizflex='fixed',hscrollmode='static',vscrollmode='static',hull_width=1200,hull_height=800)

            h2.interior().configure(background='#d4d0c8')
            h2.pack(side=tkinter.TOP,pady=2)
            h=h2.interior()
            #h=hm
        else:
            h=hm
            
        lf=tkinter.Frame(h,background='#d4d0c8')
        lf.pack(side=tkinter.LEFT,fill='both')
        self.leftframe=lf
        #data selections
        self.partstatsel=Pmw.ScrolledListBox(lf,labelpos='n',label_text='Select Channel',items=commonchanlist,listbox_selectmode=tkinter.EXTENDED,
                                              listbox_exportselection=tkinter.FALSE,selectioncommand=self.updateMultiMass,listbox_height=15,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.partstatsel.pack(side=tkinter.TOP,padx=4,pady=5,fill='both')
        self.partseltype=PmwTtkRadioSelect.PmwTtkRadioSelect(lf,buttontype='button',orient='vertical',command=self.updateMultiMass,selectmode='single',labelpos='n',label_text='Analysis Type',hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        for text in ('Sum','Mean','Median','Mode'):
            self.partseltype.add(text)
        self.partseltype.setvalue('Mean')
        self.partseltype.pack(side=tkinter.TOP,padx=3,pady=3)
        #notebook
        rf=tkinter.Frame(h,background='#d4d0c8')
        rf.pack(side=tkinter.LEFT,fill='both',expand=1)
        self.rightframe=rf
        
        if True: #sys.platform=="darwin":
            ii=rf

            topCon = tkinter.Frame(ii, background='#d4d0c8')
            topCon.pack(side=tkinter.TOP,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            botCon = tkinter.Frame(ii, background='#d4d0c8')
            botCon.pack(side=tkinter.TOP,padx=2,pady=2, fill=tkinter.BOTH, expand=1)

            topConR = tkinter.Frame(h, background='#d4d0c8')
            topConR.pack(side=tkinter.TOP,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            botConR = tkinter.Frame(h, background='#d4d0c8')
            botConR.pack(side=tkinter.TOP,padx=2,pady=2, fill=tkinter.BOTH, expand=1)


            pstatDef = tkinter.Frame(topCon, relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
            pstatDef.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)

            pstatCalib = tkinter.Frame(topConR, relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
            pstatCalib.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            

           
            
            pstatResults = tkinter.Frame(botCon, relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
            pstatResults.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            pstatPlot = tkinter.Frame(botConR, relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
            pstatPlot.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)



            l=tkinter.Label(pstatDef,text="ROI Definitions",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)        
            #l=tkinter.Label(pstatBox,text="Box Plots",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            #l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)        
            l=tkinter.Label(pstatCalib,text="Calibrant Definitions",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)        
            l=tkinter.Label(pstatResults,text="Results",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4) 
            l=tkinter.Label(pstatPlot,text="Plot",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)    
            
            self.killwidlist=[pstatDef,pstatCalib,botCon,topCon,ii,pstatResults,pstatPlot]
        
        else:
            #windoze                
            plotnb=PmwTtkNoteBook.PmwTtkNoteBook(rf)
            plotnb.configure(hull_background='#d4d0c8',hull_width=450,hull_height=400)
            plotnb.pack(side=tkinter.TOP,fill='both',expand=1,padx=3,pady=3)
            #pages
            pstatDef=plotnb.add('ROI Definitions',page_background='#d4d0c8')
            pstatResults=plotnb.add('Results',page_background='#d4d0c8')
            pstatCalib=plotnb.add('Calibrant Definitions',page_background='#d4d0c8')
        

        #build the page...
        
        # #link button (ADD)
        # b=PmwTtkButtonBox.PmwTtkButtonBox(pstatDef,orient='horizontal',hull_background='#d4d0c8')
        # b.add('Link Selections',command=self.linkSelectedROI,style='BROWN.TButton',width=15)  
        # b.add('Setup SingleCalib',command=self.setupSingle,style='LGREEN.TButton',width=20) 
        # b.add('Setup MultiCalib',command=self.setupMulti,style='GREEN.TButton',width=20) 
        # b.pack(side=tkinter.TOP,padx=5,pady=10)  
        
        
        # #individual
        # self.pstatlist=ScrollTree.ScrolledTreeViewBox(pstatDef,width=450,height=165)
        # self.pstatlist.setMode('browse')
        # self.pstatlist.setColNames(('Sel','File','ROI#', 'StdLink','Npix', 'Xcent', 'Ycent'))
        # self.pstatlist.setDefaultWA()
        # self.pstatlist.setSelect(self.partSelectROIList)
        # self.pstatlist.setColors(('white', '#ffdddd', 'white', '#ddeeff'))
        # self.pstatlist.pack(side=tkinter.TOP,padx=2,pady=4,expand=1,fill='x')
        
        # self._buildpstatlist()
        
        # self.pstatindview=Pmw.RadioSelect(pstatDef,buttontype='radiobutton',orient='vertical',command=self.partSelectROIList,hull_background='#d4d0c8')
        # for text in ('Show All','Show Current','Show None'):
        #     self.pstatindview.add(text,background='#d4d0c8')
        # self.pstatindview.setvalue('Show None')
        # self.pstatindview.pack(side=tkinter.TOP,padx=3,pady=3)
        # #export button
        # b=PmwTtkButtonBox.PmwTtkButtonBox(pstatDef,orient='horizontal',hull_background='#d4d0c8')
        # b.add('Select All',command=self.selectAll,style='SBLUE.TButton',width=12) 
        # b.add('Select None',command=self.selectNone,style='NAVY.TButton',width=12) 
        # b.add('Invert Select',command=self.selectInvert,style='ORANGE.TButton',width=12) 
        # b.pack(side=tkinter.TOP,padx=5,pady=10)        

        #export button
        b=PmwTtkButtonBox.PmwTtkButtonBox(pstatDef,orient='horizontal',hull_background='#d4d0c8')
        b.add('Select All',command=self.selectAll,style='SBLUE.TButton',width=12) 
        b.add('Select None',command=self.selectNone,style='NAVY.TButton',width=12) 
        b.add('Invert Select',command=self.selectInvert,style='ORANGE.TButton',width=12) 
        b.pack(side=tkinter.TOP,padx=5,pady=10)    

        
        #individual
        self.pstatlist=ScrollTree.ScrolledTreeViewBox(pstatDef,width=450,height=165)
        self.pstatlist.setMode('browse')
        self.pstatlist.setColNames(('Sel','File','ROI#', 'StdLink','Npix', 'Xcent', 'Ycent'))
        self.pstatlist.setDefaultWA()
        self.pstatlist.setSelect(self.partSelectROIList)
        self.pstatlist.setColors(('white', '#ffdddd', 'white', '#ddeeff'))
        self.pstatlist.pack(side=tkinter.TOP,padx=2,pady=4,expand=1,fill='x')
        
        self._buildpstatlist()
        
        self.pstatindview=Pmw.RadioSelect(pstatDef,buttontype='radiobutton',orient='vertical',command=self.partSelectROIList,hull_background='#d4d0c8')
        for text in ('Show All','Show Current','Show None'):
            self.pstatindview.add(text,background='#d4d0c8')
        self.pstatindview.setvalue('Show None')
        self.pstatindview.pack(side=tkinter.TOP,padx=3,pady=3)
        
        #link button (ADD)
        b=PmwTtkButtonBox.PmwTtkButtonBox(pstatDef,orient='horizontal',hull_background='#d4d0c8')
        b.add('Link Selections',command=self.linkSelectedROI,style='BROWN.TButton',width=15)  
        b.add('Setup SingleCalib',command=self.setupSingle,style='LGREEN.TButton',width=20) 
        b.add('Setup MultiCalib',command=self.setupMulti,style='GREEN.TButton',width=20) 
        b.pack(side=tkinter.TOP,padx=5,pady=10)  
            

        #calibration defs
        
        #normalization selection 
        self.normlist=['None']
        self.normlist.extend(commonchanlist)
        self.normchannel=Pmw.ComboBox(pstatCalib,history=0,selectioncommand=self.checkNorms,hull_background='#d4d0c8',
                                      labelpos='w',label_text="Normalization Channel:  ",label_background='#d4d0c8')
        self.normchannel.setlist(self.normlist)
        self.normchannel.selectitem('None')
        self.normchannel.pack(side=tkinter.TOP,padx=5,pady=5)        

        b=PmwTtkButtonBox.PmwTtkButtonBox(pstatCalib,orient='horizontal',hull_background='#d4d0c8')
        b.add('Suggest Matches',command=self.suggestChannelMatch,style='MBLUE.TButton',width=20) 
        self.calbut = b.add('Calibrate SINGLE',command=self.calculate,style='LGREEN.TButton',width=20) 
        b.pack(side=tkinter.TOP,padx=5,pady=5)    
        #JOY
        j=Pmw.ScrolledFrame(pstatCalib,hull_width=500,hull_height=300,usehullsize=1,vertflex='expand',horizflex='expand')
        j.interior().configure(background='#d4d0c8')
        j.pack(side=tkinter.TOP)
        self.calibFrame = j
        
        self.calibGroupDict={}
        self.calibType='single'
        
        #results frame
        
        self.resultlist=ScrollTree.ScrolledTreeViewBox(pstatResults,width=450,height=200)
        self.resultlist.setMode('browse')
        self.resultlist.setColNames(('Sel','Element','Slope', 'Intercept','GOF-R2'))
        self.resultlist.setDefaultWA()
        self.resultlist.setSelect(self.resulttoggle)
        self.resultlist.setColors(('white', '#ffdddd', 'white', '#ddeeff'))
        self.resultlist.pack(side=tkinter.TOP,padx=2,pady=4,expand=1,fill='x')
        
        self.resultobj = CalibResultObject() #listforresults=[]
                
        b=PmwTtkButtonBox.PmwTtkButtonBox(pstatResults,orient='horizontal',hull_background='#d4d0c8')
        b.add('Save Calibration File',command=self.saveCalibFile,style='NAVY.TButton',width=25) 
        b.pack(side=tkinter.TOP,padx=5,pady=10)    

        self.regplot=MyGraph.MyGraph(pstatPlot,whsize=(5,3),padx=5,pady=5,graphpos=[[.15,.1],[.9,.9]])
        
        
        #if sys.platform!='darwin':
        #    plotnb.setnaturalsize()



    def kill(self,*event):
        self.exist=0
        self.partstatROIflag=0

        if sys.platform=='darwin':
            for w in self.killwidlist:
                w.destroy()
        self.win.destroy()

    def decodeCHANmask(self,roi,power,color=1,null=0):
        if null:
            return np.np.zeros(roi.shape,dtype=np.int32)
        roi=np.asarray(roi,dtype=np.int32)
        power=int(power)
        if power==0: return np.where(roi==0,color,0)
        else: return np.where(roi&power>0,color,0)

    def makeROImask(self,roi,data,color=1):
        data=np.array(data,dtype=np.float32)
        inp=data#cv.fromarray(data)
        inp8 = inp.astype(np.uint8)
        #cv.Convert(inp,inp8)
        if not self.partStatuseWater:
            #cv.drawContours(inp8,roi,(color,color,color),(color,color,color),0,cv.FILLED)
            cv.drawContours(inp8,[roi],-1,(color,color,color),-1)
            return inp8
        else:
            cv.drawContours(inp8,[roi],0,(color,color,color),-1)
            return inp8
        
    def selectAll(self):
        for r in self.partroilist:
            r.isSelected=True
        self.updateMultiMass()
    
    def selectNone(self):
        for r in self.partroilist:
            r.isSelected=False
        self.updateMultiMass()

    def selectInvert(self):
        for r in self.partroilist:
            r.isSelected=not r.isSelected
        self.updateMultiMass()

    def toggleSelect(self,arg):
        for r in arg:
            self.partroilist[r].isSelected = not self.partroilist[r].isSelected
            
    def updateMultiMass(self,*args):
        #kill all?
        self.pstatlist.clear()        
        #add new
        basecol=['Sel','File','ROI#', 'StdLink','Npix', 'Xcent', 'Ycent']
        baseexp=[0,1,2,3,4,5,6]
        v=4
        doCor=False
        for c in self.partstatsel.getcurselection():
            basecol.append(c)
            baseexp.append(v)
            v+=1
            
       
        print(tuple(basecol))
        self.pstatlist.setColNames(tuple(basecol))
        self.pstatlist.setDefaultWA()
        
        #add new values
        icounter=1
        for r in self.partroilist:
            buf=self.ps.dataFileBuffer[r.buffer]
            xcds=buf['data'].data.get(1)  # [:,:,1]
            ycds=buf['data'].data.get(0)  # [:,:,0]
            print(icounter)
            icounter+=1
            #make a mask
            if self.partStatuseMask: mask=r.mask
            else: mask=np.asarray(self.makeROImask(r.mask,np.zeros(buf['data'].data.get(0).shape)))
            l=self.pstatdict[r.buffer+"*"+r.label]
            d=None
            if 'area' in l: area=l['area']
            else:
                d=MomentMathClass.MomentClass(xcds,ycds,mask)
                area=d.A
                l['area']=area           
                ##area=abs(cv.ContourArea(r[2]))
                ##l['area']=area
            if ('xcenter' in l and 'ycenter' in l):
                xc=l['xcenter']
                yc=l['ycenter']
            else:
                if d is None: d=MomentMathClass.MomentClass(xcds,ycds,mask)
                xc=d.medx
                yc=d.medy        
                l['xcenter']=xc
                l['ycenter']=yc
            if r.isSelected:
                seltxt="X"
            else:
                seltxt=" "
            if r.link is not None:
                linktxt=r.link
            else:
                linktxt=" "
            #TRACY REQUEST, previous value clip 5
            arglist=[seltxt,r.buffer,r.label,linktxt,area,globalfuncs.valueclip_d(xc,0),globalfuncs.valueclip_d(yc,0)]
            for c in self.partstatsel.getcurselection():
                listname=c+'&&'+self.partseltype.getvalue()
                if listname in l:
                    ival=l[listname]
                    sval=l[c+'&&SD']
                else:
                    datind=buf['data'].labels.index(c)+2
                    xv=np.ravel(buf['data'].data.get(datind))#[:,:,datind])
                    #and deadtimes...
                    #nodtx=0
                    #if self.ps.datachan.getvalue()[0] in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodtx=1
                    #if self.dodt.get()==1 and not nodtx:
                    #    #DT: corFF=FF*exp(tau*1e-6*ICR)
                    #    icr=np.ravel(buf['data'].data.get(self.DTICRchanval))
                    #    dtcor=np.exp(float(self.deadtimevalue.getvalue())*1e-6*icr)
                    #    xv=xv*dtcor
                    pic=np.reshape(xv,np.shape(buf['data'].data.get(0)))#[:,:,0]))
                    xc=buf['data'].data.get(1)#[:,:,1]
                    yc=buf['data'].data.get(0)#[:,:,0]
                    d=MomentMathClass.MomentClass(xc,yc,pic,mask=mask,all=2)
                    #check for which value to report
                    ival=''
                    if self.partseltype.getvalue()=='Sum':
                        ival=d.sum
                    if self.partseltype.getvalue()=='Mean':
                        ival=d.avg
                    if self.partseltype.getvalue()=='Median':
                        ival=d.median
                    if self.partseltype.getvalue()=='Mode':
                        ival=d.mode[0][0]
                    sval=d.stddev
                    l[c+'&&SD']=sval
                    l[c+'&&Sum']=d.sum
                    l[c+'&&Mean']=d.avg
                    l[c+'&&Median']=d.median
                    l[c+'&&Mode']=d.mode[0][0]
                    #l[listname]=ival
                    #for box plots?
                    if c+'&&DATA' not in l:
                        l[c+'&&DATA']=np.ravel(d.i)
                arglist.append(globalfuncs.valueclip_d(ival,5))

                    
            newitem=self.pstatlist.insert(list(arglist))
            if l!=self.pstatdict[r.buffer+"*"+r.label]:
                self.pstatdict[r.buffer+"*"+r.label]=l
        #self.makePartBoxPlot()

    def partSelectROIList(self,*args):
        x=self.win.winfo_pointerx()
        y=self.win.winfo_rootx()
        z=self.win.winfo_vrootx()
        #print (x,y,z)
        offs = self.leftframe.winfo_width()
        up=False
        #if sys.platform=='darwin':
        #    offs=224
        #else:
        #    offs=160
        cn=self.pstatlist.identify_column(x-y-offs)
        if len(cn)>1:
            if cn[0]=='#' and cn[1:]=='1':
                self.toggleSelect(args[0])
                up=True
        #check for switch
        if self.pstatindview.getvalue()=='Show None':
            self.partstatROIflag=0
        if self.pstatindview.getvalue()=='Show Current':
            self.partstatROIflag=1            
        if self.pstatindview.getvalue()=='Show All':
            self.partstatROIflag=2
        self.partShowROIOption()
        if up: self.updateMultiMass()

    def partShowROIOption(self):
        if self.ps.datachan.get()==():
            return
        if len(self.pstatlist.curselection())<1: return
        if self.partstatROIflag==0:
            #self.ps.domapimage()
            return
        globalfuncs.setstatus(self.ps.status,"DISPLAYING...")
        datind=self.mapdata.labels.index(self.ps.datachan.getvalue()[0])+2
        datlab=self.mapdata.labels[datind-2]

        pic=self.mapdata.data.get(datind)[::-1,:]#[::-1,:,datind]
        mi=self.mapdata.mapindex[::-1,:]
        picmsk=[]
        nodt=0
        #if self.ps.datachan.getvalue()[0] in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodt=1
        #if self.dodt.get()==1 and not nodt:
        #    #DT: corFF=FF*exp(tau*1e-6*ICR)
        #    icr=self.mapdata.data.get(self.DTICRchanval)[::-1,:]#[::-1,:,self.DTICRchanval]
        #    dtcor=np.exp(float(self.deadtimevalue.getvalue())*1e-6*icr)
        #    pic=pic*dtcor
        #i0 corr?
        #if self.doI0c.get()==1:
        #    #geti0
        #    iind=self.mapdata.labels.index(self.i0chan.getvalue())+2
        #    i0dat=self.mapdata.data.get(iind)[::-1,:]#[::-1,:,iind]
        #    #divide
        #    (xlen,ylen)=self.mapdata.data.shape[:2]
        #    newdata=np.zeros((xlen,ylen),dtype=np.float32)
        #    for i in range(xlen):
        #        for j in range(ylen):
        #            if i0dat[i,j]!=0:
        #                newdata[i,j]=float(pic[i,j])/float(i0dat[i,j])
        #    pic=newdata

        #adjust ROI
        pic=pic[::-1,:]        
        print('doingroi')
        data=np.array(pic,dtype=np.float32)
        inp8=data#cv.fromarray(data)
        contourlist=[]
        for r in self.partroilist:
            if r.buffer!=self.ps.activeFileBuffer:
                continue
            if self.partStatuseMask: test=r.pindex
            else: test=r.index
            if self.partstatROIflag==1:
                if test==self.pstatlist.curselection()[0]+1:                
                    contourlist.append(r.mask)
            else:
                contourlist.append(r.mask)
            ##print 'contourlist made'
            ##print contourlist,self.pstatlist.listbox.curselection()[0]
        for c in contourlist:
            if len(contourlist)==1: color=190./255.*max(np.ravel(pic))
            else: color=random.randint(0,255)/255.*max(np.ravel(pic))
            if self.partStatuseMask:
                pic=np.where(c>0,color,pic)
            elif not self.partStatuseWater:
                #cv.DrawContours(inp8,c,cv.RGB(color,color,color),cv.RGB(color,color,color),0,cv.CV_FILLED)
                cv.drawContours(inp8,[c], -1, (color,color,color),-1)
                print("drawing contours in not use water")
            else:
                cv.drawContours(inp8,[c],0,(color,color,color),-1)
        print('roi added')
        if not self.partStatuseMask:
            pic=np.asarray(inp8)

        pic=pic[::-1,:]
        self.ps.maindisp.placeData(np.transpose(pic),np.transpose(mi),self.ps.status,xax=self.mapdata.xvals,yax=self.mapdata.yvals,domask=self.ps.usemaskinimage,mask=picmsk,datlab=datlab)
        self.ps.showmap()
        
    def linkSelectedROI(self):
        #check for selections....
        someok=False
        for r in self.partroilist:
            if r.isSelected: someok=True
        if not someok:
            print ('canceled')
            globalfuncs.setstatus(self.ps.status,"No ROIs selected...")    
            return
        #ask for json file of calibrants
        infile=globalfuncs.ask_for_file([("JSON Calibration files","*.json"),("all files","*")],self.ps.filedir.get(),multi=False)
        if infile == '' or infile is None:
            print ('canceled')
            globalfuncs.setstatus(self.ps.status,"No calibration file defined...")
            return        
        #load file
        self.db = ConcentrationStandardClass.ConcentrationStandardData('')
        self.db.LoadFromJSON(infile)       
        self.resultobj.standardfile=infile
        
        #create list of items in json  -- this is just db["Results"]
        names=[]
        for item in self.db.data["Results"]:
            names.append(item["Properties"]["Name"])
        #create match-widget to match selected ROIs to item list
        self.MMlinkROIs(names)

        
    def MMlinkROIs(self,inputItems):
        self.MMlinkdialog=Pmw.Dialog(self.imgwin,title='Correlate ROIs',buttons=('OK','Cancel'),defaultbutton='OK',
                                      command=self.MMlinkdone)
        inter=self.MMlinkdialog.interior()
        self.MMlinkresult={}
        items=['None']
        items.extend(inputItems)
        for q in self.partroilist:
            if not q.isSelected:
                continue
            cb=Pmw.ComboBox(inter,label_text=q.label+" : "+q.buffer,labelpos='w',history=0,scrolledlist_items=items,dropdown=1)
            cb.pack(side=tkinter.TOP,padx=5,pady=5)
            cb.selectitem('None',setentry=1)
            self.MMlinkresult[q]=cb
        Pmw.alignlabels(list(self.MMlinkresult.values()))
        self.MMlinkdialog.show()

    def MMlinkdone(self,result):
        if result=='Cancel':
            print('Load cancelled')
            self.MMlinkdialog.withdraw()
            return
        #enter values in table
        for n in list(self.MMlinkresult.keys()):
            if self.MMlinkresult[n].get()=='None':
                n.link=None
            else:
                n.link=self.MMlinkresult[n].get()
        self.MMlinkdialog.withdraw()   
        self.updateMultiMass()    

    def validateLinks(self):
        lenok=False
        for q in self.partroilist:
            if not q.isSelected:
                continue
            lenok=True
            if q.link is None: 
                print ('print need links')
                return False
        if not lenok: 
            print ('need ROI selections')
            return False
        return True
    
    def validateCalib(self):
        if len(self.calibGroupDict.keys())==0: return False
        for item in self.calibGroupDict.values():
            for w in item.values():
                if not w.isValid(): return False
        return True
            

    def setupSingle(self):
        if not self.validateLinks():
            print ('Please select and link all ROIs')
            return
        self.calibType='single'
        #setup button
        #self.calbut.configure(command = self.calculateSingle)
        self.calbut.configure(text = 'Calibrate SINGLE')
        self.calbut.configure(style = 'LGREEN.TButton')
        self.updateCalibGroups()
        
    def setupMulti(self):
        if not self.validateLinks():
            print ('Please select and link all ROIs')
            return
        self.calibType='multi'
        #setup button
        #self.calbut.configure(command = self.calculateMulti)
        self.calbut.configure(text = 'Calibrate MULTI')
        self.calbut.configure(style = 'GREEN.TButton')
        self.updateCalibGroups()

    def clearCalibGroups(self):
        for i in self.calibGroupDict.keys():
            i.destroy()
        self.calibGroupDict={}

    def updateCalibGroups(self):
        self.clearCalibGroups()
        for q in self.partroilist:
            if not q.isSelected:
                continue
            #make group
            gname = q.link + ' :: '+q.label + " : "+q.buffer
            grp=Pmw.Group(self.calibFrame.interior(),tag_text=gname,hull_background='#d4d0c8',tag_background='#d4d0c8',ring_background='#d4d0c8')
            grp.interior().configure(background='#d4d0c8')
            grp.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')            
            
            widlist={}
            #list of elements in the item -- element, conc, channel, "value in that ROI"
            #find the item...
            for it in self.db.data['Results']:
                if it['Properties']['Name']!=q.link: continue
                for e in it["Contents"].keys():
                    #print (it["Contents"][e]["Units"])
                    w=calibrationWidget(grp.interior(),e,it["Contents"][e]["Value"],it["Contents"][e]["Units"],self.normlist,self.displayCallback,q)
                    widlist[e]=w
                
                self.calibGroupDict[grp]=widlist

    def suggestChannelMatch(self):
        for item in self.calibGroupDict.values():
            for e,w in item.items():
                if w.isActive():
                    for pe in w.selectlist:
                        newpe = ''.join((x for x in pe if not x.isdigit()))
                        if pe.startswith(e) or newpe.startswith(e):
                            w.channel.selectitem(pe)
                            w.prepcb()
                        
            
    def calculate(self):
        #validate?
        if not self.validateCalib():
            print ('Please match channels to all elements')
            return       
        self.elementcaldict=sortedcontainers.SortedDict(mucal.name_z)
        self.resultobj.clear()
        self.resultobj.normalize = self.normchannel.get()
        for item in self.calibGroupDict.values():
            for e,w in item.items():
                #print (e,w.units)
                if w.isActive():
                    counts=[float(w.valcon)]
                    norm=[float(w.normcon)]
                    conc=[float(w.conc)]
                    d={}
                    d['counts']=counts
                    d['conc']=conc
                    d['norm']=norm
                    d['channel']=[w.channel.get()]
                    d['units']=[w.units]
                    if e not in self.elementcaldict:
                        self.elementcaldict[e]=d
                    else:
                        self.elementcaldict[e]['counts'].extend(counts)
                        self.elementcaldict[e]['conc'].extend(conc)
                        self.elementcaldict[e]['norm'].extend(norm)
                        self.elementcaldict[e]['channel'].extend(d['channel'])
                        self.elementcaldict[e]['units'].extend(d['units'])
        if self.calibType == 'single':
            #each roi is unique with its elements...  calibrate 1 point each sample
            for e,d in self.elementcaldict.items():
                for i in range(len(d['counts'])):
                    fitwid = FitCalibClass(e,[d['conc'][i]],[d['counts'][i]],[d['norm'][i]],[d['units'][i]],[d['channel'][i]])
                    self.resultobj.listforresults.append(fitwid)                    
                        
        if self.calibType == 'multi':
            #all rois are related... calibrate elements across ROIs
            for e,d in self.elementcaldict.items():
                fitwid = FitCalibClass(e,d['conc'],d['counts'],d['norm'],d['units'],d['channel'])
                self.resultobj.listforresults.append(fitwid)    
        
        
        self.updateResultList()
        
      
    def saveCalibFile(self):
        
        #get file name to save
        fn="calibration_data.qpm"
        fn=globalfuncs.ask_save_file(fn,self.ps.filedir.get())
        if fn=='':
            print('Save cancelled')
            globalfuncs.setstatus(self.ps.status,'Save cancelled')
            return   
        if os.path.splitext(fn)[1]!='.qpm':
            fn=fn+".qpm"
        
        self.resultobj.saveFile(fn)

    def resulttoggle(self,*args):

        x=self.win.winfo_pointerx()
        y=self.win.winfo_rootx()
        z=self.win.winfo_vrootx()
        print (x,y,z)
        up=False
        offs = self.leftframe.winfo_width()#+self.rightframe.winfo_width()    #NEED TO THINK ABOUT SCROLLING???
        cn=self.resultlist.identify_column(x
            -y-offs)

        if len(cn)>1:
            if cn[0]=='#' and cn[1:]=='1':
                #do toggle #self.toggleSelect(args[0])
                for g in args:
                    #print (g)
                    if len(g)==0: continue
                    self.resultobj.listforresults[g[0]].selected=not self.resultobj.listforresults[g[0]].selected
                up=True   
            else:
                #update plot
                self.regplot.cleargraphs()
                #plot
                xvd=self.resultobj.listforresults[args[0][0]].fvx
                yvd=self.resultobj.listforresults[args[0][0]].dvy
                yvf=self.resultobj.listforresults[args[0][0]].fvy
                print("updating plot")
                print("xvd: ", xvd)
                print("yvd: ", yvd)
                print("yvf: ", yvf)
                self.regplot.plot(tuple(xvd),tuple(yvf), color='green', text='F')
                self.regplot.scatterplot(tuple(xvd),tuple(yvd),symbol="o",color='red')
                print("plotting")
                self.regplot.draw()

                print("sort test")
                print("xvd: ", xvd.sort())
                print("yvd: ", yvd.sort())
                print("yvf: ", yvf.sort())
                  
        if up:
            #call update
            self.updateResultList()
    
    def updateResultList(self,*args):
        self.resultlist.clear()
        #iterate....
        for fw in self.resultobj.listforresults:
            #Sel','Element','Slope', 'Intercept','GOF-R2'
            if fw.selected is True:
                st='X'
            else:
                st=' '
            #NOT ROUNDED
            #arglist=[st,fw.el,fw.slope,fw.intc,fw.gof]
            #ROUNDED PER TRACY REQUEST
            arglist=[st,fw.el,globalfuncs.valueclip_d(fw.slope, 5),fw.intc,globalfuncs.valueclip_d(fw.gof, 8)]
            
            
            newitem = self.resultlist.insert(list(arglist))


    def checkNorms(self,*arg):
        for item in self.calibGroupDict.values():
            for e,w in item.items():
                if w.isActive():
                    w.prepcb()

    def displayCallback(self,w):  
        if w.channel.get()=='None':
            w.valcon=None
            w.chanvalue.configure(text="Counts: ")
            w.normcon=1.0
        else:
            l=self.pstatdict[w.qitem.buffer+"*"+w.qitem.label]
            if self.partseltype.getvalue()=='Sum':
                area = 1.0 #l['area']
            else:
                area = 1.0
            w.normcon=area
            listname = w.channel.get()+'&&'+self.partseltype.getvalue()
            if listname in l:
                nv = l[listname]
            else:
                buf=self.ps.dataFileBuffer[w.qitem.buffer]
                xc=buf['data'].data.get(1)  
                yc=buf['data'].data.get(0)
                datind=buf['data'].labels.index(w.channel.get())+2
                xv=np.ravel(buf['data'].data.get(datind))
                pic=np.reshape(xv,np.shape(buf['data'].data.get(0)))
                d=MomentMathClass.MomentClass(xc,yc,pic,mask=w.qitem.mask,all=2)
                l[w.channel.get()+'&&SD']=d.stddev
                l[w.channel.get()+'&&Sum']=d.sum
                l[w.channel.get()+'&&Mean']=d.avg
                l[w.channel.get()+'&&Median']=d.median
                l[w.channel.get()+'&&Mode']=d.mode[0][0]
                nv = l[listname]                
            w.valcon = nv
            #JOY ROUNDED
            w.chanvalue.configure(text="Counts: "+globalfuncs.valueclip_d(nv,0))
            #PREVIOUS
            #w.chanvalue.configure(text="Counts: "+globalfuncs.valueclip_d(nv,4))

            #check for norm channel too:
            if self.normchannel.get() != 'None':
                normbase = w.channel.get()+'/' +self.normchannel.get()
                normname = normbase +'&&'+self.partseltype.getvalue()
                if normname in l:
                    normv = l[normname]
                else:
                    buf=self.ps.dataFileBuffer[w.qitem.buffer]
                    xc=buf['data'].data.get(1)  
                    yc=buf['data'].data.get(0)
                    datind=buf['data'].labels.index(w.channel.get())+2
                    ndatind=buf['data'].labels.index(self.normchannel.get())+2
                    ratdat = np.divide(buf['data'].data.get(datind),buf['data'].data.get(ndatind),out=np.zeros_like(buf['data'].data.get(ndatind)),where=buf['data'].data.get(ndatind)>0)
                    xv=np.ravel(ratdat)
                    pic=np.reshape(xv,np.shape(buf['data'].data.get(0)))
                    d=MomentMathClass.MomentClass(xc,yc,pic,mask=w.qitem.mask,all=2)
                    l[normbase+'&&SD']=d.stddev
                    l[normbase+'&&Sum']=d.sum
                    l[normbase+'&&Mean']=d.avg
                    l[normbase+'&&Median']=d.median
                    l[normbase+'&&Mode']=d.mode[0][0]
                    normv = l[normname]   
                w.valcon=normv
                #w.normcon=1.0
                w.chanvalue.configure(fg='blue')
            else:
                #w.normcon=1.0
                w.chanvalue.configure(fg='black')
            

class FitCalibClass:
    def __init__(self,el,conc,counts,norm,units,channels,fit=True):
        self.el=el
        self.conc=np.array(conc)
        self.counts=np.array(counts)
        self.norm=np.array(norm)
        self.channels=channels
        self.units=units[0]
        
        self.selected=True 
        
        self.slope=None
        self.intc=None
        self.gof=None
        
        print (el,conc,counts,norm)
        
        if fit: self.fit()
        
    def fit(self):
        if len(self.conc)==1:
            self.slope = float(self.conc[0]/(self.counts[0]/self.norm[0])) #float(self.norm[0]*self.conc[0]/self.counts[0])
            self.intc=0.0
            self.gof=1.0
            self.fvx=[0,self.counts[0]]   #[0,self.counts[0]/self.norm[0]]
            self.fvy=[0,self.conc[0]/self.norm[0]]
            self.dvy=[0,self.conc[0]/self.norm[0]]
        else:
            #do regressions
            ##model = np.polyfit(self.counts,self.conc/self.norm,1) #np.polyfit(self.counts/self.norm,self.conc,1)
            ##self.slope=model[0]
            ##self.intc=model[1]
            s,_,_,_ = np.linalg.lstsq(self.counts[:,np.newaxis],self.conc/self.norm,rcond=None)
            self.slope=s[0]
            self.intc=0
            model=[self.slope,self.intc]
            
            
            predict = np.poly1d(model)
            self.gof = r2_score(self.conc/self.norm,predict(self.counts)) #r2_score(self.conc,predict(self.counts/self.norm))
            self.fvx = self.counts #self.counts/self.norm
            self.fvy = predict(self.fvx)
            self.dvy = self.conc/self.norm
            #print (self.gof)

class calibrationWidget:
    def __init__(self, master, element, conc, units, selectlist, callback,qitem):
        self.master=master
        self.element=element
        self.conc=conc
        self.units=units
        self.selectlist=selectlist
        self.cb=callback
        self.qitem=qitem
        self.valcon=None
        self.normcon=1.0
        
        f=tkinter.Frame(master,background='#d4d0c8')
        f.pack(side=tkinter.TOP,padx=2,pady=2)
        self.rootf=f

        #Calc Type
        self.useme=Pmw.RadioSelect(f,labelpos=tkinter.W,label_text='',command=tkinter.DISABLED,buttontype='checkbutton',hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        self.useme.add('Use',background='#d4d0c8')        

        if mucal.name_z(element)>9:
            self.useme.invoke('Use')

        #self.namelab=tkinter.Label(f,text='Name: '+element,width=10,background='#d4d0c8')
        self.namelab=tkinter.Label(f,text=element,width=5,background='#d4d0c8')        
        self.value=tkinter.Label(f,text='Value: '+str(conc),width=13,background='#d4d0c8')
        #self.channel=Pmw.ComboBox(f,history=0,selectioncommand=self.prepcb,hull_background='#d4d0c8',labelpos='w',label_text="Channel:  ",label_background='#d4d0c8')
        self.channel=Pmw.ComboBox(f,history=0,selectioncommand=self.prepcb,hull_background='#d4d0c8',labelpos='w',label_background='#d4d0c8')
        self.channel.setlist(self.selectlist)
        self.channel.selectitem('None')    

        self.chanvalue=tkinter.Label(f,text='Counts: ',width=13,background='#d4d0c8')

        self.useme.pack(side=tkinter.LEFT,padx=0,pady=2)        
        self.namelab.pack(side=tkinter.LEFT,padx=0,pady=2)
        self.value.pack(side=tkinter.LEFT,padx=1,pady=2)
        self.channel.pack(side=tkinter.LEFT,padx=0,pady=2)  
        self.chanvalue.pack(side=tkinter.LEFT,padx=0,pady=2)  
        
    def prepcb(self,*arg):
        self.cb(self)
        
    def isValid(self):
        if len( self.useme.getcurselection())==0: return True
        if self.channel.get()=='None': return False
        if self.valcon is None: return False
        return True

    def isActive(self):
        if len( self.useme.getcurselection())==0: return False
        return True
        
class PartROIlistItem:
    def __init__(self, params=None):
        self.index=None
        self.label=None
        self.mask=None
        self.pindex=None
        self.buffer=None
        self.isSelected=False
        self.link=None
        
        if params is not None:
            self.setAll(params)
        
    def setAll(self,params):
        self.index=params[0]
        self.label=params[1]
        self.mask=params[2]
        self.pindex=params[3]
        self.buffer=params[4]
        self.isSelected=params[5]
        self.link=params[6]

class CalibResultObject:
    def __init__(self):
        self.listforresults=[]
        self.normalize=None
        self.standardfile=None
        self.chlist=None
        self.ellist=None
        self.chdict={}


    def clear(self):
        self.listforresults=[]
        self.chlist=None
        self.ellist=None
        self.chdict={}

    def loadFile(self,fn):
        fid = open(fn,'r')
        lines = fid.readlines()
        fid.close()
        if lines[0]!='SMAK QUANT V3.0\n':
            print('Invalid parameter file!')
            return     
        self.standardfile = lines[1].split('=')[1]
        self.normalize = lines[2].split('=')[1]
        readok=False
        self.chlist=[]
        self.ellist=[]
        for l in lines:
            if len(l)==0: continue
            if l[0]=='!':
                readok=True
                continue
            if not readok: continue
            
            ifs = l.split('\t')
            el=ifs[0]
            channels=[ifs[1]]
            units = ifs[5]
            fw = FitCalibClass(el,[0],[0],[0],[units],channels,fit=False)
            fw.slope = float(ifs[2])
            fw.intc = float(ifs[3])
            fw.gof = float(ifs[4])
        
            self.listforresults.append(fw)
            self.chlist.append(channels)
            self.ellist.append(el)
            self.chdict[el]=fw
            

    def saveFile(self,fn):
        fid = open(fn,'w')
        fid.write("SMAK QUANT V3.0\n")
        fid.write("# STANDARD FILE = "+str(self.standardfile)+"\n")
        if self.normalize is None:
            nct="None"
        else:
            nct=self.normalize
        fid.write("# NORM CHAN = "+nct+"\n")
        fid.write("# DATABLOCK\n")
        fid.write("! Element\tChannel\tSlope\tIntercept\tGOF\tUnits\n")
        for fw in self.listforresults:
            if fw.selected is not True:
                continue
            txt=str(fw.el)+'\t'+str(fw.channels[0])+'\t'+str(fw.slope)+'\t'+str(fw.intc)+'\t'+str(fw.gof)+'\t'+str(fw.units)
            fid.write(txt+"\n")
        fid.close()
        
    
""" File format:

SMAK QUANT V3.0
# STANDARD FILE = <foo.json>
# NORM CHAN = <i0> or None
! DATABLOCK
! <<columns -- Element, Channel, Slope, Intercept, GOF, Units>>


"""    


        
        
        
        
        
        
        
        