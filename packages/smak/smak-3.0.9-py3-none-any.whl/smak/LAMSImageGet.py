#Create SMAK from ICP-MS

#standard libraries
import csv
import datetime
import h5py
import math
import os
import string
import time
import tkinter
import tkinter.filedialog
import tkinter.simpledialog
from dateutil.parser import parse


#third party
import numpy as np
import Pmw
from scipy import interpolate

#local
import globalfuncs
import MyGraph
from ImageGet import EmptyHDF5, HDF5get, SuperClass




def ask_for_file(defaults,dir,check=1,multi=False):
    f = ''
    if not os.path.exists(dir): dir=''
    if not multi: func=tkinter.filedialog.askopenfilename
    else: func=tkinter.filedialog.askopenfilenames
    if dir=='':
        f = func(filetypes=defaults)
    else:
        f = func(filetypes=defaults,initialdir=dir)        
    return f

####################################
## Main Data Class
####################################

class LAMSData(SuperClass):
    
    def __init__(self,fn,wd,comments=""):
        self.type='LAMS'
        
        self.wd=wd
        self.fn=fn

        self.isVert=0
        self.energy='1'
        self.comments=comments

    def addLabelData(self,labels):
        self.labels=labels
        self.channels=len(labels)
        
    def addCoordData(self,xs,ys):
        self.xvals=xs
        self.yvals=ys
        self.nxpts=len(xs)
        self.nypts=len(ys)

    def finalize(self,dt):
        self.hdf5=h5py.File(os.path.join(self.wd[0],'workingfile'+str(self.wd[1])+'.hdf5'),'w')  

        self.hdf5group=self.hdf5.create_group("main")
        print(self.hdf5group.name)

        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dt,maxshape=(5000,5000,None),dtype='float')
        print(self.hdf5data.size,self.hdf5data.shape)
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)
                

        hdf5xd=self.hdf5group.create_dataset("xdata",(self.nxpts,),dtype='float',data=self.xvals)
        hdf5yd=self.hdf5group.create_dataset("ydata",(self.nypts,),dtype='float',data=self.yvals)
        hdf5xd.attrs.create("pts",self.nxpts)
        hdf5yd.attrs.create("pts",self.nypts)
        self.hdf5group.attrs.create("channels",self.channels)
        self.hdf5group.attrs.create("origin",self.type)
        self.hdf5group.attrs.create("isVert",self.isVert)
        self.hdf5group.attrs.create("labels",self.labels)
        self.hdf5group.attrs.create("comments",self.comments)
        self.hdf5group.attrs.create("energy",self.energy)

    
        
####################################
## Main
####################################

