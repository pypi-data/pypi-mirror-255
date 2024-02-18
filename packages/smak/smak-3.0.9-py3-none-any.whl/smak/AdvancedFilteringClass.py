import math
import time
import tkinter


import cv2 as cv
import numpy as np
import Pmw
import skimage.feature as peak_local_max
import scipy.ndimage as ndimage
import sklearn.metrics.pairwise as sklPairs


import globalfuncs
from MasterClass import MasterClass
import PmwTtkRadioSelect




def advancedfilters(data,filter='Mean',size=3,sigma=0,md=None,FF=0):
        data=np.array(data,dtype=np.float32)
        if filter=='Invert':
            return -data
        usecv=1
        if usecv and filter not in ['Similarity','SimBlur']:
            inp=data
            out=data
            if filter in ['Open','Close','Gradient','TopHat','BlackHat','Max','Min']:
                element=cv.getStructuringElement(cv.MORPH_RECT, (size,size))

            if filter=='FFT':
                cv.dft(inp,out,cv.DFT_ROWS,0)
            if filter=='iFFT':
                cv.dft(inp,out,cv.DFT_ROWS+cv.DFT_INVERSE+cv.DFT_SCALE,0) #5 is inverse and rows...
            if filter=='Mean':          
                out=cv.blur(inp,(size, size))
            if filter=='Median':
                out=cv.medianBlur(inp,size)
            if filter=='Min':
                out=cv.erode(inp,element)
            if filter=='Max':
                out=cv.dilate(inp,element)
            if filter=='Open':
                out=cv.morphologyEx(inp,cv.MORPH_OPEN, element)
            if filter=='Close':
                out=cv.morphologyEx(inp,cv.MORPH_CLOSE, element)
            if filter=='Gradient':
                out=cv.morphologyEx(inp,cv.MORPH_GRADIENT, element)
            if filter=='TopHat':
                out=cv.morphologyEx(inp,cv.MORPH_TOPHAT, element)
            if filter=='BlackHat':
                out=cv.morphologyEx(inp,cv.MORPH_BLACKHAT, element)
            if filter=='Denoise':
                maxval=np.max(np.ravel(data))
                inp=data / maxval * 255
                inp=np.uint8(inp)
                out=np.uint8(inp)
                cv.fastNlMeansDenoising(inp,out,sigma,7,21)
                out=np.float32(out)*maxval/255
            if filter=='Blur':
                #cv.Smooth(inp,out,smoothtype=cv.CV_GAUSSIAN,param1=size,param2=size,param3=sigma)
                out=cv.GaussianBlur(inp,(size, size),sigma)

            if filter=='EDT':
                out=ndimage.distance_transform_edt(data)
                localMax=peak_local_max(out,min_distance=int(size))
                print(len(localMax))
            if filter=='MeanShift':
                ds=list(data.shape)
                ds.extend([3])
                d2=np.zeros(ds,dtype="uint8")
                print(data.shape,d2.shape,ds)
                d2[:,:,0]=data/np.max(data)*255
                d2[:,:,1]=data/np.max(data)*255
                d2[:,:,2]=data/np.max(data)*255
                o2=np.zeros(ds,dtype="uint8")
                inp=d2
                out=o2
                out=cv.pyrMeanShiftFiltering(inp,size,size)
                out=np.asarray(out)
                out=out[:,:,0]
            out=np.asarray(out)
            return out
        else:  #manual convolve...
            
            sh=int(int(size)/2)
            (xlen,ylen)=data.shape
            newdata=np.zeros((xlen,ylen),dtype=np.float32)
            #expand original data...
            xdata=padforconvolve(data,sh)
            (nmdx,nmdy)=xdata.shape
            mdata=np.zeros((nmdx,nmdy,md.shape[2]),dtype=np.float32)     
            for k in range(md.shape[2]):
                mdata[:,:,k]=padforconvolve(md[:,:,k],sh)        
            
            for i in range(xlen):
                for j in range(ylen):
                    newdata[i,j]=subadvancedfilter(xdata[i:i+2*sh+1,j:j+2*sh+1],mdata[i:i+2*sh+1,j:j+2*sh+1,:],size,sigma,filter,FF=FF)
            return newdata    

