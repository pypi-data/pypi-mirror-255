#standard
import random
import sys
import math
import tkinter
import itertools

#third party
import Pmw
import numpy as np
import cv2 as cv
from scipy import ndimage, stats
from scipy.optimize import curve_fit, minimize
from skimage.feature import peak_local_max
from skimage.segmentation import watershed


#local
import globalfuncs
import histclass
from MasterClass import MasterClass
import MomentMathClass
import MultiFitObj
import MyGraph
import PmwTtkButtonBox
import PmwTtkNoteBook
import PmwTtkRadioSelect
import ScrollTree


class dummy():
    def __init__(self):
        self.elp=1
        
class ParticleStatisticsWindowParams():
    def __init__(self, useMask, useWater, status, isStatCalcMultiFile, activeFileBuffer, dataFileBuffer, datachan, partROIThresh, partWaterThresh, nullMaskCalc, dodt, deadtimevalue, DTICRchanval, root, doI0c, domapimage,maindisp, usemaskinimage, showmap, filedir, addchannel, SAMmasks=None):
        self.useMask = useMask
        self.status = status
        self.useWater = useWater
        self.isStatCalcMultiFile = isStatCalcMultiFile
        self.activeFileBuffer = activeFileBuffer
        self.dataFileBuffer = dataFileBuffer
        self.datachan = datachan
        self.partROIThresh = partROIThresh
        self.nullMaskCalc = nullMaskCalc
        self.dodt = dodt
        self.deadtimevalue = deadtimevalue
        self.DTICRchanval = DTICRchanval
        self.root = root
        self.doI0c = doI0c
        self.domapimage = domapimage
        self.maindisp = maindisp
        self.usemaskinimage = usemaskinimage
        self.showmap = showmap
        self.SAMmasks = SAMmasks
        self.filedir = filedir
        self.partWaterThresh = partWaterThresh
        self.addchannel = addchannel