class GetData():

    def __init__(self,root,callback):
        self.master = root
        self.complete=False
        self.callback=callback
        
    def load_data_file(self,workdir=None,filedir=None):
        #for file type determination
        if workdir is None:
            wd=['',0]
        else:
            if workdir.get() is None:
                wd=['',workdir.wfn]
            else:
                wd=[workdir.get(),workdir.wfn]
        print(wd)
        self.wd=wd
        
        fn=ask_for_file([("laser log files","*.csv"),("all files","*")],filedir.get(),multi=False)
                
        fp=fn.split('.')
        exten=fp[-1]
    
        if exten.lower()!="csv":
            print("incorrect file type")
            return
        
        cwd=os.path.dirname(fn)       
        
        fid=open(fn,"rU")
        csvread = csv.reader(fid)
        filehdata = []
        for r in csvread:
            filehdata.append(r)
        fid.close()
        
        columns=[' Comment','Timestamp',' Sequence Number',' X(um)',' Y(um)',' Laser State']
        coldict={}
        for c in columns:
            coldict[c]=filehdata[0].index(c)
    
    
        triggers=[]
        sitem={}
        rows=[]
        t0 = parse(filehdata[1][coldict["Timestamp"]])
        for r in filehdata[1:]:
            if r[coldict[" Sequence Number"]] != "": 
                if len(sitem) != 0:
                    sitem['rows']=rows
                    triggers.append(sitem)
                    rows=[]
                    sitem={}
                sitem['seq']=int(r[coldict[" Sequence Number"]])
                sitem['fn']=r[coldict[" Comment"]]
    
            ritem={}
            t1 = parse(r[coldict["Timestamp"]])
            dttd = t1-t0
            td=dttd.total_seconds()
            ritem['td']=td
            ritem['x']=float(r[coldict[" X(um)"]])
            ritem['y']=float(r[coldict[" Y(um)"]])
            ritem['ls']=r[coldict[" Laser State"]]
            rows.append(ritem)
        
        if len(rows) != 0:                
            sitem['rows']=rows
            triggers.append(sitem)        
        
        seqnames = []
        laseronoff = {}
        self.xlims={}
        self.ylims={}
        for t in triggers:
            if t["fn"] not in seqnames:
                seqnames.append(t["fn"])
                cls="Off"
                st=0
                lo=[0,0]
                xs=[1e100,0]
                ys=[1e100,0]
                for r in t["rows"]:
                    xs=[min(xs[0],r['x']),max(xs[1],r['x'])]
                    ys=[min(ys[0],r['y']),max(ys[1],r['y'])]
                    if r["ls"]!=cls:
                        lo[st]=r['td']
                        st+=1
                        if cls=="Off": cls="On"
                        else: cls="Off"
                laseronoff[t["fn"]]=lo
                self.xlims[t["fn"]]=xs
                self.ylims[t["fn"]]=ys
        
        self.laseronoff=laseronoff  #dict of seqnames as indices
        self.seqnames=seqnames  
        
        fn=ask_for_file([("LAMS data files","*.csv"),("all files","*")],cwd,multi=False)
                
        fp=fn.split('.')
        exten=fp[-1]
    
        if exten.lower()!="csv":
            print("incorrect file type")
            return        
        
        self.fn=fn
        fid=open(fn,"rU")
        csvread = csv.reader(fid)
        rawdata = []
        for r in csvread:
            rawdata.append(r)
        fid.close()        
    
        self.comments = rawdata[2]        
        
        self.dataheader = rawdata[3]
        print(self.dataheader)
        
        self.datablock = []
        for r in rawdata[4:]:
            if len(r)==len(self.dataheader):
                self.datablock.append([float(x) for x in r])
        self.datablock=np.array(self.datablock)
        self.datablock=np.transpose(self.datablock)
        print(self.datablock.shape)
        tic = np.sum(self.datablock[1:],0)
        dtic = np.gradient(tic,self.datablock[0])
        initoff = self.datablock[0,np.argmax(dtic[0:30])]
        
        self.plotter = Pmw.Dialog(self.master,title="LAMS Data View vs Time",buttons=("Accept","Cancel"),
                                  command=self.acceptSettings)
        self.plotter.userdeletefunc(func=self.killplot)  
        mh=self.plotter.interior()    
        h=tkinter.Frame(mh,bg='black')
        h.pack(side=tkinter.TOP,fill='both')
                
        f=tkinter.Frame(h,bg='#d4d0c8')
        f.pack(side=tkinter.LEFT,fill='both')

        #channel to plot
        self.plotFile=Pmw.ComboBox(f,
                        scrolledlist_items=self.dataheader[1:],dropdown=1,selectioncommand=self.updatePlot,
                        labelpos='w',label_text='Plot Sequence',history=0,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.plotFile.selectitem(self.dataheader[1],setentry=1)
        self.plotFile.pack(side=tkinter.TOP,fill=tkinter.X,expand=1,padx=5,pady=10)  
        #offset
        self.timeoffset=Pmw.EntryField(f,labelpos='w',label_text='Time Synch Offset: ',entry_width=15,hull_background='#d4d0c8',
                                       command=self.updatePlot,label_background='#d4d0c8',validate='real')
        self.timeoffset.setvalue(initoff)   #to be filled in
        self.timeoffset.pack(side=tkinter.TOP,fill=tkinter.X,pady=10)        
        #start
        self.startFile=Pmw.ComboBox(f,
                        scrolledlist_items=seqnames,dropdown=1,
                        labelpos='w',label_text='Starting Sequence',history=0,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.startFile.selectitem(seqnames[0],setentry=1)
        self.startFile.pack(side=tkinter.TOP,fill=tkinter.X,expand=1,padx=5,pady=10)       
        #end
        self.endFile=Pmw.ComboBox(f,
                        scrolledlist_items=seqnames,dropdown=1,
                        labelpos='w',label_text='Ending Sequence',history=0,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.endFile.selectitem(seqnames[-1],setentry=1)
        self.endFile.pack(side=tkinter.TOP,fill=tkinter.X,expand=1,padx=5,pady=10)               
        #background start
        self.bgstart=Pmw.EntryField(f,labelpos='w',label_text='Background Start: ',entry_width=15,command=None,hull_background='#d4d0c8',label_background='#d4d0c8',validate='real')
        self.bgstart.setvalue(0)
        self.bgstart.pack(side=tkinter.TOP,fill=tkinter.X,pady=10)        
        #background end
        self.bgend=Pmw.EntryField(f,labelpos='w',label_text='Background End: ',entry_width=15,command=None,hull_background='#d4d0c8',label_background='#d4d0c8',validate='real')
        self.bgend.setvalue(int(self.datablock[0][-1]))
        self.bgend.pack(side=tkinter.TOP,fill=tkinter.X,pady=10)        
        #background thresh
        self.bgthresh=Pmw.EntryField(f,labelpos='w',label_text='Background Thresh: ',entry_width=15,command=None,hull_background='#d4d0c8',label_background='#d4d0c8',validate='real')
        self.bgthresh.setvalue(0)
        self.bgthresh.pack(side=tkinter.TOP,fill=tkinter.X,pady=10)     
        # fitbac
        b=Pmw.ButtonBox(f,hull_background='#d4d0c8')
        b.add('Fit background',command=self.doBackground,width=15)
        b.pack(side=tkinter.TOP,fill=tkinter.X,padx=5,pady=5)        
        self.back=None
        self.plottype=Pmw.RadioSelect(f,labelpos=tkinter.W,buttontype='radiobutton',label_text='Plot: ',label_background='#d4d0c8',command=self.updatePlot,hull_background='#d4d0c8',frame_background='#d4d0c8')
        self.plottype.add('Data+Back',background='#d4d0c8')
        self.plottype.add('BackRemoved',background='#d4d0c8')
        self.plottype.setvalue('Data+Back')        
        self.plottype.pack(side=tkinter.TOP,fill=tkinter.X,pady=4)
        
        self.graphT=MyGraph.MyGraph(h,whsize=(5.5,4),side=tkinter.LEFT,padx=2,graphpos=[[.15,.1],[.9,.9]])  
        self.graphALL=MyGraph.MyGraph(mh,whsize=(8.,4),side=tkinter.TOP,padx=2,graphpos=[[.15,.1],[.93,.9]])  
        
        #add data to plots
        print(tuple(self.datablock[0,0:30]))
        self.graphT.plot(tuple(self.datablock[0,0:30]),tuple(self.datablock[self.dataheader.index(self.plotFile.get()),0:30]),text=self.plotFile.get(),color='green',symbol='.')
#        self.graphT.plot(tuple(self.datablock[0,0:30]),tuple(dtic[0:30]),text=self.plotFile.get(),color='green')

        self.graphT.addMarker(float(self.timeoffset.get()),color='white')
        self.graphALL.plot(tuple(self.datablock[0,:]),tuple(self.datablock[self.dataheader.index(self.plotFile.get()),:]),text=self.plotFile.get(),color='green')
        self.graphALL.addMarker(float(self.bgstart.get()),y=float(self.bgend.get()),color='yellow',secondcolor='red',second=True)

        
        self.graphT.draw()
        self.graphALL.draw()
        
        self.plotter.show()


    def doBackground(self,start=None,end=None):
        if start is None:
            start = int(self.bgstart.get())
        if end is None:
            end = int(self.bgend.get())
        start = self.indexTime(start)
        end = self.indexTime(end)     
        
        adata = self.datablock[self.dataheader.index(self.plotFile.get()),:]
        print("a data:")
        print(adata)
        print()
        bset = np.where(adata<int(self.bgthresh.get()))
        print("b set:")
        print(bset)
        print()
        bset=list(bset)
        print("b set list:")
        print(bset)
        print()
        print(len(bset[0]))
        if len(bset[0])<2:
            print('no data in threshold')
            return
        if len(bset[0])>500:
            bset[0]=self.arrayedit(bset[0])
        print(len(bset[0]))
        bset=tuple(bset)
        
        self.back = [0]
        for i in range(self.datablock.shape[0]):
            if i==0: continue
            x_points = self.datablock[0][bset]    
            y_points = self.datablock[i][bset]                    
            self.back.append(interpolate.UnivariateSpline(x_points,y_points,k=1))

        self.updatePlot()

    
    def arrayedit(self,a):
        a=a[1:-1]
        final = []
        c=1
        for i in range(len(a)):
            if i<len(a)-1:
                if a[i+1]==a[i]+1: 
                    c+=1
                    if c>1: final.append(a[i])
                    continue
                if c==0:
                    final.append(a[i])
                else:
                    c==0
                    continue
        while len(final)>1000:
            final=final[::2]
        return final

    def updatePlot(self,*args):
        self.graphT.cleargraphs()
        self.graphALL.cleargraphs()
        
        self.graphT.plot(tuple(self.datablock[0,0:30]),tuple(self.datablock[self.dataheader.index(self.plotFile.get()),0:30]),text=self.plotFile.get(),color='green',symbol='.')
        self.graphT.addMarker(float(self.timeoffset.get()),color='white')

#        if self.bgstart.get()==self.bgend.get():
#            self.graphALL.plot(tuple(self.datablock[0,:]),tuple(self.datablock[self.dataheader.index(self.plotFile.get()),:]),text=self.plotFile.get(),color='green')
#        else:
#            background = self.calcBackground()
#            dataremoved = self.removeBackground(background)
#            self.graphALL.plot(tuple(self.datablock[0,:]),tuple(dataremoved[self.dataheader.index(self.plotFile.get()),:]),text=self.plotFile.get(),color='green')

        if self.plottype.getvalue()=='Data+Back':
            self.graphALL.plot(tuple(self.datablock[0,:]),tuple(self.datablock[self.dataheader.index(self.plotFile.get()),:]),text=self.plotFile.get(),color='green')
            if self.back is not None:
                self.graphALL.plot(tuple(self.datablock[0,:]),tuple(self.back[self.dataheader.index(self.plotFile.get())](self.datablock[0,:])),text='back',color='orange')

        else:

            if self.back is None:
                self.graphALL.plot(tuple(self.datablock[0,:]),tuple(self.datablock[self.dataheader.index(self.plotFile.get()),:]),text=self.plotFile.get(),color='green')
            else:
                #background = self.calcBackground()
                dataremoved = self.removeBackground()
                self.graphALL.plot(tuple(self.datablock[0,:]),tuple(dataremoved[self.dataheader.index(self.plotFile.get()),:]),text=self.plotFile.get(),color='green')
            
            
        self.graphALL.addMarker(float(self.bgstart.get()),y=float(self.bgend.get()),color='yellow',secondcolor='red',second=True)
        
        self.graphT.draw()
        self.graphALL.draw()


    def indexTime(self,val):
        return np.where(self.datablock[0,:]>val)[0][0]

#    def calcBackground(self,start=None,end=None):
#        if start is None:
#            start = int(self.bgstart.get())
#        if end is None:
#            end = int(self.bgend.get())
#        start = self.indexTime(start)
#        end = self.indexTime(end)            
#            
#        background = np.average(self.datablock[:,start:end],axis=1)   
#        return background
 
    def removeBackground(self):
        dataremoved = np.copy(self.datablock)
        for i in range(self.datablock.shape[0]):
            if i==0: continue
            dataremoved[i,:]=self.datablock[i,:]-self.back[i](self.datablock[0,:])    
            #print i,back[i]
        return dataremoved                  
        
    def acceptSettings(self, result):
        print("time offset: ", self.timeoffset.get(),"\n \n")
        timeoffsetVal=float(self.timeoffset.get())
        bgstartVal=int(self.bgstart.get())
        bgendVal=int(self.bgend.get())
        startSeq=self.startFile.get()
        endSeq=self.endFile.get()
        self.plotter.withdraw()
        if result=='Cancel': return
        if self.back is None:
            print('no background')
            return
        #calculate backgrounds
        #background = self.calcBackground(start=bgstartVal,end=bgendVal)
        
        #remove background
        self.datablock = self.removeBackground()

        #offset diff
        offsetDiff = timeoffsetVal - self.laseronoff[self.seqnames[0]][0]

        #assemble data 
        datmat = []
        xblock=0
        yrows=0        
        active=False
        
        ys=[]
        xs=[]
        isVert=0
        for s in self.seqnames:
            if s == startSeq: active=True
            if s == endSeq: active=False
            if not active: continue
            ts = self.indexTime(self.laseronoff[s][0]+offsetDiff)
            te = self.indexTime(self.laseronoff[s][1]+offsetDiff)
            if xblock == 0:
                cxblock = self.datablock[1:,ts:te].shape[1]
                xblock=cxblock            
            datmat.append(np.transpose(self.datablock[1:,ts:ts+cxblock]))
            yrows+=1
            if self.xlims[s][0] - self.xlims[s][1] != 0:
                ys.append(self.ylims[s][0])
                #parse x if needed
                if len(xs) == 0:
                    print('N',self.xlims[s][0],self.xlims[s][1],(self.xlims[s][1]-self.xlims[s][0])/(xblock-1))
                    xs=globalfuncs.frange(self.xlims[s][0],end=self.xlims[s][1],inc=(self.xlims[s][1]-self.xlims[s][0])/(xblock-1))
            else:
                isVert=1
                ys.append(self.xlims[s][0])
                #parse x if needed
                if len(xs) == 0:
                    print('V', self.ylims[s][0],self.ylims[s][1],(self.ylims[s][1]-self.ylims[s][0])/(xblock-1))
                    xs=globalfuncs.frange(self.ylims[s][0],end=self.ylims[s][1],inc=(self.ylims[s][1]-self.ylims[s][0])/(xblock-1))
                
        
        print(xblock,yrows)
        print(len(xs),len(ys))
        
        datmat = np.array(datmat)
        print(datmat.shape)
        datmat = np.reshape(datmat,(yrows,xblock,len(self.dataheader[1:])))
        print(datmat.shape)
        dt = np.zeros((yrows,xblock,len(self.dataheader[1:])+2))
        dt[:,:,2:]=datmat

        #add coordinates to dt matrix
        for i in range(len(xs)):
            dt[:,i,1] = np.ones((len(ys)))*xs[i]
        for j in range(len(ys)):
            dt[j,:,0] = np.ones((len(xs)))*ys[j]        
      
        
        self.mapdata = LAMSData(self.fn,self.wd,self.comments)
        self.mapdata.isVert=isVert
        self.mapdata.addLabelData(self.dataheader[1:])
        self.mapdata.addCoordData(xs,ys)        
        
        self.mapdata.finalize(dt)
        print('LAMS done')
        self.complete=True
        self.callback(self)
        
    def killplot(self):
        self.plotter.destroy()
        