def subadvancedfilter(data,md,sh,sig,filter,FF=0):
    #t=np.ravel(data)
    tm=md.reshape(-1,md.shape[2])

    #pairCorMat=sklPairs.cosine_similarity(tm)
    pairCorMat=sklPairs.additive_chi2_kernel(tm)/10.**FF
    pairCorMat=np.exp(pairCorMat)
    
    magic=int(math.floor(sh/2.))
    if filter=='Similarity':
        return sum(pairCorMat[magic])/len(pairCorMat[magic])
        
    #corm=pairCorMat[magic].reshape([sh,sh])
    corm=np.ones([sh,sh],dtype=np.float32)*(sum(pairCorMat[magic])/len(pairCorMat[magic]))
    corm[sh//2,sh//2]=1.
    
    gauss=gausskern(l=sh,sig=sig)
    gn=sum(np.ravel(gauss))
    new=corm * gauss * data

    return sum(np.ravel(new))/gn
    
def gausskern(l=5, sig=1.):
    """
    creates gaussian kernel with side length l and a sigma of sig
    """

    ax=np.arange(-l // 2 + 1., l // 2 + 1.)
    xx, yy=np.meshgrid(ax, ax)

    kernel=np.exp(-(xx**2 + yy**2) / (2. * sig**2))

    return kernel / np.sum(kernel)

def padforconvolve(data,sh):
    (xlen,ylen)=data.shape
    nxl=xlen+2*sh
    nyl=ylen+2*sh
    newdata=np.zeros((nxl,nyl),dtype=np.float32)
    for i in range(nxl):
        if i>=sh and i<=xlen-1:
            newl=makenewpadline(data[i-sh,:],nyl,sh)  
        elif i<sh:
            newl=makenewpadline(data[0,:],nyl,sh)  
        else:
            newl=makenewpadline(data[xlen-1,:],nyl,sh)
        newdata[i,:]=newl
    return newdata

def makenewpadline(data,newy,sh):
    newl=np.zeros(newy,dtype=np.float32)
    ylen=len(data)
    for j in range(newy):
        if j<sh:
            newl[j]=data[0]
        elif j>ylen-1:
            newl[j]=data[ylen-1]
        else:
            newl[j]=data[j-sh]
    return newl


class AdvancedFilteringWindowParams:
    def __init__(self, status, maindisp, showmap, savedeconvcalculation):
        self.status = status
        self.maindisp = maindisp
        self.showmap = showmap
        self.savedeconvcalculation = savedeconvcalculation

class AdvancedFilteringWindow(MasterClass):
    def _create(self):
        # self.imgwin=imgwin
        # self.mapdata = mapdata 
        # self.ps = ps
        self.win=Pmw.Dialog(self.imgwin,title="Advanced Filtering",buttons=('Preview','Save','Done'),defaultbutton='Done',
                                     command=self.enterAdvFilter)
        h=self.win.interior()
        h.configure(background='#d4d0c8')
        lf=tkinter.Frame(h,background='#d4d0c8')
        lf.pack(side=tkinter.LEFT,fill='both')
        #data selection
        self.advfiltersel=Pmw.ScrolledListBox(lf,labelpos='n',label_text='Select Channel',items=self.mapdata.labels,listbox_selectmode=tkinter.EXTENDED,
                                              listbox_exportselection=tkinter.FALSE,selectioncommand=self.selectadvfilterdata,listbox_height=15)
        self.advfiltersel.pack(side=tkinter.TOP,padx=4,pady=5,fill='both')
        #new data name

        rf=tkinter.Frame(h,background='#d4d0c8')
        rf.pack(side=tkinter.LEFT,fill='both',padx=5)
        l=tkinter.Label(rf,text='Filter Parameters',bd=2,relief=tkinter.RAISED,background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill=tkinter.X,expand=1,pady=5)

        #filter type
        g1=Pmw.Group(rf,tag_text='Type',hull_background='#d4d0c8',tag_background='#d4d0c8',ring_background='#d4d0c8')
        g1.interior().configure(background='#d4d0c8')
        g1f1=tkinter.Frame(g1.interior(),background='#d4d0c8')
        g1f1.pack(side=tkinter.LEFT,padx=3)
        g1f3=tkinter.Frame(g1.interior(),background='#d4d0c8')
        g1f3.pack(side=tkinter.LEFT,padx=3)
        g1f2=tkinter.Frame(g1.interior(),background='#d4d0c8')
        g1f2.pack(side=tkinter.LEFT,padx=3)
        self.advfiltertype1=PmwTtkRadioSelect.PmwTtkRadioSelect(g1f1,buttontype='button',orient='vertical',command=self.selectadvfilterdata1,selectmode='single',hull_background='#d4d0c8')
        for text in ('Mean','Median','Min','Max','Invert'):
            self.advfiltertype1.add(text)
        self.advfiltertype3=PmwTtkRadioSelect.PmwTtkRadioSelect(g1f3,buttontype='button',orient='vertical',command=self.selectadvfilterdata3,selectmode='single',hull_background='#d4d0c8')
        for text in ('Blur','MeanShift','EDT','Unsharp','Denoise','Similarity','SimBlur'):
            self.advfiltertype3.add(text)
        self.advfiltertype2=PmwTtkRadioSelect.PmwTtkRadioSelect(g1f2,buttontype='button',orient='vertical',command=self.selectadvfilterdata2,selectmode='single',hull_background='#d4d0c8')
        for text in ('Open','Close','Gradient','TopHat','BlackHat','FFT','iFFT'):
            self.advfiltertype2.add(text)

        self.advfiltertype1.setvalue('Mean')
        self.advfiltertype1.pack(side=tkinter.TOP,padx=3,pady=3)
        #self.advfiltertype2.setvalue([])
        self.advfiltertype3.pack(side=tkinter.TOP,padx=3,pady=3)
        self.advfiltertype2.pack(side=tkinter.TOP,padx=3,pady=3)
        g1.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')
        
        #filter size
        self.advfilterFSvar=tkinter.IntVar()
        self.advfilterFSvar.set(3)
        self.advfilterFS=tkinter.Scale(rf,label='Filter Size',background='#d4d0c8',variable=self.advfilterFSvar,width=20,length=150,from_=3,to=31,orient=tkinter.HORIZONTAL,resolution=1)
        self.advfilterFS.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=10)

        g1=Pmw.Group(rf,tag_text='Blur/Unsharp Parameters',hull_background='#d4d0c8',tag_background='#d4d0c8',ring_background='#d4d0c8')
        g1.interior().configure(background='#d4d0c8')

        #Sdev of blurs
        self.advfilterSDvar=tkinter.DoubleVar()
        self.advfilterSDvar.set(1.0)
        self.advfilterSD=tkinter.Scale(g1.interior(),label='Blur St. Dev.',background='#d4d0c8',variable=self.advfilterSDvar,width=20,length=150,from_=0.25,to=5,orient=tkinter.HORIZONTAL,resolution=.05,state=tkinter.DISABLED,fg='gray70')
        self.advfilterSD.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=10)        
        
        #filter frac
        self.advfilterFFvar=tkinter.DoubleVar()
        self.advfilterFFvar.set(0.5)
        self.advfilterFF=tkinter.Scale(g1.interior(),label='Unsharp/Sim Strength',background='#d4d0c8',variable=self.advfilterFFvar,width=20,length=150,from_=0,to=1,orient=tkinter.HORIZONTAL,resolution=.01,state=tkinter.DISABLED,fg='gray70')
        self.advfilterFF.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=10)
        g1.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')        

        self.win.userdeletefunc(func=self.kill)

        self.win.show()


    def enterAdvFilter(self,result):
        calcerr=False
        typd={'Mean':'-avg','Median':'-med','Min':'-min','Max':'-max','Invert':'-inv','Blur':'-blur','Unsharp':'-shrp','Denoise':'-den','Open':'-open','Close':'-close','Gradient':'-grad','TopHat':'-toph','BlackHat':'-blackh','FFT':'-fft','iFFT':'-ifft','Similarity':'-sim','SimBlur':'-sblr','MeanShift':'-ms','EDT':'-edt'}          
        if result=='Done':
            self.win.withdraw()
            return
        if len(self.advfiltersel.getvalue())<1:
            print('Select a data channel')
            return
        globalfuncs.setstatus(self.ps.status,"FILTERING...")
        if self.advfiltertypegetvalue() in ['Similarity']: 
            itset=[self.advfiltersel.getvalue()[0]]
        else:
            itset=self.advfiltersel.getvalue()
        print(self.advfiltersel.getvalue(),itset)
        for fd in itset:
            t=time.process_time()
            datind=self.mapdata.labels.index(fd)+2
            old=self.mapdata.data.get(datind)#[:,:,datind]
    
            if not self.advfilterFSvar.get()%2:
                self.advfilterFSvar.set(self.advfilterFSvar.get()-1)
    
            if self.advfiltertypegetvalue() in ['Blur','Unsharp']:
                #psf=Deconv.fspecial(self.advfilterFSvar.get(),self.advfilterSDvar.get())
                #newd=filterconvolve(old,psf)
                newd=advancedfilters(old,filter='Blur',size=self.advfilterFSvar.get(),sigma=self.advfilterSDvar.get())
                if self.advfiltertypegetvalue()=='Unsharp':
                    temp=old-newd*self.advfilterFF.get()
                    #rescale
                    newd=temp/(1-self.advfilterFF.get())
            elif self.advfiltertypegetvalue() in ['Similarity','SimBlur']:
                if len(self.advfiltersel.getvalue())<2:
                    newd=old
                    print("Select more than one channel for similarities")
                    calcerr=True
                else:
                    indicies=[]
                    for n2i in self.advfiltersel.getvalue():
                        indicies.append(self.mapdata.labels.index(n2i)+2)
                    md=self.mapdata.data.get(indicies)
                    newd=advancedfilters(old,filter=self.advfiltertypegetvalue(),size=self.advfilterFSvar.get(),sigma=self.advfilterSDvar.get(),md=md,FF=self.advfilterFF.get())
            elif self.advfiltertypegetvalue() in ['Denoise']:
                newd=advancedfilters(old,filter='Denoise',size=self.advfilterFSvar.get(),sigma=self.advfilterSDvar.get())
            else:
                newd=advancedfilters(old,filter=self.advfiltertypegetvalue(),size=self.advfilterFSvar.get())
            print("calc: ",time.process_time()-t)
            globalfuncs.setstatus(self.ps.status,"DISPLAYING...")
            self.ps.maindisp.placeData(np.transpose(newd[::-1,:]),np.transpose(self.mapdata.mapindex[::-1,:]),self.ps.status,xax=self.mapdata.xvals,yax=self.mapdata.yvals)
            self.ps.showmap()        
            if result=='Save' and calcerr==False:
                print(self.advfiltertypegetvalue())
                svtype=typd[self.advfiltertypegetvalue()]
                i=1
                newname=fd+svtype
                while newname in self.mapdata.labels:
                    newname=fd+svtype+str(i)
                    i+=1
                self.ps.savedeconvcalculation(newd,newname)
        if result=='Save':
            self.advfiltersel.setlist(self.mapdata.labels)

    def selectadvfilterdata1(self,*args):
        self.advfiltertype2.setvalue([])
        self.advfiltertype3.setvalue([])
        self.selectadvfilterdata()
        
    def selectadvfilterdata2(self,*args):
        self.advfiltertype1.setvalue([])
        self.advfiltertype3.setvalue([])
        self.selectadvfilterdata()
        
    def selectadvfilterdata3(self,*args):
        self.advfiltertype2.setvalue([])
        self.advfiltertype1.setvalue([])
        self.selectadvfilterdata()


    def selectadvfilterdata(self,*args):
        typd={'Mean':'-avg','Median':'-med','Min':'-min','Max':'-max','Invert':'-inv','Blur':'-blur','Unsharp':'-shrp','Denoise':'-den','Open':'-open','Close':'-close','Gradient':'-grad','TopHat':'-toph','BlackHat':'-blackh','FFT':'-fft','iFFT':'-ifft','Similarity':'-sim','SimBlur':'-sblr','MeanShift':'-ms','EDT':'-edt'}          
        if self.advfiltertypegetvalue() in ['Unsharp']:
            self.advfilterFF.configure(to='1')
            self.advfilterFF.configure(state=tkinter.NORMAL)
            self.advfilterFF.configure(fg='black')
        elif self.advfiltertypegetvalue() in ['SimBlur','Similarity']:
            self.advfilterFF.configure(to='6')
            self.advfilterFF.configure(state=tkinter.NORMAL)
            self.advfilterFF.configure(fg='black')
        else:
            self.advfilterFF.configure(state=tkinter.DISABLED)
            self.advfilterFF.configure(fg='gray70')
            self.advfilterSD.configure(state=tkinter.DISABLED)
            self.advfilterSD.configure(fg='gray70')            
        if self.advfiltertypegetvalue() in ['Blur','Unsharp','SimBlur']:
            self.advfilterSD.configure(state=tkinter.NORMAL)
            self.advfilterSD.configure(fg='black')  
            self.advfilterSD.configure(to='5')
        if self.advfiltertypegetvalue() in ['Denoise']:
            self.advfilterSD.configure(state=tkinter.NORMAL)
            self.advfilterSD.configure(fg='black')      
            self.advfilterSD.configure(to='20')
        if self.advfiltersel.getvalue()==(): return

    def advfiltertypegetvalue(self):
        if self.advfiltertype1.getvalue() in ('Mean','Median','Min','Max','Invert'):
            return self.advfiltertype1.getvalue()
        elif self.advfiltertype3.getvalue() in ('Blur','Unsharp','Similarity','SimBlur','Denoise','EDT','MeanShift'):
            return self.advfiltertype3.getvalue()
        else:
            return self.advfiltertype2.getvalue()

    def kill(self):
        self.win.withdraw()
        self.exist=0




    