class ParticleStatisticsWindow(MasterClass):
    def _params(self):
        self.partStatuseMask=self.ps.useMask

    def initcalc(self):
        self.partStatuseWater=self.ps.useWater
        self.partstatROIflag=0
        #check for multi and same channels in all files?
        bufs=[]
        commonchanlist=list(self.mapdata.labels)
        if self.ps.isStatCalcMultiFile.get() and self.ps.SAMmasks is None:
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

        #print (self.partStatuseMask,self.ps.SAMmasks,self.ps.useWater)

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
                    return

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
            if self.ps.useWater==0:
                for bufn in bufs:
                    #JOY lots of changes to cv2/obsolete functionality need to check that this does what it should
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
            else:
                for bufn in bufs:
                    globalfuncs.setstatus(self.ps.status,"Calculating watershed segmentation from "+self.ps.datachan.getvalue()[0]+" in "+bufn)
                    buf=self.ps.dataFileBuffer[bufn]
                    datind=buf['data'].labels.index(self.ps.datachan.getvalue()[0])+2
                    data=buf['data'].data.get(datind)#[:,:,datind]
                    data=np.array(data,dtype=np.int64)

                    D=ndimage.distance_transform_edt(data)
                    #localMax=peak_local_max(D,indices=False,min_distance=int(self.ps.partWaterThresh),labels=data)
                    localMax=peak_local_max(D,min_distance=int(self.ps.partWaterThresh),footprint=np.ones((3,3)),labels=data)
                    wmask=np.zeros(D.shape,dtype=bool)
                    wmask[tuple(localMax.T)]=True
                    markers=ndimage.label(wmask)[0]
                    labels=watershed(-D,markers,mask=data)
                    print("found: ",len(np.unique(labels))-1)

                    n=0
                    for label in np.unique(labels):
                        if label==0:
                            continue
                        mask=np.zeros(data.shape,dtype="uint8")
                        mask[labels==label]=255
                        inp=mask #cv.fromarray(mask)
                        #inp8=cv.CreateMat(inp.rows,inp.cols,cv.CV_8UC1)
                        inp8=inp.astype(np.uint8)

                        #cv.Convert(inp,inp8)
                        #storage=cv.CreateMemStorage()
                        #f=cv.FindContours(inp8,storage,cv.CV_RETR_EXTERNAL,cv.CV_CHAIN_APPROX_SIMPLE)
                        f=cv.findContours(inp8,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)[0][0]

                        #print (f.shape)
                        if f.shape[0] <3: continue

                        mask=np.asarray(self.makeROImask(f,np.zeros(buf['data'].data.get(0).shape)))
                        s=sum(np.ravel(mask))
                        #print (f.shape,s)
                        if s>=self.ps.partROIThresh:
                            n+=1
                            #print(n)
                            item = PartROIlistItem([n,'ROI '+str(n),f,n,bufn,False,None])
                            self.partroilist.append(item)
                    print (len(self.partroilist))
        globalfuncs.setstatus(self.ps.status,"Calculation complete")  
        
        self.partStatuseMask=self.ps.useMask
        self.partStatuseWater=self.ps.useWater
        self.partstatROIflag=0
        
        #print (self.partroilist,self.pstatdict)
        return commonchanlist

    def _buildpstatlist(self):
        self.pstatlistlines={}

        i=1
        for r in self.partroilist:
            buf=self.ps.dataFileBuffer[r.buffer]
            xcds=buf['data'].data.get(0)  # [:,:,1]
            ycds=buf['data'].data.get(1)  # [:,:,0]

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
            newitem=self.pstatlist.insert((r.buffer,r.label,area,globalfuncs.valueclip_d(xc,5),globalfuncs.valueclip_d(yc,5)))
            l={}
            l['area']=area
            l['xcenter']=xc
            l['ycenter']=yc
            self.pstatdict[r.buffer+"*"+r.label]=l
            self.pstatlistlines[r.label]=newitem
            
            if i%10==0: print (i)
            i+=1

    def _create(self):
        #parameters 
        self._params()
        commonchanlist=self.initcalc()

        #now create dialog...
        self.win=Pmw.MegaToplevel(self.imgwin)
        self.win.title('Particle Statistics')
        self.win.userdeletefunc(func=self.kill)
        
        #self.win=Pmw.Dialog(self.imgwin,title="Particle Statistics",buttons=("Done",),defaultbutton='Done',
        #                              command=self.kill)
        hm=self.win.interior()
        hm.configure(background='#d4d0c8')
        
        if sys.platform=='darwin':
            #mac specific layout as notebook has weird behavior?
 
            h2=Pmw.ScrolledFrame(hm,usehullsize=1,vertflex='fixed',horizflex='fixed',
                                 hscrollmode='static',vscrollmode='static',
                                 hull_width=1200,hull_height=1100)
            h2.interior().configure(background='#d4d0c8')
            h2.pack(side=tkinter.TOP,pady=2)
            h=h2.interior()  
        else:
            h=hm
        
        
        lf=tkinter.Frame(h,background='#d4d0c8')
        lf.pack(side=tkinter.LEFT,fill='both')
        #data selections
        self.partstatsel=Pmw.ScrolledListBox(lf,labelpos='n',label_text='Select Channel',items=commonchanlist,listbox_selectmode=tkinter.EXTENDED,
                                              listbox_exportselection=tkinter.FALSE,selectioncommand=self.updatePartStat,listbox_height=15,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.partstatsel.pack(side=tkinter.TOP,padx=4,pady=5,fill='both')
        self.partseltype=PmwTtkRadioSelect.PmwTtkRadioSelect(lf,buttontype='button',orient='vertical',command=self.updatePartStat,selectmode='single',labelpos='n',label_text='Analysis Type',hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        for text in ('Sum','Mean','Median','Mode'):
            self.partseltype.add(text)
        self.partseltype.setvalue('Sum')
        self.partseltype.pack(side=tkinter.TOP,padx=3,pady=3)
        self.partselstdd=PmwTtkRadioSelect.PmwTtkRadioSelect(lf,buttontype='button',orient='vertical',command=self.updatePartStat,selectmode='single',labelpos='n',label_text='Show StdDev',hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        for text in ('On','Off'):
            self.partselstdd.add(text)
        self.partselstdd.setvalue('Off')
        self.partselstdd.pack(side=tkinter.TOP,padx=3,pady=3)        
        self.partselcorr=PmwTtkRadioSelect.PmwTtkRadioSelect(lf,buttontype='button',orient='vertical',command=self.updatePartStat,selectmode='single',labelpos='n',label_text='Calc Correl.',hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        for text in ('On','Rev','Off'):
            self.partselcorr.add(text)
        self.partselcorr.setvalue('Off')
        self.partselcorr.pack(side=tkinter.TOP,padx=3,pady=3) 
        self.partmorphstat=PmwTtkRadioSelect.PmwTtkRadioSelect(lf,buttontype='button',orient='vertical',command=self.updatePartStat,selectmode='single',labelpos='n',label_text='Calc Morph.',hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        for text in ('On','Off'):
            self.partmorphstat.add(text)
        self.partmorphstat.setvalue('Off')
        self.partmorphstat.pack(side=tkinter.TOP,padx=3,pady=3) 

        #notebook
        rf=tkinter.Frame(h,background='#d4d0c8')
        rf.pack(side=tkinter.LEFT,fill='both',expand=1)
        
        if sys.platform=='darwin':
            #mac specific layout as notebook has weird behavior?
 
            #hh=Pmw.ScrolledFrame(rf,usehullsize=1,vertflex='fixed',horizflex='fixed',
            #                     hscrollmode='static',vscrollmode='static',
            #                     hull_width=1200,hull_height=1100)
            #hh.interior().configure(background='#d4d0c8')
            #hh.pack(side=tkinter.TOP,pady=2)
            #ii=hh.interior()    
            ii=rf
            
            topCon = tkinter.Frame(ii, background='#d4d0c8')
            topCon.pack(side=tkinter.TOP,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            pstatInd = tkinter.Frame(topCon, relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
            pstatInd.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            pstatBox = tkinter.Frame(topCon, relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
            pstatBox.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            
            botCon = tkinter.Frame(ii, background='#d4d0c8')
            botCon.pack(side=tkinter.TOP,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            pstatDist = tkinter.Frame(botCon, relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
            pstatDist.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)
            pstatAnova = tkinter.Frame(botCon, relief=tkinter.SUNKEN,bd=2, background='#d4d0c8')
            pstatAnova.pack(side=tkinter.LEFT,padx=2,pady=2, fill=tkinter.BOTH, expand=1)

            l=tkinter.Label(pstatInd,text="Individuals",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)        
            l=tkinter.Label(pstatBox,text="Box Plots",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)        
            l=tkinter.Label(pstatDist,text="Distributions",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)        
            l=tkinter.Label(pstatAnova,text="ANOVA",relief=tkinter.RAISED,bd=2, background='#d4d0c8')
            l.pack(side=tkinter.TOP,fill=tkinter.X,padx=2,pady=4)    
            
            self.killwidlist=[pstatInd,pstatBox,pstatDist,pstatAnova,botCon,topCon,ii]
            
        else:
            #windoze
            self.plotnb=PmwTtkNoteBook.PmwTtkNoteBook(rf,raisecommand=self.updateNB)
            self.plotnb.configure(hull_background='#d4d0c8',hull_width=500,hull_height=550)
            self.plotnb.pack(side=tkinter.TOP,fill='both',expand=1,padx=3,pady=3)

            #pages
            pstatInd=self.plotnb.add('Individuals',page_background='#d4d0c8')
            pstatDist=self.plotnb.add('Distributions',page_background='#d4d0c8')
            #pstatCorr=self.plotnb.add('Correlations',page_background='#d4d0c8')
            pstatBox=self.plotnb.add('Box Plots',page_background='#d4d0c8')
            pstatAnova=self.plotnb.add('ANOVA',page_background='#d4d0c8')

        #build the pages
        #individual
        self.pstatlist=ScrollTree.ScrolledTreeViewBox(pstatInd,width=650,height=250)
        self.pstatlist.setMode('browse')
        self.pstatlist.setColNames(('File','ROI#', 'Npix', 'Xcent', 'Ycent'))
        self.pstatlist.setDefaultWA()
        self.pstatlist.setSelect(self.partSelectROIList)
        self.pstatlist.setColors(('white', '#ffdddd', 'white', '#ddeeff'))
        self.pstatlist.pack(side=tkinter.TOP,padx=2,pady=4,expand=1,fill='x')

        #x0=self.mapdata.xvals[0]
        #y0=self.mapdata.yvals[0]
        #xs=self.mapdata.xvals[1]-self.mapdata.xvals[0]
        #ys=self.mapdata.yvals[1]-self.mapdata.yvals[0]
        self._buildpstatlist()

        self.pstatindview=Pmw.RadioSelect(pstatInd,buttontype='radiobutton',orient='vertical',command=self.partSelectROIList,hull_background='#d4d0c8')
        for text in ('Show All','Show Current','Show None'):
            self.pstatindview.add(text,background='#d4d0c8')
        self.pstatindview.setvalue('Show None')
        self.pstatindview.pack(side=tkinter.TOP,padx=3,pady=3)
        #export button
        b=PmwTtkButtonBox.PmwTtkButtonBox(pstatInd,orient='horizontal',hull_background='#d4d0c8')
        b.add('Export Data',command=self.exportPartStat,style='SBLUE.TButton',width=20) 
        b.add('Export Raw Data',command=self.exportRawROIData,style='NAVY.TButton',width=20) 
        b.add('Export to Channel',command=self.exportROIData2Channel,style='GREEN.TButton',width=20) 
        b.pack(side=tkinter.TOP,padx=5,pady=10)        

        #distribution
        #graph here
        self.phistgraph=MyGraph.MyGraph(pstatDist,whsize=(5,3),padx=5,pady=5,graphpos=[[.15,.1],[.9,.9]])
        f=tkinter.Frame(pstatDist,background='#d4d0c8')
        f.pack(side=tkinter.TOP,padx=2,pady=2)
        f1=tkinter.Frame(f,background='#d4d0c8')
        f1.pack(side=tkinter.LEFT,padx=2,pady=2)
        self.pstatdisttype=Pmw.RadioSelect(f1,buttontype='radiobutton',orient='vertical',command=self.getPHdata,hull_background='#d4d0c8')
        for text in ('Area', 'Conc/Intens',  'Correlations','Mult-Correl','Angle','Asp.Ratio'):
            self.pstatdisttype.add(text,background='#d4d0c8')
        self.pstatdisttype.setvalue('Area')
        self.pstatdisttype.pack(side=tkinter.TOP,padx=3,pady=3)

        self.pstatdisttypeB=Pmw.RadioSelect(f1,buttontype='checkbutton',orient='vertical',command=self.getPHdata,hull_background='#d4d0c8')
        for text in ('log X', 'Plot Cumlative','Use Area-Type Plot' ):
            self.pstatdisttypeB.add(text,background='#d4d0c8')
        self.pstatdisttypeB.pack(side=tkinter.TOP,padx=3,pady=3)
        
        f2=tkinter.Frame(f,background='#d4d0c8')
        f2.pack(side=tkinter.LEFT,padx=2,pady=2)
        g=Pmw.Group(f2,tag_text='Histogram Options',tag_background='#d4d0c8',hull_background='#d4d0c8',ring_background='#d4d0c8')
        g.pack(side=tkinter.TOP,padx=15,pady=5,expand='yes',fill='both')
        g.interior().configure(background='#d4d0c8')
        self.pstathistbins=Pmw.EntryField(g.interior(),labelpos='w',label_text='No. of Bins: ',validate='integer',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.pstathistbins.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)
        self.pstathistbins.setvalue(25)
        self.pstathistmin=Pmw.EntryField(g.interior(),labelpos='w',label_text='Min Value: ',validate='real',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.pstathistmin.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)        
        self.pstathistmin.setvalue(0)
        self.pstathistmax=Pmw.EntryField(g.interior(),labelpos='w',label_text='Max Value: ',validate='real',entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.pstathistmax.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)
        self.pstathistmax.setvalue(1)
        Pmw.alignlabels([self.pstathistbins,self.pstathistmin,self.pstathistmax])
        b=PmwTtkButtonBox.PmwTtkButtonBox(f2,orient='horizontal',hull_background='#d4d0c8')
        b.add('Update',command=self.doPHupdate,style='SBLUE.TButton',width=15) #doHupdate
        b.add('Export',command=self.doPHexport,style='GREEN.TButton',width=15) 
        b.pack(side=tkinter.TOP,padx=5,pady=10)        
        self.getPHdata()
        #boxplots
        self.pboxgraph=MyGraph.MyGraph(pstatBox,whsize=(5,3),padx=5,pady=5,graphpos=[[.15,.1],[.9,.9]])     

        self.pstatboxtype=Pmw.RadioSelect(pstatBox,buttontype='radiobutton',orient='vertical',command=self.makePartBoxPlot,hull_background='#d4d0c8')
        for text in ('ROIs','Channels'):
            self.pstatboxtype.add(text,background='#d4d0c8')
        self.pstatboxtype.setvalue('ROIs')
        self.pstatboxtype.pack(side=tkinter.TOP,padx=3,pady=3)

        b=PmwTtkButtonBox.PmwTtkButtonBox(pstatBox,orient='vertical',hull_background='#d4d0c8')
        b.add('Save Graph',command=self.pboxSave,style='GREEN.TButton',width=20) #doHupdate
        b.pack(side=tkinter.TOP,padx=3,pady=3)        
        

        #ANOVA
        f1=tkinter.Frame(pstatAnova,background='#d4d0c8')
        f1.pack(side=tkinter.LEFT,padx=2,pady=2)

        self.parttstattype=Pmw.RadioSelect(f1,buttontype='radiobutton',orient='vertical',command=self.doANOVAstats,hull_background='#d4d0c8')
        for text in ('Size Correct','Size Fix','Size Bias'):
            self.parttstattype.add(text,background='#d4d0c8')
        self.parttstattype.setvalue('Size Correct')
        self.parttstattype.pack(side=tkinter.TOP,padx=3,pady=3)   

        blist=[]
        for r in self.partroilist:
            blist.append(r.buffer+"*"+r.label)
        self.partanovasel=Pmw.ScrolledListBox(f1,labelpos='n',label_text='Select ROI',items=blist,listbox_selectmode=tkinter.EXTENDED,
                                              listbox_exportselection=tkinter.FALSE,selectioncommand=self.doANOVAstats,listbox_height=15,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.partanovasel.pack(side=tkinter.TOP,padx=4,pady=5,fill='both')

        f2=tkinter.Frame(pstatAnova,background='#d4d0c8')
        f2.pack(side=tkinter.LEFT,padx=2,pady=2)
        g=Pmw.Group(f2,tag_text='ANOVA Results',tag_background='#d4d0c8',ring_background='#d4d0c8',hull_background='#d4d0c8')
        g.pack(side=tkinter.TOP,padx=15,pady=5,expand='yes',fill='both')
        g.interior().configure(background='#d4d0c8')
        self.pstatanovaf=Pmw.EntryField(g.interior(),labelpos='w',label_text='F-value: ',entry_width=20,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.pstatanovaf.component('entry').configure(state=tkinter.DISABLED)
        self.pstatanovaf.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)
        self.pstatanovaf.setvalue('')
        self.pstatanovap=Pmw.EntryField(g.interior(),labelpos='w',label_text='p-value: ',entry_width=20,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.pstatanovap.component('entry').configure(state=tkinter.DISABLED)
        self.pstatanovap.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)        
        self.pstatanovap.setvalue('')
        Pmw.alignlabels([self.pstatanovaf,self.pstatanovap])
        
        self.pstatanovatext=Pmw.ScrolledText(f2,hull_background='#d4d0c8',hscrollmode='static',text_wrap='none')
        self.pstatanovatext.pack(side=tkinter.TOP,padx=15,pady=5,fill='both')
        self.pstatanovatext.tag_configure('red',foreground='red')
        self.pstatanovatext.tag_configure('black',foreground='black')
        self.pstatanovatext.tag_configure('blue',foreground='blue')
        self.pstatanovatext.tag_configure('green',foreground='darkgreen')
        self.pstatanovatext.tag_configure('orange',foreground='orange')

        if sys.platform!='darwin':
            self.plotnb.setnaturalsize()

    def update(self,mapdata,ps):
        self.mapdata=mapdata
        self.ps=ps
        self._params()
        commonchanlist=self.initcalc()
        self.partstatsel.setlist(commonchanlist)
        self._buildpstatlist()
        self.updatePartStat()
        self.partSelectROIList()
        self.getPHdata()  
        self.makePartBoxPlot()
        
        blist=[]
        for r in self.partroilist:
            blist.append(r.buffer+"*"+r.label)
        self.partanovasel.setlist(blist)
        self.pstatanovatext.setvalue("")        
        
        self.win.deiconify()
        print ('updated')

    def updateNB(self,page):
        self.ps.root.update()

    def kill(self,*event):
        self.exist=0
        self.partstatROIflag=0

        if sys.platform=='darwin':
            for w in self.killwidlist:
                w.destroy()
        self.win.destroy()

    def decodeCHANmask(self,roi,power,color=1,null=0):
        if null:
            return np.zeros(roi.shape,dtype=np.int32)
        roi=np.asarray(roi,dtype=np.int32)
        power=int(power)
        if power==0: return np.where(roi==0,color,0)
        else: return np.where(roi&power>0,color,0)

    def makeContourFromMask(self,mask):
        mask=mask.astype(np.uint8)
        contours = cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)[0]
        mc = max(contours, key=cv.contourArea)
        return mc

    def makeROImask(self,roi,data,color=1):
        data=np.array(data,dtype=np.float32)
        inp=data#cv.fromarray(data)
        #JOY
        #inp8=cv.CreateMat(inp.rows,inp.cols,cv.CV_8UC1)
        inp8 = inp.astype(np.uint8)
        #cv.Convert(inp,inp8)
        if not self.partStatuseWater:
            #cv.drawContours(inp8,roi,(color,color,color),(color,color,color),0,cv.FILLED)
            #JOY
            cv.drawContours(inp8,[roi],-1,(color,color,color),cv.FILLED)
            return inp8
        else:
            #print (roi,roi.shape)
            cv.drawContours(inp8,[roi],0,(color,color,color),cv.FILLED)   # changed from data to inp8 here and next line
            return inp8
        

    def exportPartStat(self):
        text=''
        basecol=['File','ROI#', 'Npix', 'Xcent', 'Ycent']
        for c in self.partstatsel.getcurselection():
            basecol.append(c)
            if self.partselstdd.getvalue()=='On':
                basecol.append(c+'_SD')
        for t in basecol:
            text+=t+'\t'
        text+='\n'
        for r in self.partroilist:
            text+=r.buffer+'\t'+r.label+'\t'
            l=self.pstatdict[r.buffer+"*"+r.label]
            if 'area' in l: text+=str(l['area'])+'\t'
            else: text+='\t'
            if ('xcenter' in l and 'ycenter' in l):
                text+=str(l['xcenter'])+'\t'+str(l['ycenter'])+'\t'
            else:
                text+=text+'\t\t'
            for c in self.partstatsel.getcurselection():
                listname=c+'&&'+self.partseltype.getvalue()
                if listname in l: text+=str(l[listname])+'\t'
                else: text+='\t'
                if self.partselstdd.getvalue()=='On':
                    if c+'&&SD' in l: text+=str(l[c+'&&SD'])+'\t'
                    else: text+='\t'
            text+='\n'
        #export to clipboard
        self.ps.root.clipboard_clear()
        self.ps.root.clipboard_append(text)
        globalfuncs.setstatus(self.ps.status,"Particle statistics saved to clipboard")

    def updatePartStat(self,*args):
        #kill all?
        self.pstatlist.clear()        
        #add new
        basecol=['File','ROI#', 'Npix', 'Xcent', 'Ycent']
        baseexp=[0,1,2,3,4]
        v=4
        if self.partmorphstat.getvalue()=='On':
            basecol.extend(['Angle', 'AspectRat', 'Perim.'])
            v+=3
        doCor=False
        for c in self.partstatsel.getcurselection():
            basecol.append(c)
            baseexp.append(v)
            v+=1
            if self.partselstdd.getvalue()=='On':
                basecol.append(c+'-SD')
                baseexp.append(v)
                v+=1
        if self.partselcorr.getvalue() !='Off' and len(self.partstatsel.getcurselection())>1:
            doCor=True
            if self.partselcorr.getvalue()=='On':
                alab=self.partstatsel.getcurselection()[0]
                blab=self.partstatsel.getcurselection()[1]
            else:
                alab=self.partstatsel.getcurselection()[1]
                blab=self.partstatsel.getcurselection()[0]                
            basecol.append(alab+':'+blab+':A')
            basecol.append(alab+':'+blab+':B1')
            basecol.append(alab+':'+blab+':B2')
            for ii in range(3):
                baseexp.append(v)
                v+=1
        print(tuple(basecol))
        self.pstatlist.setColNames(tuple(basecol))
        self.pstatlist.setDefaultWA()
        
        #add new values
        #x0=self.mapdata.xvals[0]
        #y0=self.mapdata.yvals[0]
        #xs=self.mapdata.xvals[1]-self.mapdata.xvals[0]
        #ys=self.mapdata.yvals[1]-self.mapdata.yvals[0]
        icounter=1
        for r in self.partroilist:
            buf=self.ps.dataFileBuffer[r.buffer]
            xcds=buf['data'].data.get(0)  # [:,:,1]
            ycds=buf['data'].data.get(1)  # [:,:,0]
            if icounter%10==0: print(icounter)
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
                ##area=abs(cv.ContourArea(r.mask))
                ##l['area']=area
            if ('xcenter' in l and 'ycenter' in l):
                xc=l['xcenter']
                yc=l['ycenter']
            else:
                if d is None: d=MomentMathClass.MomentClass(xcds,ycds,mask)
                xc=d.medx
                yc=d.medy                    
##                mom=cv.Moments(r.mask)
##                try:
##                    xcp=mom.m10/mom.m00
##                except:
##                    xcp=mom.m10
##                try:
##                    ycp=mom.m01/mom.m00
##                except:
##                    ycp=mom.m01
##                #these are pixels from the bottom left corner...
##                xc=x0+xcp*xs
##                yc=y0+ycp*ys
                l['xcenter']=xc
                l['ycenter']=yc

            arglist=[r.buffer,r.label,area,globalfuncs.valueclip_d(xc,5),globalfuncs.valueclip_d(yc,5)]

            if self.partmorphstat.getvalue()=='On':
                #do morphological analysis
                elip=dummy()
                if 'angle' in l: 
                    angle=l['angle']
                    perim=l['perim']
                    asprat=l['asprat']
                    elip.elp=1
                else:
                    if not self.partStatuseMask: cmask=r.mask
                    else: cmask=self.makeContourFromMask(r.mask)
                    elip = MomentMathClass.EllipseClass(cmask)
                    if elip.elp is not None:
                        angle = elip.angle
                        perim = elip.perim
                        asprat = elip.asprat
                        l['angle'] = angle
                        l['perim'] = perim
                        l['asprat'] = asprat    
                if elip.elp is not None:
                    arglist.append(globalfuncs.valueclip_d(angle,5))
                    arglist.append(globalfuncs.valueclip_d(asprat,5))
                    arglist.append(globalfuncs.valueclip_d(perim,5))

            for c in self.partstatsel.getcurselection():
                listname=c+'&&'+self.partseltype.getvalue()
                if listname in l:
                    ival=l[listname]
                    sval=l[c+'&&SD']
                else:
                    datind=buf['data'].labels.index(c)+2
                    xv=np.ravel(buf['data'].data.get(datind))#[:,:,datind])
                    #and deadtimes...
                    nodtx=0
                    if self.ps.datachan.getvalue()[0] in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodtx=1
                    if self.ps.dodt.get()==1 and not nodtx:
                        #DT: corFF=FF*exp(tau*1e-6*ICR)
                        icr=np.ravel(buf['data'].data.get(self.ps.DTICRchanval))
                        dtcor=np.exp(float(self.ps.deadtimevalue.getvalue())*1e-6*icr)
                        xv=xv*dtcor
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
                if self.partselstdd.getvalue()=='On': arglist.append(globalfuncs.valueclip_d(sval,5))
            if doCor:
#                (alab+':'+blab+':A')
#                (alab+':'+blab+':B1')
#                (alab+':'+blab+':B2')   
                if alab+':'+blab+':A' in l:
                    ival=l[alab+':'+blab+':A']
                else:
                    #do single correlation
                    datindA=buf['data'].labels.index(alab)+2
                    datindB=buf['data'].labels.index(blab)+2
                    xv=np.ravel(buf['data'].data.get(datindA))
                    yv=np.ravel(buf['data'].data.get(datindB))
                    #and deadtimes...
                    nodtx=0
                    if self.ps.datachan.getvalue()[0] in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodtx=1
                    if self.ps.dodt.get()==1 and not nodtx:
                        #DT: corFF=FF*exp(tau*1e-6*ICR)
                        icr=np.ravel(buf['data'].data.get(self.ps.DTICRchanval))
                        dtcor=np.exp(float(self.ps.deadtimevalue.getvalue())*1e-6*icr)
                        xv=yv*dtcor                
                        xv=yv*dtcor 
                    cpm=np.ravel(mask)
                    xv=xv[np.where(cpm>0)]
                    yv=yv[np.where(cpm>0)]  
                    initguess=(1,0)
                    try:
                        result,cov=curve_fit(globalfuncs.linearFit,xv,yv,p0=initguess)
                        ival=result[0]                       
                    except:
                        ival=0
                    l[alab+':'+blab+':A']=ival
                if alab+':'+blab+':B1' in l:
                    ival1=l[alab+':'+blab+':B1']
                    ival2=l[alab+':'+blab+':B2']
                else:
                    #do single correlation
                    datindA=buf['data'].labels.index(alab)+2
                    datindB=buf['data'].labels.index(blab)+2
                    xv=np.ravel(buf['data'].data.get(datindA))
                    yv=np.ravel(buf['data'].data.get(datindB))
                    #and deadtimes...
                    nodtx=0
                    if self.ps.datachan.getvalue()[0] in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodtx=1
                    if self.ps.dodt.get()==1 and not nodtx:
                        #DT: corFF=FF*exp(tau*1e-6*ICR)
                        icr=np.ravel(buf['data'].data.get(self.ps.DTICRchanval))
                        dtcor=np.exp(float(self.ps.deadtimevalue.getvalue())*1e-6*icr)
                        xv=yv*dtcor                
                        xv=yv*dtcor 
                    cpm=np.ravel(mask)
                    xv=xv[np.where(cpm>0)]
                    yv=yv[np.where(cpm>0)]  
                    fitobj=MultiFitObj.MultiFitObj(xv,yv,2,default=True)
                    result=minimize(fitobj.eqn,fitobj.initguess,method='Nelder-Mead')
                    fp=result.x
                    ival1=fp[0]
                    ival2=fp[1]   
                    l[alab+':'+blab+':B1']=ival1
                    l[alab+':'+blab+':B2']=ival2
                arglist.append(globalfuncs.valueclip_d(ival,5))
                arglist.append(globalfuncs.valueclip_d(ival1,5))
                arglist.append(globalfuncs.valueclip_d(ival2,5))
                    
            newitem=self.pstatlist.insert(list(arglist))
            if l!=self.pstatdict[r.buffer+"*"+r.label]:
                self.pstatdict[r.buffer+"*"+r.label]=l
        self.makePartBoxPlot()


    def partSelectROIList(self,*args):
        #check for switch
        if self.pstatindview.getvalue()=='Show None':
            self.partstatROIflag=0
        if self.pstatindview.getvalue()=='Show Current':
            self.partstatROIflag=1            
        if self.pstatindview.getvalue()=='Show All':
            self.partstatROIflag=2
        self.partShowROIOption()

    def partShowROIOption(self):
        if self.ps.datachan.get()==():
            return
        if len(self.pstatlist.curselection())<1: return
        if self.partstatROIflag==0:
            self.ps.domapimage()
            return
        globalfuncs.setstatus(self.ps.status,"DISPLAYING...")
        datind=self.mapdata.labels.index(self.ps.datachan.getvalue()[0])+2
        datlab=self.mapdata.labels[datind-2]

        pic=self.mapdata.data.get(datind)[::-1,:]#[::-1,:,datind]
        mi=self.mapdata.mapindex[::-1,:]
        picmsk=[]
        nodt=0
        if self.ps.datachan.getvalue()[0] in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodt=1
        if self.ps.dodt.get()==1 and not nodt:
            #DT: corFF=FF*exp(tau*1e-6*ICR)
            icr=self.mapdata.data.get(self.ps.DTICRchanval)[::-1,:]#[::-1,:,self.ps.DTICRchanval]
            dtcor=np.exp(float(self.ps.deadtimevalue.getvalue())*1e-6*icr)
            pic=pic*dtcor
        #i0 corr?
        if self.ps.doI0c.get()==1:
            #geti0
            iind=self.mapdata.labels.index(self.i0chan.getvalue())+2
            i0dat=self.mapdata.data.get(iind)[::-1,:]#[::-1,:,iind]
            #divide
            (xlen,ylen)=self.mapdata.data.shape[:2]
            newdata=np.zeros((xlen,ylen),dtype=np.float32)
            for i in range(xlen):
                for j in range(ylen):
                    if i0dat[i,j]!=0:
                        newdata[i,j]=float(pic[i,j])/float(i0dat[i,j])
            pic=newdata

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
                #JOY
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

    def getPHdata(self,*args):
        self.pstathdata=[]
        self.wtdata=[]
        if self.pstatdisttype.getvalue()=='Correlations':
            if self.partselcorr.getvalue()=='Off':
                return
        for r in self.partroilist:
            buf=self.ps.dataFileBuffer[r.buffer]
            xcds=buf['data'].data.get(1)  # [:,:,1]
            ycds=buf['data'].data.get(0)  # [:,:,0]
            if self.partStatuseMask: mask=r.mask
            else: mask=np.asarray(self.makeROImask(r.mask,np.zeros(buf['data'].data.get(0).shape)))
            l=self.pstatdict[r.buffer+"*"+r.label]
            if self.pstatdisttype.getvalue()=='Area':
                if 'area' in l: self.pstathdata.append(l['area'])
                else:
                    d=MomentMathClass.MomentClass(xcds,ycds,mask)
                    area=d.A##area=abs(cv.ContourArea(r.mask))
                    self.pstathdata.append(area)
                    l['area']=area     
            elif self.pstatdisttype.getvalue()=='Angle':
                if 'angle' in l:
                    self.pstathdata.append(l['angle'])
                else: continue                    
            elif self.pstatdisttype.getvalue()=='Asp.Ratio':
                if 'asprat' in l:
                    self.pstathdata.append(l['asprat'])
                else: continue                    
            elif self.pstatdisttype.getvalue()=='Correlations':
                if self.partselcorr.getvalue()=='On':
                    alab=self.partstatsel.getcurselection()[0]
                    blab=self.partstatsel.getcurselection()[1]
                else:
                    alab=self.partstatsel.getcurselection()[1]
                    blab=self.partstatsel.getcurselection()[0]                 
                self.pstathdata.append(l[alab+':'+blab+':A'])
            elif self.pstatdisttype.getvalue()=='Mult-Correl':
                if self.partselcorr.getvalue()=='On':
                    alab=self.partstatsel.getcurselection()[0]
                    blab=self.partstatsel.getcurselection()[1]
                else:
                    alab=self.partstatsel.getcurselection()[1]
                    blab=self.partstatsel.getcurselection()[0]                 
                self.pstathdata.append(l[alab+':'+blab+':B1'])
                self.pstathdata.append(l[alab+':'+blab+':B2'])
            else:
                if len(self.partstatsel.getcurselection())<1:
                    if 'ICR' in self.mapdata.labels:
                        c='ICR'
                    else: return
                else: c=self.partstatsel.getcurselection()[0]
                listname=c+'&&'+self.partseltype.getvalue()
                if listname in l:
                    ival=l[listname]
                else:
                    datind=buf['data'].labels.index(c)+2
                    xv=np.ravel(buf['data'].data.get(datind))#[:,:,datind])
                    #and deadtimes...
                    nodtx=0
                    if self.ps.datachan.getvalue()[0] in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodtx=1
                    if self.ps.dodt.get()==1 and not nodtx:
                        #DT: corFF=FF*exp(tau*1e-6*ICR)
                        icr=np.ravel(buf['data'].data.get(self.ps.DTICRchanval))
                        dtcor=np.exp(float(self.ps.deadtimevalue.getvalue())*1e-6*icr)
                        xv=xv*dtcor
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
                    l[listname]=ival
                self.pstathdata.append(ival)
            if l!=self.pstatdict[r.buffer+"*"+r.label]:
                self.pstatdict[r.buffer+"*"+r.label]=l
            if "Use Area-Type Plot" in self.pstatdisttypeB.getvalue():
                self.wtdata.append(l['area'])
        #setmax and nb
        ##self.pstathistbins.setvalue(min(25,int(len(self.pstathdata)/4)))
        if len(self.pstathdata)<1: return
        if "Use Area-Type Plot" in self.pstatdisttypeB.getvalue() and self.pstatdisttype.getvalue() not in ['Correlations']:
            self.pstathistmax.setvalue(max(self.wtdata))           
        else:
            self.pstathistmax.setvalue(max(self.pstathdata))

        self.doPHupdate()
        
    def doPHupdate(self,passback=0):
        #send to histogram maker
        nb=int(self.pstathistbins.getvalue())
        if nb<1: nb=1
        log=False
        if "log X" in self.pstatdisttypeB.getvalue():
            log=True
        if self.pstatdisttype.getvalue() not in ['Area','Conc/Intens']:
            log=False
        if "Use Area-Type Plot" in self.pstatdisttypeB.getvalue() and self.pstatdisttype.getvalue() not in ['Correlations']:
            maindata=self.wtdata
            wtdata=self.pstathdata
        else:
            wtdata=None
            maindata = self.pstathdata
        hplotdata=histclass.Histogram(maindata,bins=nb,nmin=self.pstathistmin.getvalue(),nmax=self.pstathistmax.getvalue(),log=log, wts=wtdata)
        if passback: return hplotdata
        #remove old
        self.phistgraph.cleargraphs()
        #plot data
        self.phistgraph.bar(tuple(hplotdata[:,0]),tuple(hplotdata[:,1]),text='H')
        if "Plot Cumlative" in self.pstatdisttypeB.getvalue():
            cumdat=[]
            s=0
            for i in hplotdata[:,1]:
               s+=i
               cumdat.append(s)
            self.phistgraph.twinAxes('cumplot')
            self.phistgraph.plot(tuple(hplotdata[:,0]),tuple(cumdat),color='red',text='H',axes='cumplot')
        
        self.phistgraph.draw()        

    def doPHexport(self):
        data=self.doPHupdate(passback=1)
        text='Bin\tFrequency\n'
        for i in range(len(data[:,0])):
            text+=str(data[i,0])+'\t'+str(data[i,1])+'\n'
        #export to clipboard
        self.ps.root.clipboard_clear()
        self.ps.root.clipboard_append(text)
        globalfuncs.setstatus(self.ps.status,"Histogram data saved to clipboard")

    def pboxSave(self):
        fn=globalfuncs.ask_save_file('graph.png',self.ps.filedir.get())
        if fn=='':
            print('Graph save cancelled')
            globalfuncs.setstatus(self.ps.status,'Graph save cancelled')
            return        
        self.pboxgraph.savegraph(fn)

    def exportRawROIData(self):

        fn=globalfuncs.ask_save_file('roidata',self.ps.filedir.get())
        if fn=='':
            print('Raw save cancelled')
            globalfuncs.setstatus(self.ps.status,'Raw save cancelled')
            return  

        data=[]
        for r in self.partroilist:
            if len(self.partstatsel.getcurselection())<1:
                return
            c=self.partstatsel.getcurselection()[0]
            l=self.pstatdict[r.buffer+"*"+r.label]
            if c+'&&DATA' in l:
                subd=[]
                for d in l[c+'&&DATA']:
                    subd.append(float(d))
                data=np.array(subd)      

                np.savetxt(fn+"_"+r.label+".txt",data)
      
    def exportROIData2Channel(self):
        #get list
        basecol=['AllROIs']
        if self.partmorphstat.getvalue()=='On':
            basecol.extend(['angle', 'asprat', 'perim'])
        doCor=False
        for c in self.partstatsel.getcurselection():
            basecol.append(c+'&&'+self.partseltype.getvalue())
        if self.partselcorr.getvalue() !='Off' and len(self.partstatsel.getcurselection())>1:
            doCor=True
            if self.partselcorr.getvalue()=='On':
                alab=self.partstatsel.getcurselection()[0]
                blab=self.partstatsel.getcurselection()[1]
            else:
                alab=self.partstatsel.getcurselection()[1]
                blab=self.partstatsel.getcurselection()[0]                
            basecol.append(alab+':'+blab+':A')
            basecol.append(alab+':'+blab+':B1')
            basecol.append(alab+':'+blab+':B2')
        print(tuple(basecol))        
        #select channel(s)
        self.selectExportdialog=Pmw.SelectionDialog(self.imgwin,title="Select Columns to Export",buttons=('OK','Cancel'),defaultbutton='Cancel',
                                                   scrolledlist_labelpos='n',label_text='Select Columns',scrolledlist_items=basecol,
                                                   command=self.exportROIData2ChannelSelected)
        self.selectExportdialog.component('scrolledlist').component('listbox').configure(selectmode=tkinter.EXTENDED)        
        
        
    def exportROIData2ChannelSelected(self,result):
        ecs = self.selectExportdialog.getcurselection()
        self.selectExportdialog.withdraw()
        if result =='Cancel' or ecs==():
            print('No export taken')
            return            
        #figure out which buffers to add data chans...
        bufferlist = []
        imgshape={}
        for r in self.partroilist:
            if r.buffer not in bufferlist:
                bufferlist.append(r.buffer)
                buf=self.ps.dataFileBuffer[r.buffer]
                shape=buf['data'].data.get(0).shape
                imgshape[r.buffer]=shape
        #make data chans
        for b in bufferlist:
            for ec in ecs:
                #make new emptyfield
                i=0
                newdata = np.zeros(imgshape[b],dtype=np.float32)
                for r in self.partroilist:
                    l=self.pstatdict[r.buffer+"*"+r.label]
                    if ec in l:
                        color = l[ec]
                    elif ec == 'AllROIs':
                        color = 2**i
                        i+=1
                    else:
                        color = 0
                    #print (r.label, ec, color)
                    if r.buffer!=b: continue
                    if self.partStatuseMask: 
                        newdata=np.where(r.mask>0,color,newdata)
                    elif not self.partStatuseWater:
                        cv.drawContours(newdata,[r.mask], -1, (color,color,color),-1)
                    else:
                        cv.drawContours(newdata,[r.mask],-1,(color,color,color),-1)                                        
                #add channel to data
                nameroot='ROIexp'+'-'+ec+'-'
                valid=0
                i=1
                while not valid:
                    newname=nameroot+str(i)
                    if newname not in self.ps.dataFileBuffer[b]['data'].labels:
                        valid=1
                    else:
                        i+=1                
                self.ps.addchannel(newdata,newname,fbuffer=b)
                

    def makePartBoxPlot(self,*args):
        #clear:
        self.pboxgraph.cleargraphs()
        #make data (should be done already...)
        data=[]
        label=[]
        if self.pstatboxtype.getvalue()=='ROIs':
            for r in self.partroilist:
                if len(self.partstatsel.getcurselection())<1:
                    return
                c=self.partstatsel.getcurselection()[0]
                l=self.pstatdict[r.buffer+"*"+r.label]
                if c+'&&DATA' in l:
                    label.append(r.label)
                    subd=[]
                    for d in l[c+'&&DATA']:
                        subd.append(float(d))
                    data.append(subd)
        else:
            for c in self.partstatsel.getcurselection():
                label.append(c)
                subd=[]
                for r in self.partroilist:
                    l=self.pstatdict[r.buffer+"*"+r.label]
                    listname=c+'&&'+self.partseltype.getvalue()
                    if listname in l: subd.append(l[listname])
                data.append(subd)
        #make graph
        self.pboxgraph.boxplot(data,xnames=label,notch=0,sym='g+',boxcolor='green',whiskers='green',vert=1,whis=1.5,positions=None,widths=None)
        self.pboxgraph.draw()
            

    def doANOVAstats(self,*args):
        #make data (should be done already...)
        self.pstatanovatext.setvalue("")
        data=[]
        if len(self.partanovasel.getcurselection())<2: return
        for r in self.partanovasel.getcurselection():
            if len(self.partstatsel.getcurselection())<1:
                return
            c=self.partstatsel.getcurselection()[0]
            l=self.pstatdict[r]
            if c+'&&DATA' in l:
                subd=[]
                for d in l[c+'&&DATA']:
                    subd.append(float(d))
                data.append(subd)
        fval,pval=stats.f_oneway(*list(data))
        self.pstatanovaf.setvalue(str(fval))
        self.pstatanovap.setvalue(str(pval))

        text=''
        etext=''
        testlist=list(itertools.combinations(self.partanovasel.getcurselection(),2))
        p05=[]
        p01=[]
        p005=[]
        p001=[]
        for t in testlist:
            l0=self.pstatdict[t[0]]
            l1=self.pstatdict[t[1]]
            d0=l0[c+'&&DATA']
            d1=l1[c+'&&DATA']

            
            if self.parttstattype.getvalue()=='Size Bias':
                #case with large N points in t-test bias (everything seems significant)     
                tv1,pv=stats.ttest_ind(np.array(d0),np.array(d1))
                print(tv1,pv)
            else:

                #cases with manual adjustment of t-test values
                mean0=np.mean(np.array(d0))
                mean1=np.mean(np.array(d1))
                std0=np.std(np.array(d0))
                std1=np.std(np.array(d1))
                np0=len(np.array(d0))
                np1=len(np.array(d1))

                if self.parttstattype.getvalue()=='Size Correct':
                    #adjusting std to se for N bias (good, but less conservative)
                    se0=std0*math.sqrt(np0)/2
                    se1=std1*math.sqrt(np1)/2
                    tstat=(mean0-mean1)/math.sqrt((se0**2/np0)+(se1**2/np1))
                    df=((se0**2/np0)+(se1**2/np1))**2/((se0**4/(np0**2*(np0-1)))+(se1**4/(np1**2*(np1-1))))
                    pv=stats.t.sf(abs(tstat),int(df))
                    print(tstat,df,pv)
                elif self.parttstattype.getvalue()=='Size Fix':
                    #removing N and fixing df to lower number (good, more conservative - less significant results due to smaller df)
                    tstat2=(mean0-mean1)/math.sqrt((std0**2/4)+(std1**2/4))
                    df2=((std0**2/4)+(std1**2/4))**2/((std0**4/(4**2*(4-1)))+(std1**4/(4**2*(4-1))))
                    pv=stats.t.sf(abs(tstat2),int(df2))
                    print(tstat2,df2,pv)
                else:
                    pv=1

            if pv<=0.05 and pv>0.01: p05.append([t,pv])
            if pv<=0.01 and pv>0.005: p01.append([t,pv])
            if pv<=0.005 and pv>0.001: p005.append([t,pv])
            if pv<=0.001: p001.append([t,pv])
            at=t[0]+' v. '+t[1]+' has p='+str(globalfuncs.valueclip_d(pv,6))+'\n'
            atl='black'
            if pv<0.05:
                atl='blue'
            if pv<0.01:
                atl='green'
            if pv<0.005:
                atl='orange'
            if pv<0.001:
                atl='red'
            #if pv<0.0001:
            #    atl='black'
            self.pstatanovatext.insert(0.0,at,atl)
            ##etext+=at
        for t,pv in p05: text+=t[0]+' v. '+t[1]+' has p<0.05     ('+str(globalfuncs.valueclip_d(pv,6))+')\n'
        text+='\n\n\n'
        self.pstatanovatext.insert(0.0,text,'blue')
        text=''
        for t,pv in p01: text=t[0]+' v. '+t[1]+' has p<0.01     ('+str(globalfuncs.valueclip_d(pv,6))+')\n'
        text+='\n'
        self.pstatanovatext.insert(0.0,text,'green')
        text=''
        for t,pv in p005: text+=t[0]+' v. '+t[1]+' has p<0.005    ('+str(globalfuncs.valueclip_d(pv,6))+')\n'
        text+='\n'
        self.pstatanovatext.insert(0.0,text,'orange')
        text=''
        for t,pv in p001: text+=t[0]+' v. '+t[1]+' has p<0.001    ('+str(globalfuncs.valueclip_d(pv,6))+')\n'
        text+='\n'
        self.pstatanovatext.insert(0.0,text,'red')
        
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

    
   