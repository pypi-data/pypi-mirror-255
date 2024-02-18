import time
import tkinter

#third party
import Pmw
import numpy as np 
import cv2 as cv

#local
import globalfuncs
from MasterClass import MasterClass

def thresholdfilters(data,filter='TruncMax',level=0.50,value=0.0):
    data=np.array(data,dtype=np.float32)
    dmax=np.max(np.ravel(data))
    inp=np.copy(data)#cv.fromarray(data)
    out=np.copy(data)#cv.fromarray(data)
    inp8=np.copy(data)
    inp8=inp8.astype(np.uint8)
    #cv.Convert(inp,inp8)
    out8=np.copy(data)#np.array(inp.rows,inp.cols,cv.CV_8UC1)
    out8=out8.astype(np.uint8)
    print(level,value)
    print(dmax,level*dmax)
    if filter=='TruncMax':
        ret, out=cv.threshold(inp, level*dmax,level*dmax,cv.THRESH_TRUNC)    
    if filter=='TruncMin':
        ret,out=cv.threshold(inp,level*dmax,value,cv.THRESH_TOZERO)
    #JOY
    if filter=='InvBinary':
        ret,out=cv.threshold(inp,level*dmax,1.0,cv.THRESH_BINARY)  
    if filter=='Otsu':        
        ret,out8= cv.threshold(inp8,level*dmax,255,cv.THRESH_BINARY+cv.THRESH_OTSU) 
    if filter=='Binary':
        ret,out=cv.threshold(inp,level*dmax,1.0,cv.THRESH_BINARY_INV)  
    if filter=='ThreshZero':
        ret,out =cv.threshold(inp,level*dmax,value,cv.THRESH_TOZERO)  
    if filter=='InvThreshZero':
        ret,out =cv.threshold(inp,level*dmax,value,cv.THRESH_TOZERO_INV)  
    if filter=='InvAdapt':
        if value==0: value=11
        out8=cv.adaptiveThreshold(inp8,level*dmax,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY_INV,int(value),0)  
    if filter=='Adapt':
        if value==0: value=11
        out8=cv.adaptiveThreshold(inp8,level*dmax,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,int(value),0)  
    if filter=='Canny':
        m1=min(level,value)
        m2=max(level,value)
        out8= cv.Canny(inp8,m1*dmax,m2*dmax)  
    if filter in ['Canny','InvAdapt','Adapt','Otsu']: 
        out=np.asarray(out8)
    else: 
        out=np.asarray(out)
    return out

class ThresholdingWindowParams:
    def __init__(self, maindisp, status, showmap, savedeconvcalculation):
        self.maindisp =maindisp
        self.status = status
        self.showmap = showmap
        self.savedeconvcalculation = savedeconvcalculation

class ThresholdingWindow(MasterClass):
    def _create(self):
        self.win=Pmw.Dialog(self.imgwin,title="Thresholding",buttons=('Done','Preview','Save'),defaultbutton='Done', command=self.enterThreshFilter)
        h=self.win.interior()
        lf=tkinter.Frame(h,background='#d4d0c8')
        lf.pack(side=tkinter.LEFT,fill='both')
        #data selection
        self.threshsel=Pmw.ScrolledListBox(lf,labelpos='n',label_text='Select Channel',items=self.mapdata.labels,listbox_selectmode=tkinter.SINGLE,
                                              listbox_exportselection=tkinter.FALSE,selectioncommand=self.selectthreshfilterdata,listbox_height=15,
                                           hull_background='#d4d0c8',label_background='#d4d0c8')
        self.threshsel.pack(side=tkinter.TOP,padx=4,pady=5,fill='both')
        #new data name
        self.newthreshfiltername=Pmw.EntryField(lf,labelpos='w',label_text='New Channel Name: ',entry_width=15,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.newthreshfiltername.pack(side=tkinter.TOP,fill=tkinter.X,pady=10)

        #data character
        g1=Pmw.Group(lf,tag_text='Data Properties',hull_background='#d4d0c8',tag_background='#d4d0c8',ring_background='#d4d0c8')
        g1.interior().configure(background='#d4d0c8')
        self.threshDataProps=tkinter.Label(g1.interior(),text="\n\n\n",background='#d4d0c8')
        self.threshDataProps.pack(side=tkinter.TOP,padx=5,pady=4,fill='both')
        g1.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')        

        rf=tkinter.Frame(h,background='#d4d0c8')
        rf.pack(side=tkinter.LEFT,fill='both',padx=5)
        l=tkinter.Label(rf,text='Threshold Parameters',bd=2,relief=tkinter.RAISED,background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill=tkinter.X,expand=1,pady=5)

        #filter type
        g1=Pmw.Group(rf,tag_text='Type',hull_background='#d4d0c8',tag_background='#d4d0c8',ring_background='#d4d0c8')
        g1.interior().configure(background='#d4d0c8')
        self.threshfiltertype=Pmw.RadioSelect(g1.interior(),buttontype='radiobutton',orient='vertical',command=self.selectthreshfilterdata,hull_background='#d4d0c8')
        for text in ('TruncMax','TruncMin','Binary','InvBinary','Otsu','ThreshZero','InvThreshZero','Adapt','InvAdapt','Canny'):
            self.threshfiltertype.add(text,background='#d4d0c8')
        self.threshfiltertype.setvalue('TruncMax')
        self.threshfiltertype.pack(side=tkinter.TOP,padx=3,pady=3)
        g1.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')
        
        #level
        self.threshLevelvar=tkinter.DoubleVar()
        self.threshLevelvar.set(50)
        self.threshLevel=tkinter.Scale(rf,label='Threshold Level (%)',background='#d4d0c8',variable=self.threshLevelvar,width=20,length=150,from_=0,to=100,orient=tkinter.HORIZONTAL,resolution=0.01)
        self.threshLevel.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=10)

        #level
        self.threshLevelvar2=tkinter.DoubleVar()
        self.threshLevelvar2.set(50)
        self.threshLevel2=tkinter.Scale(rf,label='Threshold Level2 (%)',background='#d4d0c8',variable=self.threshLevelvar2,width=20,length=150,from_=0,to=100,orient=tkinter.HORIZONTAL,resolution=0.01,state=tkinter.DISABLED,fg='gray70')
        self.threshLevel2.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=10)

        #value
        self.threshValue=Pmw.EntryField(rf,labelpos='w',label_text='Threshold Value (num): ',entry_width=15,validate='real',value=0,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.threshValue.pack(side=tkinter.TOP,fill=tkinter.X,pady=10)        

        self.win.show()
        self.win.userdeletefunc(func=self.kill)

       

    def selectthreshfilterdata(self,*args):
        if self.threshsel.getvalue()==(): return
        name=self.threshsel.getvalue()[0]
        type='-thresh'
        i=1
        newname=name+type
        while newname in self.mapdata.labels:
            newname=name+type+str(i)
            i+=1
        self.newthreshfiltername.setvalue(newname)

        datind=self.mapdata.labels.index(name)+2
        datmin=float(self.getZoomMax(datind,opt=True))##min(ravel(self.mapdata.data.get(datind)))#[:,:,datind]))
        datmax=float(self.getZoomMax(datind))##max(ravel(self.mapdata.data.get(datind)))#[:,:,datind]))
        datave=float(self.getZoomMax(datind,dsum=True))/float(self.getZoomMax(datind,length=True))
        text='Minimum:\t\t'+str(datmin)+'\nAverage:\t\t'+str(datave)+'\nMaximum:\t\t'+str(datmax)
        globalfuncs.setstatus(self.threshDataProps,text)

        print(self.threshfiltertype.getvalue())
        if self.threshfiltertype.getvalue()=='Canny':
            self.threshLevel.configure(state=tkinter.NORMAL)
            self.threshLevel.configure(fg='black')
            self.threshLevel2.configure(state=tkinter.NORMAL)
            self.threshLevel2.configure(fg='black')
        elif self.threshfiltertype.getvalue()=='Otsu':
            self.threshLevel.configure(state=tkinter.DISABLED)
            self.threshLevel.configure(fg='gray70')
            self.threshLevel2.configure(state=tkinter.DISABLED)
            self.threshLevel2.configure(fg='gray70')
        else:
            self.threshLevel.configure(state=tkinter.NORMAL)
            self.threshLevel.configure(fg='black')
            self.threshLevel2.configure(state=tkinter.DISABLED)
            self.threshLevel2.configure(fg='gray70')
            
    def enterThreshFilter(self,result):
        if result=='Done':
            self.kill() #win.withdraw()
            return
        if len(self.threshsel.getvalue())<1:
            print('Select a data channel')
            return
        if not self.threshValue.valid():
            print('Enter valid threshold value')
            return
        globalfuncs.setstatus(self.ps.status,"THRESHOLDING...")
        t=time.process_time()
        datind=self.mapdata.labels.index(self.threshsel.getvalue()[0])+2
        old=self.mapdata.data.get(datind)#[:,:,datind]
        if self.threshfiltertype.getvalue()=='Canny':
            newd=thresholdfilters(old,filter=self.threshfiltertype.getvalue(),level=self.threshLevelvar.get()/100.,value=self.threshLevelvar2.get()/100.)
        else:
            newd=thresholdfilters(old,filter=self.threshfiltertype.getvalue(),level=self.threshLevelvar.get()/100.,value=float(self.threshValue.getvalue()))
        print("calc: ",time.process_time()-t)
        globalfuncs.setstatus(self.ps.status,"DISPLAYING...")
        self.ps.maindisp.placeData(np.transpose(newd[::-1,:]),np.transpose(self.mapdata.mapindex[::-1,:]),self.ps.status,xax=self.mapdata.xvals,yax=self.mapdata.yvals)
        self.ps.showmap()        
        if result=='Save':
            self.ps.savedeconvcalculation(newd,self.newthreshfiltername.getvalue())
            self.threshsel.setlist(self.mapdata.labels)

    def getZoomMax(self,index,dsum=False,opt=False,length=False):
        tdata=self.mapdata.data.get(index)
        if self.ps.maindisp.zmxyi[2] != -1 and self.ps.maindisp.zmxyi[3] != -1:
            tdata=tdata[::-1,:]
            tdata=tdata[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
            tdata=tdata[::-1,:]
        if dsum:
            return str(sum(np.ravel(tdata)))
        if length:
            return str(len(np.ravel(tdata)))
        if not opt:
            return str(max(np.ravel(tdata)))
        else:
            return str(min(np.ravel(tdata)))

    def kill(self):
        self.exist=0
        self.win.withdraw()
