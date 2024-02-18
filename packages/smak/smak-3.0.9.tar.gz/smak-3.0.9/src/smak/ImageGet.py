"""
used time.perf_counter() insteack of time.clock()
replaced/modified some text encodings
upper/lower etc
"""

#standard libraries
import importlib.util
import io
import json
import math
import os.path
import shutil
import string
import struct
import time
import zipfile



#third party libraries
import envilite.envi as envi
import fabio
import h5py
import numpy as np
import packaging.version as VRS
from PIL import Image as MainImage
import Pmw
import read_agilent
from scipy import ndimage
import sortedcontainers
import tkinter
import tkinter.messagebox


#local imports
import globalfuncs

MainImage.MAX_IMAGE_PIXELS=None


#check pyimzml
if importlib.util.find_spec("pyimzml") is not None:
    print ('loading pyimzml')
    from pyimzml.ImzMLParser import ImzMLParser
    import pyimzml
    pyimzmlInstalled=True
else:
    pyimzmlInstalled=False

#check opusFC
if importlib.util.find_spec("opusFC") is not None:
    print ('loading opus')
    import opusFC
    opusInstalled=True
else:
    opusInstalled=False
    
hdf5_version = h5py.version.hdf5_version_tuple[0:3]    
if VRS.Version(h5py.__version__)>=VRS.parse("3.5.0") and not (hdf5_version < (1, 12, 1) and (
                hdf5_version[:2] != (1, 10) or hdf5_version[2] < 7)):
    HD5OPT={'locking':False}
    print ('using unlocked hdf5')
else:
    HD5OPT={}


def isnumberlist(list):
    for a in list:
        try: int(a)
        except: return 0
    return 1

def skipline(f,n):
    text=''
    for i in range(n):
        text=text+f.readline()
    return text

def bytesize(a):
    return int(4*math.ceil(float(a)/4))


############# Spiral Indicies for MASSBOX?

def spiral_cw(A):
    A = np.array(A)
    out = []
    while(A.size):
        out.append(A[0])        # take first row
        A = A[1:].T[::-1]       # cut off first row and rotate counterclockwise
    return np.concatenate(out)

def base_spiral(nrow, ncol):
    return spiral_cw(np.arange(nrow*ncol).reshape(nrow,ncol))

def to_spiral(A):
    A = np.array(A)
    B = np.empty_like(A)
    B.flat[base_spiral(*A.shape)] = A.flat
    return B

################



class HDF5get():

    def __init__(self,hdf5):
        self.hdf5=hdf5
        self.calcShape()

    def get(self,index):
        return np.array(self.hdf5[:,:,index])

    def getPix(self,i,j):
        return np.array(self.hdf5[i,j,:])
        
    def getRow(self,index,i):
        return np.array(self.hdf5[i,:,index])
        
    def calcShape(self):
        self.shape=self.hdf5.shape
        return self.shape

    def put(self,index,data):
        self.hdf5[:,:,index]=data

    def putRow(self,index,i,data):
        self.hdf5[i,:,index]=data

    def putPixel(self,indList,value):
        self.hdf5[indList[0],indList[1],indList[2]]=value

    def addChannel(self,data):
        cur=self.shape[2]
        self.hdf5.resize(self.shape[2]+1,axis=2)
        self.put(cur,data)
        self.calcShape()

    def removeChannel(self,index):
        #skip ahead to channel we need to remove...
        #copy the next row+1 into row
        #resize smaller
        for i in range(self.shape[2]):
            if i>index: self.hdf5[:,:,i-1]=self.hdf5[:,:,i]
        self.hdf5.resize(self.shape[2]-1,axis=2)
        self.calcShape()


class SuperClass:
    def __init__(self):
        self.hdf5=None

    def cleanString(self):
        try:
            self.type=self.type.decode()
        except:
            print("type ok")
        try:
            #self.isVert= self.isVert.decode()
            self.comments=self.comments.decode()
        except:
            print("comments ok")
        try:
            newlabels=[]
            for label in self.labels:
                newlabels.append(label.decode())
            self.labels=newlabels
        except:
            print("labels ok")




####################################
## HDF5 format
####################################   

class EmptyHDF5(SuperClass):
    
    def __init__(self,fn):
        
        self.hdf5=h5py.File(fn,'w', **HD5OPT)

        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        
    def close(self):
        self.hdf5.close()
        
    def addParams(self,xv,yv,pdict):
        self.xvals=xv
        self.yvals=yv
        self.nxpts=len(xv)
        self.nypts=len(yv)
        self.channels=pdict['channels']
        self.type=pdict['type']
        self.isVert=pdict['isVert']
        self.labels=pdict['labels']
        self.comments=pdict['comments']
        self.energy=pdict['energy']
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
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



class HDF5load(SuperClass):

    def __init__(self,fn,temp,wd):
        

        hdf5=h5py.File(fn)       

        if  "/mono_0/scalar_0" in hdf5 and "/mono_0/vortex_0" in hdf5:
            self.type="CLS-BIOXAS_HDFb"
            print ("CLS-BIOXAS-B")
            
            self.isVert=0
            self.energy=str(1.23)
            
            sroot="/"
            sdpath=sroot+"mono_0"
            #sppath=sroot+"/Support"
        
            #have scalars_0-4 and vortex_0-4 
            self.labels=['scalar_0','scalar_1','scalar_2','scalar_3','scalar_4']
            for j in list(hdf5[sdpath+'/vortex_0_meta'].keys()):
                self.labels.append(str(j))
            self.channels=len(self.labels) 
            self.comments="None in file"
            print((self.labels))
            
            #axes
            (ylen,xlen)=hdf5[sdpath+"/scalar_0/before"][()].shape
            xpositions=list(range(xlen)) #hdf5[sppath+"/cols"][()]
            ypositions=list(range(ylen)) #hdf5[sppath+"/rows"][()]
            start1=xpositions[0]
            start2=ypositions[0]
            stop1=xpositions[-1]
            stop2=ypositions[-1]
            step1=(stop1-start1)/(len(xpositions)-1)
            step2=(stop2-start2)/(len(ypositions)-1)
            
            print((start1,stop1,step1))
            print((start2,stop2,step2)) 
            
            self.xvals=xpositions
            self.yvals=ypositions
            self.nxpts=len(self.xvals)
            self.nypts=len(self.yvals)

            mdfile=''
            if tkinter.messagebox.askyesno(title="Load CLS Data",message="Is there a metadata file?"):
                atmeta = os.path.splitext(fn)[0][-5:]
                fty=[("meta files","*.meta"),("all files","*")]
                mdfile=globalfuncs.ask_for_file(fty,"",multi=False)
            if mdfile!='':
                fim = open(mdfile)
                tdata = fim.read()
                fim.close()
                mdata = json.loads(tdata)
                
                if type(mdata['key:meta']['key:mono_energies']) == list:
                    #multiples?
                    self.energy = float(mdata['key:meta']['key:mono_energies'][0])
                    numE=len(mdata['key:meta']['key:mono_energies'])
                else:
                    self.energy = float(mdata['key:meta']['key:mono_energies'])
                    numE=1

                self.labels=[]     
                plabels=[]
                if numE>1:
                    mE=0
                    for ie in range(numE):
                        if  "/mono_"+str(ie) in hdf5: 
                            mE+=1
                        else: break
                    if mE>1:
                        for ce in range(mE):
                            etext = mdata['key:meta']['key:mono_energies'][ce]
                
                            for j in mdata['key:meta']['key:scalar:chan:list']:
                                self.labels.append(mdata['key:meta']['key:scalar:chan:devices'][str(j)]+"_"+str(etext))
                                if ce==0: plabels.append('scalar_'+str(j))
                            for j in list(hdf5[sdpath+'/vortex_0_meta'].keys()):
                                self.labels.append(str(j)+"_"+str(etext))    
                                if ce==0: plabels.append(str(j)) 
                
                    else:                
                        for j in mdata['key:meta']['key:scalar:chan:list']:
                            self.labels.append(mdata['key:meta']['key:scalar:chan:devices'][str(j)])
                        for j in list(hdf5[sdpath+'/vortex_0_meta'].keys()):
                            self.labels.append(str(j))   
                        plabels = self.labels
                else:
                    mE=1

                self.channels=len(self.labels) 
                self.comments=mdata['key:meta']['key:scan:notes']
                print((self.labels))
                
                xpositions=np.array(list(range(xlen)))*float(mdata['key:meta']['key:scan:cfg']['var:flyscan:cfg:resolution_h']) #hdf5[sppath+"/cols"][()]
                ypositions=np.array(list(range(ylen)))*float(mdata['key:meta']['key:scan:cfg']['var:flyscan:cfg:resolution_v'])
                xpositions+=float(mdata['key:meta']['key:scan:cfg']['var:flyscan:cfg:bottom'])
                ypositions+=float(mdata['key:meta']['key:scan:cfg']['var:flyscan:cfg:left'])
                start1=xpositions[0]
                start2=ypositions[0]
                stop1=xpositions[-1]
                stop2=ypositions[-1]
                step1=(stop1-start1)/(len(xpositions)-1)
                step2=(stop2-start2)/(len(ypositions)-1)
                
                print((start1,stop1,step1))
                print((start2,stop2,step2)) 
                
                self.xvals=xpositions
                self.yvals=ypositions
                self.nxpts=len(self.xvals)
                self.nypts=len(self.yvals)
            else:
                mE=1
                plabels=self.labels

            dtshaped=[len(xpositions),len(ypositions),len(self.labels)+2]
            dt=np.zeros(tuple(dtshaped),dtype=np.float32)
            
            ind=2
            for mnum in range(mE):
                sdpath=sroot+"mono_"+str(mnum)
                print (sdpath)
                for l in plabels[0:5]:  #scalers
                    print(sdpath+"/"+l+"/before")
                    dt[:,:,ind]=np.reshape(np.ravel(hdf5[sdpath+"/"+l+"/before"][()]),(len(xpositions),len(ypositions)))
                    ind+=1
    
                for l in plabels[5:]: #vortex
                    vtemp=np.zeros((len(xpositions),len(ypositions)),dtype=np.float32)
                    for vind in range(16):
                        if sdpath+"/vortex_"+str(vind)+"_meta" in hdf5:
                            vtemp+=np.reshape(np.ravel(hdf5[sdpath+"/vortex_"+str(vind)+"_meta/"+l][()]),(len(xpositions),len(ypositions)))
                    dt[:,:,ind]=vtemp
                    ind+=1    


            #add coordinates to dt matrix
            for i in range(self.nxpts):
                dt[i,:,1]=np.ones((self.nypts))*self.xvals[i]
            for j in range(self.nypts):
                dt[:,j,0]=np.ones((self.nxpts))*self.yvals[j]                

            #extract MCA data
            for mnum in range(mE):
                if mdfile!='':
                    etext = '_'+str(mdata['key:meta']['key:mono_energies'][mnum])
                else:
                    etext =''
                
                fnout=os.path.splitext(fn)[0]+etext+"_mca.hdf5"
                if wd[0]!='':
                    fnout=os.path.join(wd[0],os.path.splitext(os.path.split(fn)[1])[0]+"_"+etext+"_mca.hdf5")
                
                print (fnout)      
                sdpath=sroot+"mono_"+str(mnum)
                print (sdpath)
                
                if not os.path.exists(fnout):
                    fout=h5py.File(fnout,'w')
                    groupout=fout.create_group("main")
            
                    rawmcadata=hdf5[sdpath+"/vortex_sum"][()]
                    
                    #for n in range(16):
                    #    if sdpath+"/vortex_"+str(n+1) in hdf5:
                    #       rawmcadata+=hdf5[sdpath+"/vortex_"+str(n+1)][()]
                        
                    print((rawmcadata.shape,np.max(rawmcadata)))
                    maxpoints=rawmcadata.shape[0]*rawmcadata.shape[1]
                    maxlen=min(rawmcadata.shape[2],2048)
                    mcadata=groupout.create_dataset("mcadata",(maxpoints,maxlen),maxshape=(None,maxlen),dtype='float',compression="gzip",compression_opts=4)
                    
                    print ("reorg")
                    rawmcadata=rawmcadata[:,:,:maxlen]
                    rawmcadata=np.reshape(rawmcadata,(maxpoints,maxlen)) 
                    i=0
                    cb=100
                    while i<maxpoints:
                        if i+cb<maxpoints:
                            mcadata[i:i+cb,:]=rawmcadata[i:i+cb,:]
                            i+=cb
                        else:
                            mcadata[i:,:]=rawmcadata[i:,:]
                            i=maxpoints+1
                    #mcadata=rawmcadata.copy()
                    #print np.max(mcadata)
                    #a=np.sum(mcadata,axis=1)
                    #print np.max(a),np.where(a==np.max(a))
                    #for j in range(self.nypts):
                    #    for i in range(self.nxpts):
                    #        mcadata[i+j*rawmcadata.shape[1]]=rawmcadata[j,i,:]
            
                    fout.flush() 
                    fout.close()
                    print ('mcadone')
                else:
                    rawmcadata=hdf5[sdpath+"/vortex_sum"][()]
                    print((np.max(rawmcadata)))
                    for n in range(16):
                        if sdpath+"/vortex_"+str(n) in hdf5:
                           rawmcadata=hdf5[sdpath+"/vortex_"+str(n)][()]
                           print((n,np.max(rawmcadata)))
        
        elif "/Data/Support/" in hdf5 and "/Data/Mono_Energy_0/Full/mca" in hdf5 and "/Data/Mono_Energy_0/Full/vortex_0" in hdf5:
            self.type="CLS-BIOXAS_HDF"
            print ("CLS-BIOXAS")
            
            self.isVert=0
            self.energy=str(hdf5['Data/Support/mono_energies'][:][0])
            
            sroot=list(hdf5.keys())[0]
            sdpath=sroot+"/Mono_Energy_0/Full"
            sppath=sroot+"/Support"
            
            #have scalars_0-4 and vortex_0-4 
            self.labels=['scalar_0','scalar_1','scalar_2','scalar_3','scalar_4']
            self.channels=len(self.labels) 
            self.comments="None in file"
            
            #axes
            xpositions=hdf5[sppath+"/cols"][()]
            ypositions=hdf5[sppath+"/rows"][()]
            start1=xpositions[0]
            start2=ypositions[0]
            stop1=xpositions[-1]
            stop2=ypositions[-1]
            step1=(stop1-start1)/(len(xpositions)-1)
            step2=(stop2-start2)/(len(ypositions)-1)
            
            print((start1,stop1,step1))
            print((start2,stop2,step2)) 
            
            self.xvals=xpositions
            self.yvals=ypositions
            self.nxpts=len(self.xvals)
            self.nypts=len(self.yvals)
            
            dtshaped=[len(ypositions),len(xpositions),len(self.labels)+2]
            dt=np.zeros(tuple(dtshaped),dtype=np.float32)
            
            ind=2
            for l in self.labels:
                dt[:,:,ind]=hdf5[sdpath+"/"+l][()]
                ind+=1

            #add coordinates to dt matrix
            for i in range(self.nxpts):
                dt[:,i,1]=np.ones((self.nypts))*self.xvals[i]
            for j in range(self.nypts):
                dt[j,:,0]=np.ones((self.nxpts))*self.yvals[j]                

            #extract MCA data
            fnout=os.path.splitext(fn)[0]+"_mca.hdf5"
            if wd[0]!='':
                fnout=os.path.join(wd[0],os.path.splitext(os.path.split(fn)[1])[0]+"_mca.hdf5")
            
            print (fnout)        
            if not os.path.exists(fnout):
                fout=h5py.File(fnout,'w')
                groupout=fout.create_group("main")
        
                rawmcadata=hdf5[sdpath+"/vortex_0"][()]
                for n in range(4):
                    rawmcadata+=hdf5[sdpath+"/vortex_"+str(n+1)][()]
                    
                print((rawmcadata.shape))
                maxpoints=rawmcadata.shape[0]*rawmcadata.shape[1]
                mcadata=groupout.create_dataset("mcadata",(maxpoints,rawmcadata.shape[2]),maxshape=(None,rawmcadata.shape[2]),dtype='int',compression="gzip",compression_opts=4)
                
                for j in range(self.nypts):
                    for i in range(self.nxpts):
                        mcadata[i+j*rawmcadata.shape[1]]=rawmcadata[j,i,:]
        
                fout.flush() 
                fout.close()

        elif list(hdf5.keys())[0]+"-norm" in hdf5:
            self.type="BRAZIL_HDF"        

            self.isVert=0
            self.energy='1'            

            sroot=list(hdf5.keys())[0]
    
            sdpath=sroot+"-norm"
    
            #get scalar data
            labels=["sum"]
            #transfer data
                    
            self.labels=labels
            self.channels=len(self.labels)      
            comments="None in file"
            self.comments=comments
                
                
                
            xpositions= hdf5[sdpath+"/sxpos"]   
            ypositions= hdf5[sdpath+"/szpos"]
            
            print((xpositions.shape))
            
            start1= np.average(xpositions[:,0])
            start2= np.average(ypositions[0,:])
            stop1= np.average(xpositions[:,xpositions.shape[1]-1])
            stop2= np.average(ypositions[ypositions.shape[0]-1,:])
            step1=(stop1-start1)/(xpositions.shape[1]-1)
            step2=(stop2-start2)/(ypositions.shape[0]-1)
            
            print((start1,stop1,step1))
            print((start2,stop2,step2))
            
            dtshaped=list(xpositions.shape)
            dtshaped.extend([self.channels+2])
            dt=np.zeros(tuple(dtshaped),dtype=np.float32)        
            
            ind=2
            #JOY Q
            for l in labels:
                for n in readiter:
                    sfitdata=hdf5[sdpath+"/"+l+n][()]
                    print((l,n,sfitdata.shape))
                
                    dt[:,:,ind]+=sfitdata
                ind+=1
    
            if start1>stop1 and step1>0: step1=-step1
            if start1<stop1 and step1<0: step1=-step1
            if start2>stop2 and step2>0: step2=-step2    
            if start2<stop2 and step2<0: step2=-step2    
    
            self.xvals=globalfuncs.frange(start1,end=stop1,inc=step1)
            self.yvals=globalfuncs.frange(start2,end=stop2,inc=step2)
            
            if len(self.xvals)>dtshaped[1]:self.xvals=self.xvals[:-1]        
            if len(self.yvals)>dtshaped[0]:self.yvals=self.yvals[:-1]        
    
            print ("WARNING! FORCING X ARRAYS TO FIT.")        
            if len(self.xvals)!=dtshaped[1]: self.xvals=self.xvals[:dtshaped[1]]
            print ("WARNING! FORCING Y ARRAYS TO FIT.")        
            if len(self.yvals)!=dtshaped[0]: self.yvals=self.yvals[:dtshaped[0]]
            
            
            self.nxpts=len(self.xvals)
            self.nypts=len(self.yvals)
            
            print((self.nxpts,self.nypts))
    
            #add coordinates to dt matrix
            for i in range(self.nxpts):
                dt[:,i,1]=np.ones((self.nypts))*self.xvals[i]
            for j in range(self.nypts):
                dt[j,:,0]=np.ones((self.nxpts))*self.yvals[j]
    
    
            #extract MCA data
            fnout=os.path.splitext(fn)[0]+"_mca.hdf5"
            
            print (fnout)        
            if not os.path.exists(fnout):
                fout=h5py.File(wd[0]+fnout,'w')
                groupout=fout.create_group("main")
        
                rawmcadata=hdf5[sdpath+"/channel00"][()]
                
                print((rawmcadata.shape))
                maxpoints=rawmcadata.shape[0]*rawmcadata.shape[1]
                mcadata=groupout.create_dataset("mcadata",(maxpoints,rawmcadata.shape[2]),maxshape=(None,rawmcadata.shape[2]),dtype='int',compression="gzip",compression_opts=4)
                
                for j in range(self.nypts):
                    for i in range(self.nxpts):
                        mcadata[i+j*rawmcadata.shape[1]]=rawmcadata[j,i,:]
        
                fout.flush() 
                fout.close()
            
            
        elif "/2D Scan/Detectors/" in hdf5 and str(hdf5["/2D Scan"].attrs.get("Header")).startswith("# 2-D Scan File"):
            self.type="APSPNC_HDF"  
            print ("2D PNC")

            self.isVert=0
            self.energy='1'

            #transfer data
            labels=hdf5["/2D Scan/Detectors/"].attrs.get("Detector Names")
            self.labels=list(labels[:])
            self.channels=len(self.labels)
            
            comments=str(hdf5["/2D Scan"].attrs.get("Header"))
            self.comments=comments 
                
            start1=hdf5["/2D Scan/X Positions"][0,0]
            start2=hdf5["/2D Scan/Y Positions"][0,0]
            stop1=hdf5["/2D Scan/X Positions"][0,-1]
            stop2=hdf5["/2D Scan/Y Positions"][0,-1]
            step1=hdf5["/2D Scan/X Positions"][0,0]-hdf5["/2D Scan/X Positions"][0,1]
            step2=hdf5["/2D Scan/Y Positions"][0,0]-hdf5["/2D Scan/Y Positions"][0,1]
            
            dtshaped=list(hdf5["/2D Scan/Detectors/"].shape)
            dtshaped[2]=dtshaped[2]+2
            dt=np.zeros(tuple(dtshaped),dtype=np.float32)
            
            dt[:,:,2:]=hdf5["/2D Scan/Detectors/"][()]
    
            if start1>stop1 and step1>0: step1=-step1
            if start1<stop1 and step1<0: step1=-step1
            if start2>stop2 and step2>0: step2=-step2    
            if start2<stop2 and step2<0: step2=-step2    
    
            self.xvals=globalfuncs.frange(start1,end=stop1,inc=step1)
            self.yvals=globalfuncs.frange(start2,end=stop2,inc=step2)
            
            if len(self.xvals)>dtshaped[1]:self.xvals=self.xvals[:-1]        
            if len(self.yvals)>dtshaped[0]:self.yvals=self.yvals[:-1]        
    
            print ("WARNING! FORCING X ARRAYS TO FIT.")        
            if len(self.xvals)!=dtshaped[1]: self.xvals=self.xvals[:dtshaped[1]]
            print ("WARNING! FORCING Y ARRAYS TO FIT.")        
            if len(self.yvals)!=dtshaped[0]: self.yvals=self.yvals[:dtshaped[0]]
            
            
            self.nxpts=len(self.xvals)
            self.nypts=len(self.yvals)
                   
            #add coordinates to dt matrix
            for i in range(self.nxpts):
                dt[:,i,1]=np.ones((self.nypts))*self.xvals[i]
            for j in range(self.nypts):
                dt[j,:,0]=np.ones((self.nxpts))*self.yvals[j]
 

            #MCA export?
            #check to see if file exists...
            mcafn=os.path.splitext(fn)[0]+"_SMAK_MCA"+os.path.splitext(fn)[1]
            filelist=os.listdir(os.path.dirname(mcafn))
            if mcafn not in filelist:
                #ask
                if tkinter.messagebox.askyesno(title="MCA Create",message="Create MCA file from data?"):
                    #create

                    otherchans=[]
                    if "/2D Scan/MCA 2" in hdf5: otherchans.append("/2D Scan/MCA 2")
                    if "/2D Scan/MCA 3" in hdf5: otherchans.append("/2D Scan/MCA 3")
                    if "/2D Scan/MCA 4" in hdf5: otherchans.append("/2D Scan/MCA 4")
                        

                    mcamaxno=hdf5["/2D Scan/MCA 1"].shape[2]         
                    mcasize=hdf5["/2D Scan/MCA 1"].shape[0]*hdf5["/2D Scan/MCA 1"].shape[1]
                    mcahdf=h5py.File(mcafn,'w')
                    groupout=mcahdf.create_group("main")
                    mcadata=groupout.create_dataset("mcadata",(mcasize,mcamaxno),maxshape=(None,mcamaxno),dtype='int',compression="gzip",compression_opts=4)
                    
                    n=0
                    ln=hdf5["/2D Scan/MCA 1"].shape[1]
                    ds=hdf5["/2D Scan/MCA 1"]
                    rs=np.reshape(ds,(mcasize,mcamaxno))
                    mcadata[:,:]=rs
                    for k in otherchans:
                        ds=hdf5[k]
                        rs=np.reshape(ds,(mcasize,mcamaxno))
                        mcadata[:,:]=mcadata[:,:]+rs
#                    for i in range(hdf5["/2D Scan/MCA 1"].shape[0]):
#                        print "working line ",i+1
#                        mcadata[n:n+ln,:]=hdf5["/2D Scan/MCA 1"][i,:,:]
#                        for k in otherchans:
#                            mcadata[n:n+ln,:]+=hdf5[k][i,:,:]
#                        n+=ln                        
#                        for j in range(hdf5["/2D Scan/MCA 1"].shape[1]):
#                            mcadata[n,:]=hdf5["/2D Scan/MCA 1"][i,j,:]
#                            for k in otherchans:
#                                mcadata[n,:]+=hdf5[k][i,j,:]
#                            n+=1
#                        print n,'mcas'
                    
                    mcahdf.close()

        else:
            hdf5.close()
            t=time.perf_counter()
    
            #make file copy
            if not temp:
                if wd[0]=='':
                    hdffn=os.path.join(os.path.split(fn)[0],"workingfile"+str(wd[1])+".hdf5")
                else:
                    hdffn=os.path.join(wd[0],"workingfile"+str(wd[1])+".hdf5")
            else:
                if wd[0]=='':
                    hdffn=os.path.join(os.path.split(fn)[0],"temp.hdf5")
                else:
                    hdffn=os.path.join(wd[0],"temp.hdf5")
            print((fn,hdffn))
            shutil.copy(fn,hdffn)
            self.hdf5=h5py.File(hdffn, 'a', **HD5OPT)
            self.hdf5group=self.hdf5["/main"]
            self.hdf5data=self.hdf5["/main/mapdata"]
            self.hasHDF5=True
    
            self.data=HDF5get(self.hdf5data)
    
            
            hdf5xd=self.hdf5["/main/xdata"]
            hdf5yd=self.hdf5["/main/ydata"]
            self.xvals=np.array(hdf5xd[:])
            self.yvals=np.array(hdf5yd[:])
            self.nxpts=hdf5xd.attrs.get("pts")
            self.nypts=hdf5yd.attrs.get("pts")
            self.channels=self.hdf5group.attrs.get("channels")
            self.type=self.hdf5group.attrs.get("origin")
            self.isVert=self.hdf5group.attrs.get("isVert")
            self.labels=list(self.hdf5group.attrs.get("labels"))
            self.comments=self.hdf5group.attrs.get("comments")
            self.energy=self.hdf5group.attrs.get("energy")
    
            print((time.perf_counter()-t))
            return


        hdf5.close()

        #open new hdf

        print((self.nypts,self.nxpts,self.channels+2,dt.shape))
        print((self.labels))
           
        #dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))
        #print dataShaped.shape

        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)

        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dt,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
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
## SCANE
####################################

class SCANE(SuperClass):

    def __init__(self,fn,large,root,temp,wd):
        print("initializing scane obj")
        self.root=root
        self.wd=wd
        self.t=time.perf_counter()
        self.type='SCANE'
        fid=open(fn)
        self.fid=fid
        self.large=large
        self.temp=temp
        self.hasHDF5=False
        #process header
        self.nxpts=int(fid.readline().split(':')[1])
        self.nypts=int(fid.readline().split(':')[1])
        self.isVert=0
        vertCheck=fid.readline()
        if len(vertCheck)>0 and vertCheck.upper().rfind("VERT")!=-1:
            self.isVert=1
        
        self.channels=int(fid.readline().split(':')[1])
        #define channels
        chlab=fid.readline().split(':')
        if chlab[0][0]=='*':
            if chlab[0][0:10]=='* Data Lab':
                self.labels=chlab[1].split()
            else:
                #do defaults
                self.labels=[]
                for i in range(self.channels):
                    self.labels.append('CH'+str(i+1))
                if self.channels==20:
                    self.labels=['I0','I1','FF1','FF2','FF3','FF4','FF5','FF6','FF7','FF8','FF9','FF10','FF11','FF12','FF13','FF14','FF15','FF16','FF17','ICR']
        else:
            self.labels=chlab[1].split()

        #large file edits?
        if large=="Edit" or large=="Single":
            self.remove=['CH2','CH3','CH4','I1','I0','IMPF1','IMPF2','FFCH1','FFCH2']
################            remove=['Zn','Ca','K','S','P','Cl','Si','Mn']
        else:
            self.remove=[]
        if large=="Select":
            self.getdatachannels()
        else:
            self.finish()

    def finish(self):

        rempos=[]
        fid=self.fid
        large=self.large
        t=self.t
        remlab=[]

        for i in range(len(self.labels)):
            l=self.labels[i]
            if large=="Edit" or large=="Single":
                if (len(l.split('.'))>1 and l.split('.')[1] in self.remove) or l in self.remove:
                    #if l.split('.')[1] in self.remove:
                        #print i,l
                    remlab.append(l)
                    self.channels=self.channels-1
                    rempos.append(i)
        
################            #temp fix
            if large=="Select" and l in self.remove:
                remlab.append(l)
                self.channels=self.channels-1
                rempos.append(i)
################            #end temp
        for l in remlab:
            self.labels.remove(l)
        #print self.labels,self.remove
        #print rempos
        
        skipline(fid,1)
        self.comments=skipline(fid,3)
        skipline(fid,2)
        #xpoints
        self.xvals=[]
        buf=fid.readline().split('*')[1].split()
        for b in buf:
            self.xvals.append(float(b))        
        skipline(fid,3)
        #ypoints
        self.yvals=[]
        buf=fid.readline().split('*')[1].split()
        for b in buf:
            self.yvals.append(float(b))                
        skipline(fid,3)
        self.energy=float(fid.readline().split()[1])
        skipline(fid,2)
        #data block (x,y,field)
        dt=[]
        line=' '
        #for line in xreadlines.xreadlines(fid):

        if large!="Single":
            i=0
            while line!='':
                #if line=='':continue
                ttemp=[]
                line=fid.readline()
                linedat=line.split()
                for i in range(len(linedat)):
                    if (i-2) not in rempos:
                        ttemp.append(float(linedat[i]))
                if ttemp!=[]:
                    #self.data[i,:]=np.array(temp)
                    #i+=1
                    dt.append(ttemp)
            fid.close()
            #array-ize data
            self.xvals=np.array(self.xvals)
            self.yvals=np.array(self.yvals)
            try:
                dt=np.array(dt)
            except:
                print ('dt load error')
                print((type(dt)))
                print((len(dt)))
                print((dt[0]))
                return
            
            #self.data=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))
            #self.hasHDF5=False
            dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))
            print((dataShaped.shape))
            if not self.temp: self.hdf5=h5py.File(os.path.join(self.wd[0],'workingfile'+str(self.wd[1])+'.hdf5'),'w', **HD5OPT)
            else: self.hdf5=h5py.File(os.path.join(self.wd[0],'temp.hdf5'),'w', **HD5OPT)
            self.hdf5group=self.hdf5.create_group("main")
            print((self.hdf5group.name))
            self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
            if int(h5py.version.version.split('.')[1])<3:
                print((self.hdf5data.shape))
            else:
                print((self.hdf5data.size,self.hdf5data.shape))
            self.hasHDF5=True
        else: #large==Single

            dataFilepos=fid.tell()
            #JOY Q
            if not self.temp: self.hdf5=h5py.File(os.path.join(self.wd[0],'workingfile'+str(self.wd[1])+'.hdf5'),'w', **HD5OPT)
            else: self.hdf5=h5py.File(os.path.join(self.wd[0],'temp.hdf5'),'w', **HD5OPT)
            self.hdf5group=self.hdf5.create_group("main")
            print((self.hdf5group.name))
            self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),maxshape=(5000,5000,None),dtype='float')
            print((self.hdf5data.size,self.hdf5data.shape))
            self.hasHDF5=True   
            #add data one index at a time
            loadList=list(range(self.channels+len(rempos)+2))
            for r in rempos:
                loadList.remove(r+2)

            i=0
            for loadIndex in loadList:
                dt=[]

                while line!='':
                    if line=='':continue
                    ##temp=[]
                    line=fid.readline()
                    linedat=line.split()
                    #print len(linedat),len(dt)
                    if len(linedat)==0: continue
                    dt.append(float(linedat[loadIndex]))

                try:
                    dt=np.array(dt)
                except:
                    print ('dt load error')
                    print((type(dt)))
                    print((len(dt)))
                    print((dt[0]))
                    return
                ##print len(dt),self.nypts*self.nxpts
                dataShaped=np.reshape(dt,(self.nypts,self.nxpts))
                ##print dataShaped.shape
                self.hdf5data[:,:,i]=dataShaped
                print((self.hdf5data.size,self.hdf5data.shape))
                print(("done",loadIndex,i))
                fid.seek(dataFilepos,0)
                print(("fid at",fid.tell()))
                line=" "
                i+=1

            fid.close()

            #array-ize data
            self.xvals=np.array(self.xvals)
            self.yvals=np.array(self.yvals)

        #add other meta-data to HDF for posterity...
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

        #print self.nxpts,self.nypts

        self.data=HDF5get(self.hdf5data)

        if self.isVert:
            pass

        print((time.perf_counter()-t))

    def getdatachannels(self):
        self.dialog=Pmw.SelectionDialog(self.root,title='Channel Select',buttons=('OK',),defaultbutton='OK',
                                        scrolledlist_labelpos='n',label_text='Channel List',scrolledlist_items=self.labels,
                                        command=self.selected)
        self.dialog.component('scrolledlist').component('listbox').configure(selectmode=tkinter.EXTENDED)
        self.dialog.activate()

    def selected(self,result):
        pick=self.dialog.getcurselection()
        self.dialog.deactivate()
        remove=[]
        for i in self.labels:
            if i not in pick:
                remove.append(i)
        self.remove=remove
        self.finish()
        
####################################
## SUPER
####################################

class SUPER(SuperClass):

    def __init__(self,fn,start,temp,wd):
        self.type='SUPER'
        fp=fn.split('.')[0]
        fid=open(fn)
        #process header of "G" file
        self.nxpts=0
        while 1==1:
            bad=fid.readline().split()
            if bad[0]=='#S':
                self.nypts=int(bad[5])+1
                break       
        while 1==1:
            bad=fid.readline().split()
            if bad[0]=='#L':
                break
        self.xvals=[]
        self.yvals=[]
        dt=[]
        fnum=start
        #begin reading data block
        while 1==1:
            try:
                self.xvals.append(float(fid.readline().split()[0]))
            except:
                break
            ttemp=[]
            #open lin file
            fid2=open(fp+'.'+fnum,'r')
            #if first, process line header
            if self.nxpts==0:
                skipline(fid2,7)
                self.channels=int(fid2.readline().split()[1])-1
                skipline(fid2,2)
                self.energy=float(fid2.readline().split()[1])
                while 1==1:
                    bad=fid2.readline().split()
                    if bad[0]=='#L':
                        break
            else:
                while 1==1:
                    bad=fid2.readline().split()
                    if bad[0]=='#L':
                        break
            #read the data lines
            while 1==1:
                buf=fid2.readline().split()
                if buf==[]: break
                if self.nxpts==0:
                    self.yvals.append(float(buf[0]))
                ttemp.append(self.xvals[-1])
                for num in buf:
                    ttemp.append(float(num))
            self.nxpts=self.nxpts+1
            dt.append(ttemp)
            fid2.close()
            #increment fnum
            fnum=str(int(fnum)+1)
            fnum=fnum.zfill(3)
        #end loop
        t=self.xvals
        self.xvals=np.array(self.yvals)
        self.yvals=np.array(t)
        dt=np.array(dt)
        dataShaped=np.reshape(dt,(self.nxpts,self.nypts,self.channels+2))

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nxpts,self.nypts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        t=self.nxpts
        self.nxpts=self.nypts
        self.nypts=t
        #set labels
        if self.channels<=12:
            typical=['I0','I1','I2','I4','I5','I6','FF1','FF2','FF3','FF4','FF5','FFtime']
            self.labels=typical[:self.channels]
        else:
            typical=['I0','I1','I2','I4','I5','I6','FF1','FF2','FF3','FF4','FF5','FF6','FF7','FF8','FF9','FF10','FF11','FF12','FF13','FF14','FF15','FF16','FF17','ICR']
            self.labels=typical[:self.channels]
        self.comments='Super File'
        fid.close()

        self.isVert=0

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
## ROBL SPEC
####################################

class SPEC(SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='SPEC'
        fp=fn.split('.')[0]
        fid=open(fn)
        #process header of "SPEC" file
        self.nxpts=0
        self.nypts=0
        self.xvals=[]
        self.yvals=[]
        self.energy=None
        energyIndex=None
        energyLine=None
        dt=[]

        comlines=''
        lines=fid.readlines()
        fid.close()
        readdata=False
        
        for l in lines:
            bad=l.split()
            if not readdata:
                #print bad
                if len(bad)>0 and len(bad[0])>2 and bad[0][0:2]=='#O':
                    if energyIndex is None:
                        for obj in bad:
                            if obj == 'energy':
                                energyIndex=bad.index(obj)
                                energyLine=bad[0][-1]
                    print((l,energyIndex,energyLine))
                if len(bad)>0 and len(bad[0])>2 and bad[0][1] == 'P' and energyIndex is not None:
                    if bad[0][-1] == energyLine:
                        self.energy=float(bad[energyIndex])
                if len(bad)>0 and bad[0]=='#S':
                    self.nypts=int(bad[6])
                    self.nxpts=int(bad[10])
                    yr=[float(bad[4]),float(bad[5])]
                    xr=[float(bad[8]),float(bad[9])]     
                    #make arrays here
                    print (xr,yr)
                    self.yvals=globalfuncs.frange(xr[0],xr[1],(xr[1]-xr[0])/self.nxpts)
                    self.xvals=globalfuncs.frange(yr[0],yr[1],(yr[1]-yr[0])/self.nypts)
                    self.nxpts=len(self.xvals)
                    self.nypts=len(self.yvals)
                elif l.startswith('#URO'):
                    comlines+=l+'\n'
                elif len(bad)>0 and bad[0]=='#L':
                    #labels   
                    self.labels=[]
                    for i in bad[3:]:
                        self.labels.append(i)
                    self.channels=len(self.labels)
                    readdata=True
            else:
                #data reading
                tm=[]
                if len(bad)==0: continue
                for num in bad:
                    tm.append(float(num))
                dt.append(tm)
            
        dt=np.array(dt)
        dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))
        print((dataShaped.shape))
        print (self.nxpts,self.nypts)
        
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

#        t=self.nxpts
#        self.nxpts=self.nypts
#        self.nypts=t
        self.comments=comlines
        self.isVert=0
        print((self.energy))
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
## RAS ASCII
####################################

class RAS (SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='RAS'
        fid=open(fn)
        lines=fid.read().split('\n')
        fid.close()
        self.energy='1'
        self.xvals=[]
        self.yvals=[]
        self.comments=''
        self.channels=0
        dt=[]
        datablock=0
        for line in lines:
            l=0
            if len(line.split())>0:
                l=len(line.split()[0])
            if l>7 and line.split()[0][:7]=='Comment':
                self.comments=self.comments+line+'\n'
            if l>8 and line.split()[0][:8]=='Channels':
                self.channels=int(line.split()[1])
                self.labels=[]
                for i in range(self.channels):
                    self.labels.append('CH'+str(i+1))
            if l>6 and line.split()[0][:6]=='Points':
                self.nxpts=int(line.split()[1])
                self.xvals=list(range(int(self.nxpts)))
            if l>5 and line.split()[0][:5]=='Lines':
                self.nypts=int(line.split()[1])
                self.yvals=list(range(int(self.nypts)))
            if l>4 and line.split()[0][:4]=='Data':
                datablock=1
            if len(line.split())==self.channels and datablock:
                #read data
                ttemp=[0.,0.]
                for d in line.split():
                    ttemp.append(float(d))
                dt.append(ttemp)
        #end loop and finish types
        self.xvals=np.array(self.xvals)
        self.yvals=np.array(self.yvals)        
        dt=np.array(dt)
        #print dt.shape,self.nypts,self.nxpts,self.channels
        dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))        

        print((dataShaped.shape))
        if not self.temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## APS-DATA
####################################


class GSEH5load(SuperClass):

    def __init__(self,fn,root,temp,wd):
        
        self.isVert=0
        self.energy='1'
        
        #open hdf
        GSEh5=h5py.File(fn)       
        self.type=None

        if "TofDAQ Version" in GSEh5.attrs.keys():
            self.type='MASSBOX'
            print ('MASSBOX')
        if "/Data ID" in GSEh5:
            self.type='SIGRAY'
            print ('SIGRAY')
        if "/1/measurement" in GSEh5:
            self.type="CHESS_HDF5"
            xroot="/measurement/"
            #print str(GSEh5["/1"].attrs.get("acquisition_shape"))
        if "/xrfmap/config/environ/address" in GSEh5 and str(GSEh5["/xrfmap/config/environ/address"][1]).startswith("ID1"):
            self.type="APSGSE_HDF"    
            xroot="/xrfmap"
        if "/xrmmap/config/environ/address" in GSEh5:
            if type(GSEh5["/xrmmap/config/environ/address"][1]) == bytes:
                teststr = GSEh5["/xrmmap/config/environ/address"][1].decode()
            else:
                teststr =str(GSEh5["/xrmmap/config/environ/address"][1])            
            if teststr.startswith("XF") or teststr.startswith("13ID") or teststr.startswith("experiment_i"):
                self.type="APSGSE_HDF2"    
                xroot="/xrmmap"
        if "/xrfmap/scan_metadata/" in GSEh5 and str(GSEh5["/xrfmap/scan_metadata"].attrs.get("file_format")) == "NSLS2-XRF-MAP": 
            xroot="/xrfmap"
            print ('NSLS-II-XRFMAP')

        if self.type=="CHESS_HDF5":
            hindex=0
            npt=0
            shape=None
            for h in range(1,10):
                if "/"+str(h) in GSEh5:
                    print((str(GSEh5["/"+str(h)].attrs.get("acquisition_shape")))) 
                    print((str(GSEh5["/"+str(h)].attrs.get("npoints")))) 
                    if int(GSEh5["/"+str(h)].attrs.get("npoints"))>npt:
                        qnpt=int(GSEh5["/"+str(h)].attrs.get("npoints"))
                        qshape=str(GSEh5["/"+str(h)].attrs.get("acquisition_shape")) 
                        qrp=eval(qshape)[0]*eval(qshape)[1]
                        if qnpt==qrp:                                               
                            npt=qnpt                                
                            hindex=h
                            shape=str(GSEh5["/"+str(h)].attrs.get("acquisition_shape")) 
                else:
                    break
            print((hindex,shape,npt))
            if npt==0 or shape is None:
                return
            xroot="/"+str(hindex)
            labels=list(GSEh5[xroot+"/measurement/element_maps"].keys())
            self.labels=list(labels[:])
            #print self.labels
            self.channels=len(self.labels)
            self.comments=""
            
            sy=eval(shape)[0]
            sx=eval(shape)[1]
            start1=GSEh5[xroot+"/measurement/scalar_data/samx"][0] #x is second axis)
            start2=GSEh5[xroot+"/measurement/scalar_data/samz"][0] #z is first axis)
            stop1=GSEh5[xroot+"/measurement/scalar_data/samx"][-1]
            stop2=GSEh5[xroot+"/measurement/scalar_data/samz"][-1]
            step1=(stop1-start1)/(sx-1)
            step2=(stop2-start2)/(sy-1)

            self.xvals=globalfuncs.frange(start1,end=stop1,inc=step1)
            self.yvals=globalfuncs.frange(start2,end=stop2,inc=step2)

            dtshaped=[sy,sx,self.channels+2]
            dt=np.zeros(tuple(dtshaped),dtype=np.float32)

            #add data
            i=2
            for la in self.labels:
                nextd=GSEh5[xroot+"/measurement/element_maps/"+la][()]
                nextd=nextd.reshape(eval(shape))
                dt[:,:,i]=nextd
                i+=1


            if len(self.xvals)>dtshaped[1]:self.xvals=self.xvals[:-1]        
            if len(self.yvals)>dtshaped[0]:self.yvals=self.yvals[:-1]    
            
            if len(self.xvals)!=dtshaped[1]: 
                print ("WARNING! FORCING X ARRAYS TO FIT.")        
                self.xvals=self.xvals[:dtshaped[1]]
            if len(self.yvals)!=dtshaped[0]: 
                print ("WARNING! FORCING Y ARRAYS TO FIT.")        
                self.yvals=self.yvals[:dtshaped[0]]            

            self.nxpts=len(self.xvals)
            self.nypts=len(self.yvals)

            #add coordinates to dt matrix
            for i in range(self.nxpts):
                dt[:,i,1]=np.ones((self.nypts))*self.xvals[i]
            for j in range(self.nypts):
                dt[j,:,0]=np.ones((self.nxpts))*self.yvals[j]

            for i in range(self.channels):
                self.labels[i]=str(self.labels[i])
 
            GSEh5.close()

        elif self.type=='SIGRAY':
            xroot='/Data ID'
        
            xmin = float(GSEh5[xroot].attrs.get("X Start"))
            xmax = float(GSEh5[xroot].attrs.get("X End"))
            xn = int(GSEh5[xroot].attrs.get("X Point"))
            ymin = float(GSEh5[xroot].attrs.get("Y Start"))
            ymax = float(GSEh5[xroot].attrs.get("Y End"))
            yn = int(GSEh5[xroot].attrs.get("Y Point"))
        
            stepx=(xmax-xmin)/(xn-1)
            stepy=(ymax-ymin)/(yn-1)
        
            self.nxpts=xn
            self.nypts=yn
            self.xvals=globalfuncs.frange(xmin,end=xmax,inc=stepx)
            self.yvals=globalfuncs.frange(ymin,end=ymax,inc=stepy)        
        
            dfnroot=GSEh5[xroot].attrs.get("Data File Name")[0]
            dfnroot=bytes.decode(dfnroot,'utf-8')
            imgcap = int(GSEh5[xroot].attrs.get("Capture Image"))
            if imgcap:
                imgxmax=float(GSEh5[xroot].attrs.get("Image X Max"))
                imgxmin=float(GSEh5[xroot].attrs.get("Image X Min"))
                imgymax=float(GSEh5[xroot].attrs.get("Image Y Max"))
                imgymin=float(GSEh5[xroot].attrs.get("Image Y Min"))
            
            self.comments=""
            self.energy=15000.0
            
            self.labels=["XRF","pid"]
            
            
            self.channels = len(self.labels)

            dtshaped=[yn,xn,self.channels+2]
            dt=np.zeros(tuple(dtshaped),dtype=np.float32)
            pid = np.arange(yn*xn)
            pid=pid.reshape((yn,xn))
            dt[:,:,3]=pid

            #add coordinates to dt matrix
            for i in range(self.nxpts):
                dt[:,i,1]=np.ones((self.nypts))*self.xvals[i]
            for j in range(self.nypts):
                dt[j,:,0]=np.ones((self.nxpts))*self.yvals[j]

            
            GSEh5.close()

            #read and assimilate data... (and process MCA)
            fnout = os.path.splitext(fn)[0]+"_mca.hdf5"
            #if wd[0]!='':
            #    fnout=os.path.join(wd[0],os.path.splitext(os.path.split(fn)[1])[0]+"_mca.hdf5")
            print (fnout)    
            writeMCA=False
            if not os.path.exists(fnout):
                writeMCA=True
                fout=h5py.File(fnout,'w')
                groupout=fout.create_group("main")
                maxpoints=yn*xn
                maxlen=4096
                mcadata=groupout.create_dataset("mcadata",(maxpoints,maxlen),maxshape=(None,maxlen),dtype='int',compression="gzip",compression_opts=4)
            
            fnbase = os.path.dirname(fn)+os.path.sep
            for findex in range(yn):
                
                dfn=fnbase+dfnroot+str(findex+1)+".hdf5"
                dfh5=h5py.File(dfn)   
                
                #nx x 4096
                newline = dfh5["/entry/detector/data1"][:]
                print (findex, newline.shape)
                dt[findex,:,2]=np.sum(newline,axis=2)[:,0]    
                
                if writeMCA:
                    mcadata[findex*xn:(findex+1)*xn,:]=newline[:,0,:]
                
                dfh5.close()
                
            if imgcap:
                
                ifn = os.path.dirname(fn)+os.path.sep+"MosaicImages"+os.path.sep+"Overview.jpg"
                iofn = os.path.splitext(fn)[0]+"_imgout.jpg"
                if os.path.exists(ifn) and not os.path.exists(iofn):
                    print ("processing visible image mosaic...")
                    im=MainImage.open(ifn)
                    im.load()
                    img=im.transpose(MainImage.FLIP_LEFT_RIGHT) #.convert('L')
                    (inxpts,inypts)=img.size[0:2]
                    #istpx = (imgxmax-imgxmin)/(inxpts-1)
                    #istpy = (imgymax-imgymin)/(inypts-1)
                    iymin = min(ymin,ymax)
                    iymax = max(ymin,ymax)
                    ixmin = min(xmin,xmax)
                    ixmax = max(xmin,xmax)
                    imcrxa = (ixmin-imgxmin)/(imgxmax-imgxmin)
                    imcrxb = (imgxmax-ixmax)/(imgxmax-imgxmin)
                    imcrya = (iymin-imgymin)/(imgymax-imgymin)
                    imcryb = (imgymax-iymax)/(imgymax-imgymin)
                    print (imcrxa,imcrxb,imcrya,imcryb)
                    img = img.crop([int(imcrxa*inxpts),int(imcrya*inypts),int((1-imcrxb)*inxpts),int((1-imcryb)*inypts)])
                    img.save(iofn)
                else:
                    print ('image mosaic does not exist at...',ifn)

        elif self.type=="MASSBOX":
            #MassBOX TOF-MS
            
            dt=[]
            self.xvals=[]
            self.yvals=[]
            self.labels=[]
            self.channels=0
            self.energy=1
            self.comments=''

            unitconversion = 82.9875519  # units to mm

            #defaults...

            nx=GSEh5['PeakData']['PeakData'].shape[1]
            ny=GSEh5['PeakData']['PeakData'].shape[0]
            self.xvals=np.arange(nx,dtype=float)
            self.yvals=np.arange(ny,dtype=float)
            self.nxpts=nx
            self.nypts=ny
            
            for l in GSEh5['PeakData']['PeakTable']:
                self.labels.append('Mass-'+str(l[1]))
            self.channels=len(self.labels)  
            
            
            #get json file
            filelist=os.listdir(os.path.dirname(fn))
            jpf=None
            for jf in filelist:
                if os.path.splitext(jf)[1].lower()=='.json':
                    jpf=jf
            if jpf is None:
                print ('No json parameter file')
                
            else:
                hfile=open(os.path.dirname(fn)+os.sep+jpf)
                hinfo=json.loads(hfile.read())
                hfile.close()
                
                if ('CoordinateInfo' not in hinfo) and ('SampleInfo' not in hinfo):
                    print ('invalid header')
                    #use the current defaults...
                else:
                    bn = hinfo['SampleInfo']['Name']
                    nrast = hinfo['Rasters']['rasterCount']

                    for r in hinfo['Rasters'].values():
                        if type(r)==int: continue
                        if r['FilePath'] in fn:
                            print (r['FilePath'])
                            fpx = float(r['firstPointX'])*unitconversion
                            fpy = float(r['firstPointY'])*unitconversion                        
                            spx = float(r['secondPointX'])*unitconversion
                            spy = float(r['secondPointY'])*unitconversion  
                            
                            nx = int(r['Width'])
                            ny = int(r['Height'])                            

                            xst = ((spx-fpx)/(nx-1))
                            yst = ((spy-fpy)/(ny-1))
                                   
                    #make base arrays
                    self.xvals=globalfuncs.frange(fpx,spx,xst)
                    self.yvals=globalfuncs.frange(fpy,spy,yst)
                    self.nxpts=nx
                    self.nypts=ny

            newshape = (ny,nx,GSEh5['PeakData']['PeakData'].shape[3]+2)
            dt=np.zeros(tuple(newshape),dtype=np.float32)

            rawset = GSEh5["PeakData"]["PeakData"][:,:,0,:]
            rawset = rawset.reshape(rawset.shape[0]*rawset.shape[1],rawset.shape[2])
            rawset = rawset[:nx*ny,:]
            rawset = rawset.reshape((nx,ny,rawset.shape[1]))

            dt[:,:,2:]=rawset
            xv,yv=np.meshgrid(self.xvals,self.yvals)
            print (xv.shape,yv.shape)
            dt[:,:,0]=xv
            dt[:,:,1]=yv 
            
            
            #iterate spiral fix....
            for fi in range(2,newshape[2]):
                dt[:,:,fi]=to_spiral(dt[:,:,fi])
            
            #extract m/z data
            fnout=os.path.splitext(fn)[0]+"_mz.hdf5"
            print (fnout)
            if not os.path.exists(fnout):
                fout=h5py.File(fnout,'w')
                groupout=fout.create_group("main")   
                
                rawdata = GSEh5["FullSpectra"]["TofData"][:,:,0,:]
                maxlen=len(GSEh5["FullSpectra"]["MassAxis"])
                rawdata = rawdata.reshape((rawdata.shape[0]*rawdata.shape[1],maxlen))
                rawdata = rawdata[:nx*ny,:]
                rawdata = rawdata.reshape((nx,ny,rawdata.shape[1]))
                #print (rawdataS.shape)
                
                #fix spiral...
                for mi in range(rawdata.shape[2]):
                    rawdata[:,:,mi]=to_spiral(rawdata[:,:,mi])
                rawdata = rawdata.reshape((rawdata.shape[0]*rawdata.shape[1],maxlen))
                
                maxpoints=rawdata.shape[0]#*rawmcadata.shape[1]
                mcadata=groupout.create_dataset("mcadata",(maxpoints,rawdata.shape[1]),maxshape=(None,rawdata.shape[1]),dtype='float',compression="gzip",compression_opts=4)
                mcadataxv=groupout.create_dataset("xdata",(maxlen),maxshape=(maxlen),dtype='float',compression="gzip",compression_opts=4)
                
                mcadata[:,:]=rawdata
                mcadataxv[:]=GSEh5["FullSpectra"]["MassAxis"][()]
                
                fout.flush() 
                fout.close()          

            GSEh5.close()

        elif self.type!=None:
#        paths to hdf data:
#        /xrfmap/config/scan/
#            comments
#            start1
#            start2
#            step1
#            step2
#            stop1
#            stop2
#            time1
#            
#        /xrfmap/roimap/
#            sum_name
#            sum_raw
#            det_name
#            det_raw           
                    
            #transfer data
            labels=GSEh5[xroot+"/roimap/sum_name"]
            self.labels=list(labels[:])
            self.channels=len(self.labels)
            
            comments=GSEh5[xroot+"/config/scan/comments"]
            self.comments="COM: "+str(comments[()])
                
            start1=GSEh5[xroot+"/config/scan/start1"][()]
            start2=GSEh5[xroot+"/config/scan/start2"][()]
            stop1=GSEh5[xroot+"/config/scan/stop1"][()]
            stop2=GSEh5[xroot+"/config/scan/stop2"][()]
            step1=GSEh5[xroot+"/config/scan/step1"][()]
            step2=GSEh5[xroot+"/config/scan/step2"][()]
            time1=GSEh5[xroot+"/config/scan/time1"][()]
            
            dtshaped=list(GSEh5[xroot+"/roimap/sum_raw"].shape)
            dtshaped[2]=dtshaped[2]+2
            dt=np.zeros(tuple(dtshaped),dtype=np.float32)
            
            dt[:,:,2:]=GSEh5[xroot+"/roimap/sum_raw"][()]
    
            if start1>stop1 and step1>0: step1=-step1
            if start1<stop1 and step1<0: step1=-step1
            if start2>stop2 and step2>0: step2=-step2    
            if start2<stop2 and step2<0: step2=-step2    
    
            self.xvals=globalfuncs.frange(start1,end=stop1,inc=step1)
            self.yvals=globalfuncs.frange(start2,end=stop2,inc=step2)
            
            if len(self.xvals)>dtshaped[1]:self.xvals=self.xvals[:-1]        
            if len(self.yvals)>dtshaped[0]:self.yvals=self.yvals[:-1]        
    
            print ("WARNING! FORCING X ARRAYS TO FIT.")        
            if len(self.xvals)!=dtshaped[1]: self.xvals=self.xvals[:dtshaped[1]]
            print ("WARNING! FORCING Y ARRAYS TO FIT.")        
            if len(self.yvals)!=dtshaped[0]: self.yvals=self.yvals[:dtshaped[0]]
            
            
            self.nxpts=len(self.xvals)
            self.nypts=len(self.yvals)
                   
            #add coordinates to dt matrix
            for i in range(self.nxpts):
                dt[:,i,1]=np.ones((self.nypts))*self.xvals[i]
            for j in range(self.nypts):
                dt[j,:,0]=np.ones((self.nxpts))*self.yvals[j]
 
            GSEh5.close()

        elif "/MAPS" in GSEh5:
            self.type="MAPS"
            xroot="/MAPS"

            if "/MAPS/XRF_fits" in GSEh5:
                droot="/XRF_fits"
            else:
                droot="/XRF_roi"

            labels=GSEh5[xroot+"/channel_names"]
            self.labels=list(labels[:])
            self.labels.insert(0,'ds_ic')
            self.labels.insert(0,'us_ic')
            frextra=2
            self.labels.append('OCR1')
            self.labels.append('ICR1')
            extra=4
            
            self.channels=len(self.labels)
            
            #comments=GSEh5[xroot+"/config/scan/comments"]
            self.comments="COM: "
                
            start1=GSEh5[xroot+"/x_axis"][()][0]
            start2=GSEh5[xroot+"/y_axis"][()][0]
            stop1=GSEh5[xroot+"/x_axis"][()][-1]
            stop2=GSEh5[xroot+"/y_axis"][()][-1]
            step1=GSEh5[xroot+"/x_axis"][()][1]-start1
            step2=GSEh5[xroot+"/y_axis"][()][1]-start2
            time1=100#GSEh5[xroot+"/config/scan/time1"][()]
            
            dtinitshaped=list(GSEh5[xroot+droot].shape)  #data is c,x,y need x,y,c
            dtshaped=[dtinitshaped[1],dtinitshaped[2],dtinitshaped[0]]            
            dtshaped[2]=dtshaped[2]+2+extra
            dt=np.zeros(tuple(dtshaped),dtype=np.float32)
            
            for j in range(len(self.labels)-extra):
                dtemp=GSEh5[xroot+droot][()][j,:,:]
                dtemp[dtemp==np.inf]=0
                dtemp=np.nan_to_num(dtemp)
                dt[:,:,2+frextra+j]=dtemp              
            
            scalername=list(GSEh5[xroot+"/scaler_names"][:])
            for n in ('us_ic','ds_ic','OCR1','ICR1'):
                i=scalername.index(n)
                di=self.labels.index(n)
                dtemp=GSEh5[xroot+"/scalers"][()][i,:,:] 
                dtemp[dtemp==np.inf]=0
                dtemp=np.nan_to_num(dtemp)
                dt[:,:,di+2]=dtemp                 

            self.xvals=GSEh5[xroot+"/x_axis"][()] #globalfuncs.frange(start1,end=stop1,inc=step1)
            self.yvals=GSEh5[xroot+"/y_axis"][()] #globalfuncs.frange(start2,end=stop2,inc=step2)

            #read the real values?
            ##dt[:,:,:2]=GSEh5[xroot+"/scalers"][()][:,:,-2:]
            
            #if len(self.xvals)>dtshaped[1]:self.xvals=self.xvals[:-1]        
            #if len(self.yvals)>dtshaped[0]:self.yvals=self.yvals[:-1]        

            print ("WARNING! FORCING X ARRAYS TO FIT.")        
            if len(self.xvals)!=dtshaped[1]: self.xvals=self.xvals[:dtshaped[1]]
            print ("WARNING! FORCING Y ARRAYS TO FIT.")        
            if len(self.yvals)!=dtshaped[0]: self.yvals=self.yvals[:dtshaped[0]]
            
            self.nxpts=len(self.xvals)
            self.nypts=len(self.yvals)
                   
            #add coordinates to dt matrix
            for i in range(self.nxpts):
                dt[:,i,1]=np.ones((self.nypts))*self.xvals[i]
            for j in range(self.nypts):
                dt[j,:,0]=np.ones((self.nxpts))*self.yvals[j]
 
            GSEh5.close()
            

                    
        elif "/xrfmap/scalers" in GSEh5:
            self.type="NSLSII_HDF"        
        
            #determine where the xrf_fit portions are...
            dataroots=["/xrfmap/det1","/xrfmap/det2","/xrfmap/det3","/xrfmap/det4","/xrfmap/detsum"]
            datapaths=[]
            for dr in dataroots:
                if dr in GSEh5 and dr+"/xrf_fit" in GSEh5:
                    print (dr)
                    datapaths.append(dr)
            
            xtractMCA=False
            if len(datapaths) == 0: 
                print ("No xrf fitted data in hdf file")
                xtractMCA=True
            if len(datapaths) > 1:
                #multiple choices...

                scadialog=Pmw.Dialog(parent=root,title="SCA Selection",buttons=('OK','Cancel'))
                scaselbox=Pmw.TtkRadioSelect(parent=scadialog.interior(),labelpos='n',label_text="Please select detector channel to load")
                for sb in datapaths:
                    scaselbox.add(sb.split("/")[-1])
                scaselbox.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=5)
                scaselect=scadialog.activate()
                if scaselect == "Cancel" : readpath=datapaths[0]
                else:
                    dsel=scaselbox.getvalue()
                    readpath="/xrfmap/"+dsel
            if len(datapaths) == 1: 
                readpath=datapaths[0]
    
            #transfer data
            if not xtractMCA:
                labels=GSEh5[readpath+"/xrf_fit_name"]
            else:
                labels=[]
            
            scalers=GSEh5["/xrfmap/scalers/name"]
            
            self.labels=list(scalers[:])+list(labels[:])
            self.channels=len(self.labels)
            
            comments="None in file" ##GSEh5["/xrfmap/config/scan/comments"]
            self.comments=comments
                
            positions= GSEh5["/xrfmap/positions/pos"]   

            
            start1= np.average(positions[0,:,0])
            start2= np.average(positions[1,0,:])
            stop1= np.average(positions[0,:,positions.shape[2]-1])
            stop2= np.average(positions[1,positions.shape[1]-1,:])
            step1=(stop1-start1)/(positions.shape[2]-1)
            step2=(stop2-start2)/(positions.shape[1]-1)
            
            print((start1,stop1,step1))
            print((start2,stop2,step2))
            
            if not xtractMCA:
                nslsfitdata=GSEh5[readpath+"/xrf_fit"][()]
                print((nslsfitdata.shape))
                nslsfitdataT= np.swapaxes(nslsfitdata,0,2)
                nslsfitdataT= np.swapaxes(nslsfitdataT,0,1)
                print((nslsfitdataT.shape))
                dtshaped=list(nslsfitdataT.shape)
                dtshaped[2]=dtshaped[2]+2+len(scalers)
                dt=np.zeros(tuple(dtshaped),dtype=np.float32)
                dt[:,:,2:2+len(scalers)]=GSEh5["/xrfmap/scalers/val"][()]
                dt[:,:,2+len(scalers):]=nslsfitdataT

            else:
                nslsfitdata=GSEh5["xrfmap/detsum/counts"][()]
                print((nslsfitdata.shape))
                dtshaped=list(nslsfitdata.shape)
                dtshaped[2]=3+len(scalers)
                dt=np.zeros(tuple(dtshaped),dtype=np.float32)
                dt[:,:,2:2+len(scalers)]=GSEh5["/xrfmap/scalers/val"][()]
                dt[:,:,-1]=np.sum(nslsfitdata,axis=2)
                self.labels.append('FF_SUM')
                self.channels=len(self.labels)
    
            if start1>stop1 and step1>0: step1=-step1
            if start1<stop1 and step1<0: step1=-step1
            if start2>stop2 and step2>0: step2=-step2    
            if start2<stop2 and step2<0: step2=-step2    
    
            print((step1,step2))    
    
            self.xvals=globalfuncs.frange(start1,end=stop1,inc=step1)
            self.yvals=globalfuncs.frange(start2,end=stop2,inc=step2)
            
            if len(self.xvals)>dtshaped[1]:self.xvals=self.xvals[:-1]        
            if len(self.yvals)>dtshaped[0]:self.yvals=self.yvals[:-1]        
    
            print ("WARNING! FORCING X ARRAYS TO FIT.")        
            if len(self.xvals)!=dtshaped[1]: self.xvals=self.xvals[:dtshaped[1]]
            print ("WARNING! FORCING Y ARRAYS TO FIT.")        
            if len(self.yvals)!=dtshaped[0]: self.yvals=self.yvals[:dtshaped[0]]
            
            
            self.nxpts=len(self.xvals)
            self.nypts=len(self.yvals)
                   
            #add coordinates to dt matrix
            for i in range(self.nxpts):
                dt[:,i,1]=np.ones((self.nypts))*self.xvals[i]
            for j in range(self.nypts):
                dt[j,:,0]=np.ones((self.nxpts))*self.yvals[j]

            if xtractMCA:

                #extract MCA data
                fnout=os.path.splitext(fn)[0]+"_mca.hdf5"
                if wd[0]!='':
                    fnout=os.path.join(wd[0],os.path.splitext(os.path.split(fn)[1])[0]+"_mca.hdf5")
                
                print (fnout)        
                if not os.path.exists(fnout):
                    fout=h5py.File(fnout,'w')
                    groupout=fout.create_group("main")
            
                    rawmcadata=nslsfitdata
                        
                    print((rawmcadata.shape))
                    maxpoints=rawmcadata.shape[0]*rawmcadata.shape[1]
                    maxlen=rawmcadata.shape[2] ##min(rawmcadata.shape[2],2048)
                    mcadata=groupout.create_dataset("mcadata",(maxpoints,maxlen),maxshape=(None,maxlen),dtype='int',compression="gzip",compression_opts=4)
                    
                    print ("reorg")
                    rawmcadata=rawmcadata[:,:,:maxlen]
                    rawmcadata=np.reshape(rawmcadata,(maxpoints,maxlen)) 
                    i=0
                    cb=100
                    while i<maxpoints:
                        if i+cb<maxpoints:
                            mcadata[i:i+cb,:]=rawmcadata[i:i+cb,:]
                            i+=cb
                        else:
                            mcadata[i:,:]=rawmcadata[i:,:]
                            i=maxpoints+1
            
                    fout.flush() 
                    fout.close()
                    print ('mcadone')



            GSEh5.close()

        else:
            print ("unknown h5 type")
            GSEh5.close()
            return



          
        #open new hdf

        print((self.nypts,self.nxpts,self.channels+2,dt.shape))
        print((self.labels))
           
        #dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))
        #print dataShaped.shape

        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)

        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dt,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
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
        

class APS_GSE(SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='APSGSE'
        fid=open(fn)
        lines=fid.read().split('\n')
        fid.close()
        self.energy='1'
        self.comments=''
        self.xvals=[]
        self.yvals=[]
        dt=[]
        hasx=0
        i=-1
        fast=0
        for fc in range(100):
            if len(lines[fc].split())>1 and lines[fc].split()[-1].upper()=='FAST':
                fast=1
        for line in lines:
            i=i+1
            if line[:3]==';2D':
                #top of data set line
                self.yvals.append(float(line.split()[2]))
                #read data block in
                j=1
                while lines[i+j][0]==';':
                    j=j+1
                #now get data
                while i+j<len(lines)-1 and lines[i+j][0]!=';':
                    if not hasx:
                        self.xvals.append(float(lines[i+j].split()[0]))
                    ttemp=[]
                    for d in lines[i+j].split():
                        ttemp.append(float(d))
                    #insert y value if fast
                    if 1: #fast only???
                        ttemp.insert(1,float(line.split()[2]))
                    dt.append(np.array(ttemp))
                    j=j+1
                hasx=1                        
            if len(line.split())>1 and line.split()[-1]=='titles:':
                ttemp=[]
                self.comments=''
                j=1
                while 1:
                    if lines[i+j].split()[-2]=='PV' and lines[i+j].split()[-1]=='list:':
                        break
                    ttemp.append(lines[i+j])
                    j=j+1
                for t in ttemp:
                    self.comments=self.comments+t+'\n'
            if len(line.split())>2 and line.split()[-2]=='column' and line.split()[-1]=='labels:':
                self.labels=[]
                j=1
                k=0
                delim='{'
                while lines[i+j][1]!='-':
                    if lines[i+j].split()[1][0]=='P' and lines[i+j].rfind('Time')==-1:
                        k=k+1
                    else:
                        i1=lines[i+j].rfind('{')
                        i2=lines[i+j].rfind('}')
                        if i1!=-1 and i2!=-1:
                            self.labels.append(lines[i+j][i1+1:i2])
                        else:
                            self.labels.append('UNK')
                                
#                        labtemp=lines[i+j].split(delim)[1]
#                        if lower(labtemp[0])=='i':
#                            self.labels.append(labtemp[:2])
#                        else:
#                            self.labels.append(labtemp.split()[1])
                    j=j+1     
                self.channels=j-k-1
        fid.close()
        #arrayize data points
        self.nxpts=len(self.xvals)
        self.nypts=len(self.yvals)
        #trim dt
##        check
##        lt=[0]
##        for l in dt:
##            lt.append(len(l))
        dt=np.array(dt)
##        if not fast: dt=dt[:,k-2:]

        #array-ize data
        print((self.nypts,self.nxpts,self.channels+2,dt.shape))
        print((self.labels))
        dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.xvals=np.array(self.xvals)
        self.yvals=np.array(self.yvals)
##        print self.data.shape
##        print self.channels
##        print self.xvals.shape
##        print self.yvals.shape
##        print self.labels

        self.isVert=0

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
## SOLEIL - DIFFABS
####################################

class SOLEILload(SuperClass):

    def __init__(self,fn,root,temp,wd,special):
        
        self.isVert=0
        self.energy='1'
        
        #open hdf
        Sh5=h5py.File(fn,'r')       
                
                        
        self.type="SOLEIL_NXS"        
    
        sroot=list(Sh5.keys())[0]
        sdpath=sroot+"/scan_data"

        if "entry" in Sh5 and "raw_entry" not in Sh5:
            
            tkinter.messagebox.showerror(title="File Error",message="Please choose the XSPRESS .nxs data file")
            return

        if "entry" in Sh5 and "raw_entry" in Sh5:
            self.type="DIAMOND_NXS"
            
            comments="None in file"
            self.comments=Sh5["/raw_entry/sample/description"]
            
            dpath="/entry/auxiliary/"+list(Sh5["/entry/auxiliary/"].keys())[0]
            self.labels=list(Sh5[dpath].keys())
            self.channels=len(self.labels)

            xpos=Sh5[dpath+"/"+self.labels[0]+"/table_x"]
            ypos=Sh5[dpath+"/"+self.labels[0]+"/table_y"]
            self.nxpts=len(xpos)
            self.nypts=len(ypos)
            self.xvals=np.array(xpos)
            self.yvals=np.array(ypos)
            
            dtshaped=[self.nypts,self.nxpts]
            dtshaped.extend([self.channels+2])
            dt=np.zeros(tuple(dtshaped),dtype=np.float32)   

            for i in range(self.nxpts):
                dt[:,i,1]=np.ones((self.nypts))*self.xvals[i]
            for j in range(self.nypts):
                dt[j,:,0]=np.ones((self.nxpts))*self.yvals[j]

            newl=[]             
            for h in enumerate(self.labels,2):
                dt[:,:,h[0]]=Sh5[dpath+"/"+h[1]+"/data"]
                newl.append(str(h[1]))
            self.labels=newl
                
            #MCA export?
            #check to see if file exists...
            mcafn=os.path.splitext(fn)[0]+"_SMAK_MCA"+os.path.splitext(fn)[1]
            filelist=os.listdir(os.path.dirname(mcafn))
            if mcafn not in filelist:
                #ask
                print ('support for mca later')
                #if tkMessageBox.askyesno(title="MCA Create",message="Create MCA file from data?"):
                    #create
            

        elif sdpath+"/data_14" in Sh5 and sdpath+"/actuator_1_1" in Sh5 and sdpath+"/actuator_2_1" not in Sh5:
            print ("fullfield image dataset")
            
            #extract energy list
            if sdpath+"/trajectory_1_1" in Sh5:
                elist=Sh5[sdpath+"/trajectory_1_1"]
            else:
                elist=np.array([1])

            if special==None:
                elist=[elist[-1]]
                skip=1
            else:
                skip=special[1]
                elist=list(elist)[::skip]
            labels=[]
            for e in elist:
                labels.append("eV"+str(float(e)*1000))
            self.labels=labels
            self.channels=len(self.labels)     
            
            #make up image points
            comments="None in file"
            self.comments=comments
            
            if special==None:                
                self.xvals=list(range(2048))
                self.yvals=list(range(2048))
            else:
                self.xvals=list(range(special[0][2]-special[0][0]))
                self.yvals=list(range(special[0][3]-special[0][1]))


            self.nxpts=len(self.xvals)
            self.nypts=len(self.yvals)
            
            dtshaped=[self.nypts,self.nxpts,self.channels+2]
            dt=np.zeros(tuple(dtshaped),dtype=np.float32)
            
            #extract images
            dind=2
            nind=0
            for l in labels:
                if special==None:
                    imdata=Sh5[sdpath+"/data_14"][nind,:,:]
                else:
                    imdata=Sh5[sdpath+"/data_14"][nind,2048-special[0][3]:2048-special[0][1],special[0][0]:special[0][2]]
                print((nind,imdata.shape))
                dt[:,:,dind]+=imdata
                dind+=1
                nind+=skip
                
            #add coordinates to dt matrix
            for i in range(self.nxpts):
                dt[:,i,0]=np.ones((self.nypts))*self.xvals[i]
            for j in range(self.nypts):
                dt[j,:,1]=np.ones((self.nxpts))*self.yvals[j]            
            
            



        else:

            nanopre="/"
            nanop2=""
            if sdpath+"/xmap1channel00" in Sh5:
                nanopre="/xmap1"
                nanop2="xmap1"

            #for flyscan:
            if sdpath+nanopre+"channel00" in Sh5: 
                validrdpath=["00"]
                dataroots=[sdpath+nanopre+"channel00"]
                for x in range(15):
                    if sdpath+nanopre+"channel"+str(x+1).zfill(2) in Sh5:
                        dataroots.extend([sdpath+nanopre+"channel"+str(x+1).zfill(2)])
                        validrdpath.append(str(x+1).zfill(2))
                datapaths=[]
                for dr in dataroots:
                    if dr in Sh5:
                        print (dr)
                        datapaths.append(dr)
                
                if len(datapaths) == 0: 
                    print ("No readable data in hdf file")
                    Sh5.close()
                    return
                if len(datapaths) > 1:
                    #multiple choices...
        
                    scadialog=Pmw.Dialog(parent=root,title="SCA Selection",buttons=('OK','Cancel'))
                    scaselbox=Pmw.TtkRadioSelect(parent=scadialog.interior(),labelpos='n',label_text="Please select detector channel to load")
                    for sb in datapaths:
                        scaselbox.add(sb.split("/")[-1])
                    scaselbox.add("SUM")    
                    scaselbox.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=5)
                    scaselect=scadialog.activate()
                    if scaselect == "Cancel" : readpath="SUM"
                    else:
                        dsel=scaselbox.getvalue()
                        if dsel != 'SUM':
                            readpath=dsel[-2:]
                        else: readpath=dsel
                else: 
                    readpath=datapaths[0][-2:]
        
                print (readpath)
                readpath=readpath.encode("ascii","ignore")
        
                #get scalar data
                labels=["icr"+readpath,"ocr"+readpath,"livetime"+readpath,"deadtime"+readpath]
                #transfer data
                        
                self.labels=labels
                self.channels=len(self.labels)
        
                rlabels=[nanop2+"icr",nanop2+"ocr",nanop2+"livetime",nanop2+"deadtime"]        
                if readpath == 'SUM':
                    readiter=validrdpath#["00","01","02","03"]
                else:
                    readiter=[readpath]
                
                comments="None in file"
                self.comments=comments
                
                if sdpath+"/sxpos" in Sh5:
                    xpositions= Sh5[sdpath+"/sxpos"]   
                    ypositions= Sh5[sdpath+"/szpos"]
                elif sdpath+"/COD_GONIO_Tz1" in Sh5:
                    xpositions= Sh5[sdpath+"/COD_GONIO_Ts2"]   
                    ypositions= Sh5[sdpath+"/COD_GONIO_Tz1"]
                elif sdpath+"/multiaxis_tx" in Sh5:
                    xpositions= Sh5[sdpath+"/multiaxis_tx"]
                    ypositions= Sh5[sdpath+"/multiaxis_tz2"]
                elif sdpath+"/Tx" in Sh5:
                    xpositions= Sh5[sdpath+"/Tx"]
                    ypositions= Sh5[sdpath+"/Tz"]
                else:
                    xpositions= Sh5[sdpath+"/xpos"]   
                    ypositions= Sh5[sdpath+"/zpos"]
                                    
                
                print((xpositions.shape))
                
                start1= np.average(xpositions[:,0])
                start2= np.average(ypositions[0,:])
                stop1= np.average(xpositions[:,xpositions.shape[1]-1])
                stop2= np.average(ypositions[ypositions.shape[0]-1,:])
                step1=(stop1-start1)/(xpositions.shape[1]-1)
                step2=(stop2-start2)/(ypositions.shape[0]-1)
                
                print((start1,stop1,step1))
                print((start2,stop2,step2))
                
                dtshaped=list(xpositions.shape)
                dtshaped.extend([self.channels+2])
                dt=np.zeros(tuple(dtshaped),dtype=np.float32)        
                
                ind=2
                for l in rlabels:
                    for n in readiter:
                        if sdpath+"/"+l+n in Sh5:
                            sfitdata=Sh5[sdpath+"/"+l+n][()]
                            print((l,n,sfitdata.shape))
                        else:
                            print(("WARN: ",sdpath+"/"+l+n))
                            sfitdata=np.np.zeros(tuple(dtshaped[0:2]))
                        dt[:,:,ind]+=sfitdata
                    ind+=1
        
                if start1>stop1 and step1>0: step1=-step1
                if start1<stop1 and step1<0: step1=-step1
                if start2>stop2 and step2>0: step2=-step2    
                if start2<stop2 and step2<0: step2=-step2                
        
                if step1>1e-6:
                    self.xvals=globalfuncs.frange(start1,end=stop1,inc=step1)
                else:
                    self.xvals=globalfuncs.frange(0,xpositions.shape[1],inc=1.0)
                if step2>1e-6:
                    self.yvals=globalfuncs.frange(start2,end=stop2,inc=step2)
                else:
                    self.yvals=globalfuncs.frange(0,xpositions.shape[0],inc=1.0)
                    
                if len(self.xvals)>dtshaped[1]:self.xvals=self.xvals[:-1]        
                if len(self.yvals)>dtshaped[0]:self.yvals=self.yvals[:-1]        
        
                print ("WARNING! FORCING X ARRAYS TO FIT.")        
                if len(self.xvals)!=dtshaped[1]: self.xvals=self.xvals[:dtshaped[1]]
                print ("WARNING! FORCING Y ARRAYS TO FIT.")        
                if len(self.yvals)!=dtshaped[0]: self.yvals=self.yvals[:dtshaped[0]]
                
                
                self.nxpts=len(self.xvals)
                self.nypts=len(self.yvals)
                
                print((self.nxpts,self.nypts))
        
                #add coordinates to dt matrix
                for i in range(self.nxpts):
                    dt[:,i,1]=np.ones((self.nypts))*self.xvals[i]
                for j in range(self.nypts):
                    dt[j,:,0]=np.ones((self.nxpts))*self.yvals[j]
        
        
                #extract MCA data
                fnout=os.path.splitext(fn)[0]+"_mca.hdf5"
                if wd[0]!='':
                    fnout=os.path.join(wd[0],os.path.splitext(os.path.split(fn)[1])[0]+"_mca.hdf5")
                
                print (fnout)        
                if not os.path.exists(fnout):
                    fout=h5py.File(fnout,'w')
                    groupout=fout.create_group("main")
            
                    rawmcadata=Sh5[sdpath+nanopre+"channel00"][()]
                    
                    print((rawmcadata.shape))
                    maxpoints=rawmcadata.shape[0]*rawmcadata.shape[1]
                    mcadata=groupout.create_dataset("mcadata",(maxpoints,rawmcadata.shape[2]),maxshape=(None,rawmcadata.shape[2]),dtype='int',compression="gzip",compression_opts=4)

                    for mci in readiter:                            
                        rawmcadata=Sh5[sdpath+nanopre+"channel"+mci][()]
                        print (mci)
                        for j in range(self.nypts):
                            for i in range(self.nxpts):
                                mcadata[i+j*rawmcadata.shape[1]]=rawmcadata[j,i,:]
            
                    fout.flush() 
                    fout.close()
            
            else: #raster format XMAP
                datapaths=[]
                spectrumpath=[]
                for dnum in range(35):
                    droot=sdpath+"/data_"+str(dnum).rjust(2,'0')
                    if droot in Sh5:
                        print (droot)
                        #now check data type
                        if Sh5[droot].attrs["interpretation"]=="spectrum":
                            spectrumpath.append(droot)
                            print ("spec")
                        else:                          
                            datapaths.append(droot)
                if len(datapaths) == 0: 
                    print ("No readable data in hdf file")
                    Sh5.close()
                    return
                if len(datapaths) > 1:
                    #multiple choices...
                    pathsdict={}
                    scadialog=Pmw.Dialog(parent=root,title="Channel Selection",buttons=('OK','Cancel'))
                    scaselbox=Pmw.TtkRadioSelect(parent=scadialog.interior(),labelpos='n',
                                                 buttontype="checkbutton",orient="vertical",
                                                 label_text="Please select detector channel(s) to load")
                    for sb in datapaths:
                        text=Sh5[sb].attrs["long_name"].split("/")[-1].replace("_",".")  
                        #text=sb.split("/")[-1].replace("_",".")
                        scaselbox.add(text)
                        pathsdict[text]=sb
                    scaselbox.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=5)
                    scaselect=scadialog.activate()
                    if scaselect == "Cancel" :
                        print ("load cancelled")
                        Sh5.close()
                        return                        
                    else:
                        readpath=[]
                        labels=[]
                        for rp in scaselbox.getvalue():
                            readpath.append(pathsdict[rp].encode("ascii","ignore"))
                            labels.append(rp.encode("ascii","ignore"))
                print (readpath)
        
                #get scalar data
                        
                self.labels=labels
                self.channels=len(self.labels)
                print (labels)
#                rlabels=["icr","ocr","livetime","deadtime"]        
#                if readpath == 'SUM':
#                    readiter=["00","01","02","03"]
#                else:
#                    readiter=[readpath]
                
                comments="None in file"
                self.comments=comments
            
                xpositions= Sh5[sdpath+"/trajectory_1_1"]   
                ypositions= Sh5[sdpath+"/trajectory_2_1"]
                                    
                print((xpositions.shape))
                
                start1= np.average(xpositions[0])
                start2= np.average(ypositions[0])
                stop1=xpositions[-1]
                stop2=ypositions[-1]
                step1=(stop1-start1)/(xpositions.shape[0]-1)
                step2=(stop2-start2)/(ypositions.shape[0]-1)
              
#                start1= np.average(xpositions[:,0])
#                start2= np.average(ypositions[0])
#                stop1= np.average(xpositions[:,xpositions.shape[1]-1])
#                stop2=ypositions[-1]
#                step1=(stop1-start1)/(xpositions.shape[1]-1)
#                step2=(stop2-start2)/(ypositions.shape[0]-1)
                
                print((start1,stop1,step1))
                print((start2,stop2,step2))
                
                dtshaped=[len(ypositions),len(xpositions)]
                dtshaped.extend([self.channels+2])
                dt=np.zeros(tuple(dtshaped),dtype=np.float32)        
                
                for ind in range(len(readpath)):
                    sfitdata=Sh5[readpath[ind]][()]
                    print((readpath[ind],sfitdata.shape))                    
                    dt[:,:,ind+2]+=sfitdata
        
                if start1>stop1 and step1>0: step1=-step1
                if start1<stop1 and step1<0: step1=-step1
                if start2>stop2 and step2>0: step2=-step2    
                if start2<stop2 and step2<0: step2=-step2    
        
                self.xvals=globalfuncs.frange(start1,end=stop1,inc=step1)
                self.yvals=globalfuncs.frange(start2,end=stop2,inc=step2)
                
                if len(self.xvals)>dtshaped[1]:self.xvals=self.xvals[:-1]        
                if len(self.yvals)>dtshaped[0]:self.yvals=self.yvals[:-1]        
        
                print ("WARNING! FORCING X ARRAYS TO FIT.")        
                if len(self.xvals)!=dtshaped[1]: self.xvals=self.xvals[:dtshaped[1]]
                print ("WARNING! FORCING Y ARRAYS TO FIT.")        
                if len(self.yvals)!=dtshaped[0]: self.yvals=self.yvals[:dtshaped[0]]
                
                
                self.nxpts=len(self.xvals)
                self.nypts=len(self.yvals)
                
                print((self.nxpts,self.nypts))
        
                #add coordinates to dt matrix
                for i in range(self.nxpts):
                    dt[:,i,1]=np.ones((self.nypts))*self.xvals[i]
                for j in range(self.nypts):
                    dt[j,:,0]=np.ones((self.nxpts))*self.yvals[j]
        
        
                #extract MCA data
                if len(spectrumpath)>0:

                    fnout=os.path.splitext(fn)[0]+"_mca.hdf5"
                    if wd[0]!='':
                        fnout=os.path.join(wd[0],os.path.splitext(os.path.split(fn)[1])[0]+"_mca.hdf5")
                    
                    print (fnout)        
                    if not os.path.exists(fnout):
                        fout=h5py.File(fnout,'w')
                        groupout=fout.create_group("main")
                        rawmcadata= []
                        for mp in spectrumpath:
                            rawmcadata.append(Sh5[mp][()])
                        
                        print((rawmcadata[0].shape))
                        maxpoints=rawmcadata[0].shape[0]*rawmcadata[0].shape[1]
                        mcadata=groupout.create_dataset("mcadata",(maxpoints,rawmcadata[0].shape[2]),maxshape=(None,rawmcadata[0].shape[2]),dtype='int',compression="gzip",compression_opts=4)
                        
                        for j in range(self.nypts):
                            for i in range(self.nxpts):
                                for m in rawmcadata:
                                    mcadata[i+j*rawmcadata[0].shape[1]]+=m[j,i,:]
                
                        fout.flush() 
                        fout.close()
            



    
        Sh5.close()
    
              
        #open new hdf

        print((self.nypts,self.nxpts,self.channels+2,dt.shape))
        print((self.labels))
           
        #dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))
        #print dataShaped.shape

        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)

        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dt,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
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
## ALS 10.3.2 DATA
####################################

class ALS1032(SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='ALS1032'
        fid=open(fn)
        lines=fid.read().split('\n')
        fid.close()
        self.comments=lines[0]
        if (lines[1].split()[0]).lower() =='subtitle':
            self.comments=self.comments+lines[1]
            sl=2
        else:
            sl=1
        xrange=[float(lines[sl].split()[4]),float(lines[sl].split()[5])]        
        yrange=[float(lines[sl+1].split()[4]),float(lines[sl+1].split()[5])]
        self.nxpts=int(lines[sl+3].split()[5])
        self.nypts=int(lines[sl+3].split()[6])
        self.energy=float(lines[sl+6].split()[2])
        self.channels=int(lines[sl+7].split()[3])
        self.xvals=list(range(int(xrange[0]),int(xrange[1]),int(float(lines[sl+4].split()[3]))))
        self.yvals=list(range(int(yrange[0]),int(yrange[1]),int(float(lines[sl+4].split()[4]))))
        #odd number of xpts!
        xtrue=len(self.xvals)
        xdiff=xtrue-self.nxpts
        xst=int(xdiff/2)
        xen=xtrue-xst
        self.xvals=self.xvals[xst:xen]
        dt=np.zeros((self.nypts,self.nxpts,self.channels+2),dtype=np.float32)
        self.labels=[]
        for i in range(10,10+self.channels):
            self.labels.append(lines[i].split()[2])
        j=0
        while lines[j][:2]!='I0':
            j=j+1
        j=j+1
        k=0
        for m in range(self.channels):
            for n in range(self.nypts):
                for o in range(self.nxpts):
                    buf=lines[j+n+self.nypts*m].split()[o]
                    dt[n,o,m+2]=float(buf)
        
        #array-ize data
        dataShaped=dt

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.xvals=np.array(self.xvals)
        self.yvals=np.array(self.yvals)
##        print self.xvals.shape
##        print self.yvals.shape
##        print self.labels
##        print self.channels

        self.isVert=0

        print((self.nxpts,len(self.xvals),self.nypts,len(self.yvals)))

        hdf5xd=self.hdf5group.create_dataset("xdata",(self.nxpts,),dtype='float',data=self.xvals[:-1])
        hdf5yd=self.hdf5group.create_dataset("ydata",(self.nypts,),dtype='float',data=self.yvals)
        hdf5xd.attrs.create("pts",self.nxpts)
        hdf5yd.attrs.create("pts",self.nypts)
        self.hdf5group.attrs.create("channels",self.channels)
        self.hdf5group.attrs.create("origin",self.type)
        self.hdf5group.attrs.create("isVert",self.isVert)
        self.hdf5group.attrs.create("labels",self.labels)
        self.hdf5group.attrs.create("comments",self.comments)
        self.hdf5group.attrs.create("energy",self.energy)


class ALS1032_fmt2(SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='ALS1032'
        fid=open(fn)
        lines=fid.read().split('\n')
        fid.close()
        
        tl=0
        for i in range(len(lines)):
            if lines[i].split()[0]=='Title':
                tl=i
                break
        stl=0
        for i in range(len(lines)):
            if lines[i].startswith('Scan type'):
                stl=i
                break

        self.comments=lines[tl]
        if (lines[tl+1].split()[0]).lower() =='subtitle':
            self.comments=self.comments+lines[1]
#            sl=4+tl
#        else:
#            sl=3+tl
        sl=stl+1
        
        xrange=[float(lines[sl].split()[4]),float(lines[sl].split()[5])]        
        yrange=[float(lines[sl+1].split()[4]),float(lines[sl+1].split()[5])]
        self.nxpts=int(lines[sl+3].split()[5])
        self.nypts=int(lines[sl+3].split()[6])
        self.energy=float(lines[sl+6].split()[2])
        self.channels=int(lines[sl+8].split()[3])
        self.xvals=list(range(int(xrange[0]),int(xrange[1]),int(float(lines[sl+4].split()[3]))))
        self.yvals=list(range(int(yrange[0]),int(yrange[1]),int(float(lines[sl+4].split()[4]))))
        #odd number of xpts!
        xtrue=len(self.xvals)
        xdiff=xtrue-self.nxpts
        xst=int(xdiff/2)
        xen=xtrue-xst
        self.xvals=self.xvals[xst:xen]
        dt=np.zeros((self.nypts,self.nxpts,self.channels+2),dtype=np.float32)
        self.labels=[]
        for i in range(sl+10,sl+10+self.channels):
            self.labels.append(lines[i].split()[2])
        j=0
        while lines[j][:2]!='I0':
            j=j+1
        j=j+1
        k=0
        for m in range(self.channels):
            for n in range(self.nypts):
                for o in range(self.nxpts):
                    buf=lines[j+n+self.nypts*m].split()[o]
                    dt[n,o,m+2]=float(buf)
        
        #array-ize data
        dataShaped=dt

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.xvals=np.array(self.xvals,dtype='float')
        self.yvals=np.array(self.yvals,dtype='float')
##        print self.xvals.shape
##        print self.yvals.shape
##        print self.labels
##        print self.channels

        self.isVert=0

        print((self.nxpts,len(self.xvals),self.nypts,len(self.yvals)),self.xvals.shape,self.yvals.shape)
        if len(self.xvals)>self.nxpts:
            xsd=self.xvals[:-1]
        else:
            xsd=self.xvals
        hdf5xd=self.hdf5group.create_dataset("xdata",(self.nxpts,),dtype='float',data=xsd)
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
## PNC-CAT DATA
####################################

class PNC(SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='PNC-CAT'
        fid=open(fn)
        lines=fid.read().split('\n')
        fid.close()
        comtemp=[]
        dt=[]
        self.xvals=[]
        self.yvals=[]
        self.labels=[]
        self.channels=0
        self.energy=1
        i=0
        com=0
        dat=0
        savej=[]
        for line in lines:
            if com==1:
                comtemp.append(line)
            if dat>0:
                ttemp=[]
                j=0
                k=0
                for d in line.split():
                    if savej[j]!=5:
                        ttemp.append(float(d))
                    if dat<=self.nxpts and savej[j]==8:
                        self.xvals.append(float(d))
                    if dat==1 and savej[j]==5:
                        self.energy=float(d)
                    if int(math.fmod(dat,self.nxpts))==0 and savej[j]==9:
                        self.yvals.append(float(d))
                    j=j+1
                if ttemp!=[]: dt.append(ttemp)    
                dat=dat+1
            if len(line.split())>2 and line.split()[1]=='User':
                com=1
            if len(line.split())>2 and line.split()[1]=='Detector':
                com=0
                self.comments=''
                comtemp.pop()
                for c in comtemp:
                    self.comments=self.comments+c+'\n'
            if len(line.split())>2 and line.split()[1]=='Column':
                ttemp=lines[i+1]
                j=0
                savej=[]
                for hh in ttemp.split('#')[1].split('  '):
                    h=hh.lstrip()
                    if h[0:6]=='KB Hor' or h[0:6]=='KB_Hor' or h=='AeroTechH':
                        savej.append(8)
                    if h[0:6]=='KB Ver' or h[0:6]=='KB_Ver' or h=='AeroTechV':
                        savej.append(9)
                    if h[0:12]=='pncaux3:mono' or h[0:10]=='pncid:mono':
                        savej.append(5)
                    if h!='' and h[0:2]!='KB' and h[0:5]!='AeroT' and h[0:12]!='pncaux3:mono' and h[0:10]!='pncid:mono':
                        self.labels.append(h)
                        savej.append(1)
                        self.channels=self.channels+1
                    j=j+1
            if len(line.split())>2 and line.split()[0]=='*':
                dat=1
                self.nxpts=int(line.split()[4])
                self.nypts=int(line.split()[5])
                monct=0
                for c in savej:
                    if c==5: monct=monct+1
                if self.channels!=int(line.split()[3])-monct:
                    print(('WARNING: File size mismatch: ',self.channels,line.split()[3]))
            i=i+1    
        #array-ize data
        self.xvals=np.array(self.xvals)
        self.yvals=np.array(self.yvals)
        dt=np.array(dt)
        print((self.xvals.shape,self.yvals.shape,dt.shape))
        dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))        

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0


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
## Raw Image type
####################################

class fromRawImage(SuperClass):

    def __init__(self,fn,temp,wd,t=False):
        self.type='Image'
        if not t:
            im=MainImage.open(fn)
            im.load()
            img=im.convert('L')
            (self.nxpts,self.nypts)=img.size
            graw=np.array(img)
            raw=np.array(im)
            print (raw.shape)
            if raw.shape[2]==4:
                raw[:,:,3]=graw
            else:
                zraw=np.zeros((raw.shape[0],raw.shape[1],raw.shape[2]+1),dtype=np.float32)
                zraw[:,:,0:3]=raw
                zraw[:,:,3]=graw
                raw=zraw
                raw=raw[::-1,:,:]
            self.channels=4        
            self.labels=['ImageCH1','ImageCH2','ImageCH3','ImageGREY']
        else:
            im=ndimage.imread(fn,mode='I')
            raw=im
            (self.nypts,self.nxpts)=im.shape
            self.channels=1        
            self.labels=['ImageCH1']
            raw=np.array(raw)
            raw=raw[::-1,:]
        self.comments='Data from '+fn
        self.energy=1
        self.xvals=np.arange(int(self.nxpts))
        self.yvals=np.arange(int(self.nypts))        
        
        dataShaped=np.ones((self.nypts,self.nxpts,self.channels+2),dtype=np.float32)
        print (raw.shape,dataShaped.shape)
        dataShaped[:,:,2:]=raw
        xv,yv=np.meshgrid(np.arange(self.nxpts),np.arange(self.nypts))
        print (xv.shape,yv.shape)
        dataShaped[:,:,0]=xv
        dataShaped[:,:,1]=yv
        #for i in self.yvals:
        #    for j in self.xvals:
        #        dataShaped[i,j,0]=j
        #        dataShaped[i,j,1]=i

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(25000,25000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## NSLS ASCII type
####################################

class NSLSASCII(SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='NSLS'
        fid=open(fn)
        lines=fid.read().split('\n')
        fid.close()
        
        dt=[]
        self.xvals=[]
        self.yvals=[]
        self.labels=[]
        self.channels=0
        self.energy=1
        self.comments=''
        i=0
        lab=0
        xv=0
        dat=0
        ypos=0
        savej=[]
        for line in lines:
            i+=1
            if i<3:
                self.comments=self.comments+line+'\n'
            if i<6 and line.rfind('columns:')>0:
                self.nxpts=int(line.split()[-1])
            if i<6 and line.rfind('rows:')>0:
                self.nypts=int(line.split()[-1])
            if line[0:7]=='Y Dist.':
                dat=1
                ypos=float(line.split()[-1])
                self.yvals.append(ypos)
                continue
            if dat==1 and lab==0 and line[0:7]=='X Dist.':
                self.labels=line.split(',')
                self.labels.pop(0)
                self.labels.pop()
                continue
            if dat:
                if line.split()==[]:
                    dat=0
                    xv=1
                    continue
                vals=line.split(',')
                dattemp=[ypos]
                for v in vals:
                    if v!='': dattemp.append(float(v))
                if not xv:
                    self.xvals.append(float(vals[0]))
                dt.append(dattemp)
        self.channels=len(self.labels)
        self.xvals=np.array(self.xvals)
        self.yvals=np.array(self.yvals)
        dt=np.array(dt)       
        dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)


        self.isVert=0

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
## NSLS BINARY type
####################################

class NSLSBINARY(SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='NSLS'
        fid=open(fn,"rb")
        data=fid.read()
        fid.close()
        
        dt=[]
        self.xvals=[]
        self.yvals=[]
        self.labels=[]
        self.channels=0
        self.energy=1
        self.comments=''
        i=0
        lab=0
        xv=0
        dat=0
        ypos=0

        #parsed read
        i=0
        p='>1i'
        rows=struct.unpack_from(p,data,i)[0]
        i+=struct.calcsize(p)
        cols=struct.unpack_from(p,data,i)[0]
        self.nypts=rows
        self.nxpts=cols
        i+=struct.calcsize(p)
        chans=struct.unpack_from(p,data,i)[0]
        i+=struct.calcsize(p)
        unk1=struct.unpack_from(p,data,i)[0]
        i+=struct.calcsize(p)
        unk2=struct.unpack_from(p,data,i)[0]
        i+=struct.calcsize(p)
        unk3=struct.unpack_from(p,data,i)[0]
        i+=struct.calcsize(p)
        
        print((rows,cols,chans,unk1,unk2,unk3))
        
        p='>1f'
        poscolstart=struct.unpack_from(p,data,i)[0]
        i+=struct.calcsize(p)
        poscolend=struct.unpack_from(p,data,i)[0]
        i+=struct.calcsize(p)
        posrowstart=struct.unpack_from(p,data,i)[0]
        i+=struct.calcsize(p)
        posrowend=struct.unpack_from(p,data,i)[0]
        i+=struct.calcsize(p)
        
        print((poscolstart,poscolend))
        print((posrowstart,posrowend))
        steprow=(posrowend-posrowstart)/(rows-1)
        stepcol=(poscolend-poscolstart)/(cols-1)
        self.yvals=globalfuncs.frange(posrowstart,end=posrowend,inc=steprow)
        self.xvals=globalfuncs.frange(poscolstart,end=poscolend,inc=stepcol)        
        print((len(self.xvals),len(self.yvals)))
        
        p='>2i'
        comchars=struct.unpack_from(p,data,i)[0]
        i+=struct.calcsize(p)
        #print comchars
        p='>'+str(comchars)+'s'
        self.comments=struct.unpack_from(p,data,i)
        i+=bytesize(struct.calcsize(p))
        
        p='>2i'
        mot1chars=struct.unpack_from(p,data,i)[0]
        i+=struct.calcsize(p)
        #print mot1chars
        p='>'+str(mot1chars)+'s'
        motor1=struct.unpack_from(p,data,i)
        i+=bytesize(struct.calcsize(p))
        #print motor1
        
        p='>2i'
        mot2chars=struct.unpack_from(p,data,i)[0]
        i+=struct.calcsize(p)
        #print mot2chars
        p='>'+str(mot2chars)+'s'
        motor2=struct.unpack_from(p,data,i)
        i+=bytesize(struct.calcsize(p))
        #print motor2
        
        for h in range(chans):
            p='>2i'
            c=struct.unpack_from(p,data,i)[0]
            i+=struct.calcsize(p)
            p='>'+str(c)+'s'
            ct=struct.unpack_from(p,data,i)[0]
            i+=bytesize(struct.calcsize(p))
            print (ct)
            self.labels.append(ct)
        self.channels=chans
        
        p='>2i'
        unk4=struct.unpack_from(p,data,i)
        i+=bytesize(struct.calcsize(p))
        print (unk4)

        dtshaped=[self.nypts,self.nxpts]
        dtshaped.extend([self.channels+2])
        dataShaped=np.zeros(tuple(dtshaped),dtype=np.float32) 
        #add coordinates to dt matrix
        for i in range(self.nxpts):
            print (i)
            dataShaped[:,i,1]=np.ones((self.nypts))*self.xvals[i]
        for j in range(self.nypts):
            dataShaped[j,:,0]=np.ones((self.nxpts))*self.yvals[j]
            
        #data
        p='>'+str(rows*cols)+'i'
        for h in range(chans):
            dc=struct.unpack_from(p,data,i)
            i+=struct.calcsize(p)
            dc=np.array(dc)
            dc=dc.reshape([self.nypts,self.nxpts])
            dataShaped[:,:,h+2]=dc
            
        print ('END?')
        
        p=">8c"
        print((struct.unpack_from(p,data,i)))
        i+=struct.calcsize(p)
        print((i, len(data)))


        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)


        self.isVert=0

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
## BL 6-2 TXM type
####################################

class BL62TXM(SuperClass):

    def __init__(self,fn,temp,wd):        
        self.type='BL62TXM'
        fid=open(fn)
        l1=fid.readline()
        l2=fid.readline()
        lines=fid.read().split('\n')
        fid.close()
        
        dt=[]
        self.nxpts=int(l1.split()[0])
        self.nypts=int(l1.split()[1])
        self.xvals=np.arange(int(l1.split()[0]))
        self.yvals=np.arange(int(l1.split()[1]))
        self.labels=l2.split()
        self.channels=int(l1.split()[2])
        self.energy=1
        self.comments=''
        #process data block
        for l in lines:
            ttemp=[]
            if len(l.split())<1: continue
            i=int(l.split()[0])
            ttemp.append(float(i%self.nxpts))
            ttemp.append(float(i/self.nypts))
            for d in l.split()[1:]:
                ttemp.append(float(d))
            if ttemp!=[]:
                dt.append(ttemp)

        dt=np.array(dt)
        #print dt.shape,self.nypts,self.nxpts,self.channels
        dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))

        print((dataShaped.shape))
        #JOY Q
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## ESRF EDF type
####################################

class EDFload(SuperClass):
    
    def __init__(self,fn,temp,wd):
        self.type='EDF'

        dt=[]
        self.xvals=[]
        self.yvals=[]
        self.labels=[]
        self.channels=0
        self.energy=1
        self.comments=''        

        img=fabio.open(fn)
        self.channels=img.nframes
        self.xvals=list(range(img.dim2))
        self.yvals=list(range(img.dim1))
        self.nypts=len(self.yvals)
        self.nxpts=len(self.xvals)        
        
        dtshaped=list(img.dims)
        dtshaped.extend([self.channels+2])
        dt=np.zeros(tuple(dtshaped),dtype=np.float32)        
        
        #add coordinates to dt matrix
        for i in range(self.nxpts):
            dt[:,i,1]=np.ones((self.nypts))*self.xvals[i]
        for j in range(self.nypts):
            dt[j,:,0]=np.ones((self.nxpts))*self.yvals[j]

        print((img.dims,img.data.shape))
        
        for i in range(self.channels):
            self.labels.append("Ch"+str(i))
            dt[:,:,i+2]=np.transpose(img.getframe(i).getData())


        dt=np.array(dt)       
        dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## Diamond RGB type
####################################

class DIAMOND_RGB(SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='RGB'
        fid=open(fn)
        lines=fid.read().split('\n')
        fid.close()
        
        dt=[]
        self.xvals=[]
        self.yvals=[]
        self.labels=[]
        self.channels=0
        self.energy=1
        self.comments=''
        i=0
        lab=0
        xv=''
        yv=''
        apx=1
        dat=0
        ypos=0
        savej=[]
        for line in lines:
            i+=1
            if i==1:
                dat=1
                for l in line.split():
                    if l not in ["row","ROW","column","COLUMN"]:
                        self.labels.append(l)
                continue                
            if i==2:
                yv=line.split()[0]
                self.yvals.append(float(line.split()[0]))
            if dat:
                if line.split()==[]:
                    continue
                vals=line.split()
                if vals[0]==yv and apx:
                    self.xvals.append(float(vals[1]))
                if vals[0]!=yv:
                    self.yvals.append(float(vals[0]))
                    yv=vals[0]
                    apx=0
                dattemp=[]
                for v in vals:
                    if v!='': dattemp.append(float(v))
                    
                dt.append(dattemp)
        self.channels=len(self.labels)
        self.nypts=len(self.yvals)
        self.nxpts=len(self.xvals)
        self.xvals=np.array(self.xvals)
        self.yvals=np.array(self.yvals)
        dt=np.array(dt)       
        dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## APS MRCAT (APS 10ID) Format
####################################

class MRCAT(SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='MRCAT'
        fid=open(fn)
        lines=fid.read().split('\n')
        fid.close()

        print ("MRCAT")
        
        dt=[]
        self.xvals=[]
        self.yvals=[]
        self.labels=[]
        self.channels=0
        self.energy=1
        self.comments=''
        i=0
        lab=0
        xv=''
        yv=''
        apx=1
        dat=0
        ypos=0
        savej=[]
        for line in lines:
            i+=1
            if i==1:
                nh=int(line.split()[-1])
                continue                
            if i>nh:
                if not dat:
                    dat=1
                    for l in line.split():
                        if l!='#' and l[0]!='%' and l!='=':
                            if l not in ["sam_hor","sam_vert"]:
                                self.labels.append(l)
                    continue
                if i==nh+2:
                    yv=line.split()[0]
                    self.yvals.append(float(line.split()[0]))
                if dat:
                    if line.split()==[]:
                        continue
                    vals=line.split()
                    if vals[0]==yv and apx:
                        self.xvals.append(float(vals[1]))
                    if vals[0]!=yv:
                        self.yvals.append(float(vals[0]))
                        yv=vals[0]
                        apx=0
                    dattemp=[]
                    for v in vals:
                        if v!='': dattemp.append(float(v))
                        
                    dt.append(dattemp)
        self.channels=len(self.labels)
        self.nypts=len(self.yvals)
        self.nxpts=len(self.xvals)
        self.xvals=np.array(self.xvals)
        self.yvals=np.array(self.yvals)
        dt=np.array(dt)
        print((self.channels,dt.shape,self.nxpts,self.nypts))
        print((self.labels))
        dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## ICP-MS Format
####################################

class ICPMS(SuperClass):
    
    def __init__(self,fn,temp,wd):
        self.type='ICPMS'
        fid=open(fn)
        lines=fid.read().split('\n')
        fid.close()

        dt=[]
        self.xvals=[]
        self.yvals=[]
        self.labels=[]
        self.channels=0
        self.energy=1
        self.comments=''
        yv=None
        xvadv=0

        for line in lines:
            if len(line)==0 or line=='' or line==' ': continue
            if len(line)>0 and line[0]=='#': continue
            if line[0]=='X' or line[0]=='x':
                for l in line.split():
                    if l=='X' or l=='Y' or l=='x' or l=='y': continue
                    self.channels+=1
                    self.labels.append(l)
                continue
            #append data
            ttemp=[]
            tl=line.split()
            if len(tl)<2: continue
            if yv==None:
                yv=float(tl[1])
                self.yvals.append(yv)
            elif yv!=float(tl[1]):
                xvadv=1
                yv=float(tl[1])
                self.yvals.append(yv)                
            if not xvadv:
                self.xvals.append(float(tl[0]))
            for l in tl:
                ttemp.append(float(l))
            dt.append(ttemp)
        self.nypts=len(self.yvals)
        self.nxpts=len(self.xvals)
        self.xvals=np.array(self.xvals)
        self.yvals=np.array(self.yvals)
        dt=np.array(dt)
        print((self.channels,dt.shape,self.nxpts,self.nypts))
        print((self.labels))
        dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## TOF ZIP'd ICP-MS Format
####################################

class ziptofms(SuperClass):

    def getZipIndex(self,fn):
        (fn,ext)=os.path.splitext(fn)
        index=fn.split('_')[-1]
        return int(index)
    
    def __init__(self,fn,temp,wd):
        self.type='TOF-MS'

        dt=[]
        self.xvals=[]
        self.yvals=[]
        self.labels=[]
        self.channels=0
        self.energy=1
        self.comments=''

        infile=zipfile.ZipFile(fn,mode='r')
        l=infile.namelist()
        sl=sortedcontainers.SortedDict()
        for n in l:
            (fn,ext)=os.path.splitext(n)
            if ext!='.csv': continue
            sl[self.getZipIndex(n)]=n
        
        dt=[]
        xminval=1e100
        xmaxval=0
        xinc=0
        yminval=1e100
        ymaxval=0
        yinc=0
        isVert=False

        for k in sl.keys():
            print (k,sl[k])            
            f=sl[k]
            with infile.open(f) as ofile:
                dl=ofile.readlines()
                dv=[]
                dr=False
                for dla in dl:
                    csv=dla.split(b',')
                    if len(csv)<1: continue
                    if dr is True:
                        ttemp=list(map(float,csv))
                        nd=ttemp[1:]
                        nd.append(ttemp[0])
                        dv.append(nd)
                        xminval=min(xminval,ttemp[1])
                        xmaxval=max(xmaxval,ttemp[1])                            
                        yminval=min(yminval,ttemp[2])
                        ymaxval=max(ymaxval,ttemp[2])  
                        #print (nd)
                    if ( csv[0].rfind(b'Cycle'))>-1:
                        if self.labels == []:
                            l1=list(map(bytes.decode,csv))
                            labels=list(map(str.strip,l1))
                            self.labels=labels[3:]
                            self.labels.append(labels[0])
                            self.channels=len(self.labels)
                            print (self.labels)
                            print (labels)
                        dr=True
                dt.append(dv)
                if xinc==0:
                    xinc = abs(dv[1][0]-dv[0][0])
                if xinc==0 and yinc!=0:
                    xinc = abs(dt[1][0][0]-dt[0][0][0])
                    isVert=True
                if yinc==0:
                    yinc = abs(dv[1][1]-dv[0][1])
                if yinc==0 and len(dt)>1:
                        yinc = abs(dt[1][0][1]-dt[0][0][1])
                    
        print (xminval,xmaxval,xinc)
        print (yminval,ymaxval,yinc)

        xvs = np.array(globalfuncs.frange(xminval,xmaxval,xinc))
        yvs = np.array(globalfuncs.frange(yminval,ymaxval,yinc))
        if not isVert:
            #xvs=np.arange(xminval,xmaxval,xinc)
            maxllen=len(xvs)
        else:
            #yvs=np.arange(yminval,ymaxval,yinc)
            maxllen=len(yvs)
        print (maxllen)

        dtemp=np.zeros((len(dt),maxllen,len(self.labels)+2))

        if not isVert:
            for i,j in enumerate(dt):
                xstart = j[0][0]
                xindex = np.argmin((xvs-xstart)**2)
                print (i,xindex,len(j))
                if xindex+len(j)>maxllen:
                    xindex=xindex-1
                dtemp[i][xindex:xindex+len(j),:]=j
        else:                       
            for i,j in enumerate(dt):
                ystart = j[0][1]
                yindex = np.argmin((yvs-ystart)**2)
                print (i,yindex,len(j))
                if yindex+len(j)>maxllen:
                    yindex=yindex-1
                dtemp[i][yindex:yindex+len(j),:]=j
            

        dt=np.array(dtemp)       
        
        print (dt.shape)
        infile.close()

        self.yvals=xvs #dt[0,:,1]
        self.xvals=yvs #dt[:,0,0]

        self.nypts=len(self.yvals)
        self.nxpts=len(self.xvals)

        print((self.channels,dt.shape,self.nxpts,self.nypts))
        print(len(self.labels))
        if not isVert:
            dataShaped=dt.transpose((1,0,2))
        else:
            dataShaped=dt
        #dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))

        print((dataShaped.shape))
        if self.nypts>dataShaped.shape[0]:
            self.yvals=self.yvals[:dataShaped.shape[0]]
            self.nypts=len(self.yvals)
        if self.nxpts>dataShaped.shape[1]:
            self.xvals=self.xvals[:dataShaped.shape[1]]
            self.nxpts=len(self.xvals)
        if self.nxpts<dataShaped.shape[1]:
            dataShaped=dataShaped[:,:self.nxpts,:]
            

        #think we need to swap 0,1 indices...
        tempa0 = dataShaped[:,:,0].copy()
        tempa1 = dataShaped[:,:,1].copy()
        dataShaped[:,:,0] = tempa1
        dataShaped[:,:,1] = tempa0
        
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        print(dataShaped.shape,self.nypts,self.nxpts,self.channels+2)
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(10000,10000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## AXIS XIM
####################################

class XIM(SuperClass):
    
    def __init__(self,fn,temp,wd):
        self.type='XIM'
        
        self.labels=['Chan1']
        self.channels=1
        self.xvals=[]
        self.yvals=[]
        self.energy=1
        self.comments=''      
        
        raw=np.fromfile(fn,sep=" ")

        fid=open(fn)
        lines=fid.read().split('\n')
        fid.close()

        print((raw.shape,len(lines)))
        
        
        self.nxpts=int(len(lines)-1)
        self.nypts=raw.shape[0]/self.nxpts
        
        startx=0
        stopx=self.nxpts     
        starty=0
        stopy=self.nypts     

        print((self.channels,raw.shape,self.nxpts,self.nypts))
     
   
        stepx=1
        stepy=1
        
        print((startx,stopx,stepx))
        print((starty,stopy,stepy))
        
        dtshaped=[self.nypts,self.nxpts]
        dtshaped.extend([self.channels+2])
        dataShaped=np.zeros(tuple(dtshaped),dtype=np.float32)        
        
        self.xvals=globalfuncs.frange(startx,end=stopx-stepx,inc=stepx)
        self.yvals=globalfuncs.frange(starty,end=stopy-stepy,inc=stepy)
        
        print((len(self.xvals),len(self.yvals)))

        #add coordinates to dt matrix
        for i in range(self.nxpts):
            dataShaped[:,i,1]=np.ones((self.nypts))*self.xvals[i]
        for j in range(self.nypts):
            dataShaped[j,:,0]=np.ones((self.nxpts))*self.yvals[j]

        rawShaped=np.reshape(raw,(self.nypts,self.nxpts,self.channels))    
        dataShaped[:,:,2:]=rawShaped
        
        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## AXIS Binary
####################################

class NCB(SuperClass):
    
    def __init__(self,fn,temp,wd):
        self.type='NCB'
        
        self.labels=[]
        self.xvals=[]
        self.yvals=[]
        self.energy=1
        self.comments=''      
        
        raw=np.fromfile(fn,dtype=np.dtype('int16').newbyteorder("="))

        print((np.where(raw==2107)))
        print((np.where(raw==2106)))
        print((np.where(raw==2112)))
        
        
        

        headfn=os.path.splitext(fn)[0]+".dat"
        fid=open(headfn,"rU")
        lines=fid.read().split('\n')
        fid.close()
        
        self.nxpts=int(lines[0].split()[0])
        self.nypts=int(lines[0].split()[1])
        scale=float(lines[0].split()[2])
        
        startx=float(lines[1].split()[0])
        stopx=float(lines[1].split()[1])        
        starty=float(lines[2].split()[0])
        stopy=float(lines[2].split()[1])     
        self.channels=int(lines[3])
        for i in range(self.channels):
            self.labels.append('eV'+lines[i+4].split()[0])

        print((self.channels,raw.shape,self.nxpts,self.nypts))
        print((self.labels        ))
   
        stepx=(stopx-startx)/(self.nxpts)
        stepy=(stopy-starty)/(self.nypts)
        
        print((startx,stopx,stepx))
        print((starty,stopy,stepy))
        
        dtshaped=[self.nxpts,self.nypts]
        dtshaped.extend([self.channels+2])
        dataShaped=np.zeros(tuple(dtshaped),dtype=np.float32)        
        
        self.xvals=globalfuncs.frange(startx,end=stopx-stepx,inc=stepx)
        self.yvals=globalfuncs.frange(starty,end=stopy-stepy,inc=stepy)
        
        print((len(self.xvals),len(self.yvals)))

        #add coordinates to dt matrix
        for i in range(self.nxpts):
            dataShaped[i,:,1]=np.ones((self.nypts))*self.xvals[i]
        for j in range(self.nypts):
            dataShaped[:,j,0]=np.ones((self.nxpts))*self.yvals[j]

        #rawShaped=np.reshape(raw,(self.nypts,self.nxpts,self.channels))   
        rawShaped=np.reshape(raw,(self.channels,self.nxpts,self.nypts))  
        rawShaped=rawShaped.transpose(1,2,0)
        dataShaped[:,:,2:]=rawShaped
        #dataShaped=dataShaped.transpose(1,0,2)
        
        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## 3 Column Text Format (from ESRF?)
####################################

class text3column(SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='3COLTXT'
        fid=open(fn)
        lines=fid.read().split('\n')
        fid.close()

        dt=[]
        self.xvals=[]
        self.yvals=[]
        self.labels=['Chan1']
        self.channels=1
        self.energy=1
        self.comments=''
        yv=None
        xvadv=0
        yfull=0

        for line in lines:
            if len(line)==0 or line=='' or line==' ': continue
            if len(line)>0 and line[0]=='#': continue
            #append data
            ttemp=[]
            tl=line.split()
            if len(tl)<2: continue
            xvadv=0
            if yv==None:
                yv=float(tl[1])
                self.yvals.append(yv)
            elif yv!=float(tl[1]):
                xvadv=1
                if not yfull:
                    self.yvals.append(float(tl[1]))
            else:
                yfull=1            
            if not xvadv:
                self.xvals.append(float(tl[0]))
            for l in tl:
                ttemp.append(float(l))
            dt.append(ttemp)
        self.nypts=len(self.yvals)
        self.nxpts=len(self.xvals)
        self.xvals=np.array(self.xvals)
        self.yvals=np.array(self.yvals)
        dt=np.array(dt)
        print((self.channels,dt.shape,self.nxpts,self.nypts,yv))
        #print self.labels
        dataShaped=np.reshape(dt,(self.nxpts,self.nypts,self.channels+2))

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## Agilent Format (FTIR Maps)
####################################

class agilentload(SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='AGILENT'
        (basefn,ext)=os.path.splitext(fn)
    
        [wavenumbers, data, width, height, filename]=read_agilent.agilentFile(fn)
        print (width,height,data.shape)
        ftirdata=data.reshape(data.shape[0]*data.shape[1],data.shape[2])
        xstep=1.
        ystep=1.

        dsum=np.sum(data,axis=2)

        self.xvals=[]
        self.yvals=[]
        self.labels=['FTIR']
        self.channels=1
        self.energy=1
        self.comments=''


        dims=list(dsum.shape)
        dims.extend([self.channels+2])
        dtshaped=np.zeros(tuple(dims),dtype=np.float32)
        dtshaped[:,:,2]=dsum

        self.nypts=height
        self.nxpts=width
        self.xvals=np.arange(self.nxpts)*xstep
        self.yvals=np.arange(self.nypts)*ystep

        print((self.channels,dtshaped.shape,self.nxpts,self.nypts))
        #add coordinates to dt matrix
        for i in range(self.nxpts):
            dtshaped[:,i,1]=np.ones((self.nypts))*self.xvals[i]
        for j in range(self.nypts):
            dtshaped[j,:,0]=np.ones((self.nxpts))*self.yvals[j]
            
        print((dtshaped.shape))

        #extract FTIR spectral data
        fnout=os.path.splitext(fn)[0]+"_ftir.hdf5"
        print (fnout)        
        if not os.path.exists(fnout):
            fout=h5py.File(fnout,'w')
            groupout=fout.create_group("main")
            
            print((ftirdata.shape))
            maxlen=len(wavenumbers)
            maxpoints=ftirdata.shape[0]#*rawmcadata.shape[1]
            mcadata=groupout.create_dataset("mcadata",(maxpoints,ftirdata.shape[1]),maxshape=(None,ftirdata.shape[1]),dtype='float',compression="gzip",compression_opts=4)
            mcadataxv=groupout.create_dataset("xdata",(maxlen),maxshape=(maxlen),dtype='float',compression="gzip",compression_opts=4)
           
            mcadata[:,:]=ftirdata
            mcadataxv[:]=wavenumbers
            fout.attrs.create("wavenumbers",wavenumbers)
            fout.flush() 
            fout.close()

        

        
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dtshaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## ENVI Format (FTIR Maps)
####################################

class enviload(SuperClass):

    def __init__(self,fn,temp,wd):
        self.type='ENVI'
        (basefn,ext)=os.path.splitext(fn)
        img=envi.open(fn,basefn+".dat")
        print (img)

        xstep=float(img.paramlist.psize[0])*1000.
        ystep=float(img.paramlist.psize[1])*1000.

        d=np.array(img[:,:,:])
        print((d.shape))
        ftirdata=d.reshape(d.shape[0]*d.shape[1],d.shape[2])        
        dsum=d.sum(axis=2)

        self.xvals=[]
        self.yvals=[]
        self.labels=['FTIR']
        self.channels=1
        self.energy=1
        self.comments=str(img.paramlist.desc)
        yv=None
        xvadv=0
        yfull=0

        dims=list(dsum.shape)
        dims.extend([self.channels+2])
        dtshaped=np.zeros(tuple(dims),dtype=np.float32)
        dtshaped[:,:,2]=dsum

        self.nypts=img.paramlist.nrows
        self.nxpts=img.paramlist.ncols
        self.xvals=np.arange(self.nxpts)*xstep
        self.yvals=np.arange(self.nypts)*ystep

        print((self.channels,dtshaped.shape,self.nxpts,self.nypts))
        #add coordinates to dt matrix
        for i in range(self.nxpts):
            dtshaped[:,i,1]=np.ones((self.nypts))*self.xvals[i]
        for j in range(self.nypts):
            dtshaped[j,:,0]=np.ones((self.nxpts))*self.yvals[j]
            
        print((dtshaped.shape))

        #extract FTIR spectral data
        fnout=os.path.splitext(fn)[0]+"_ftir.hdf5"
        print (fnout)        
        if not os.path.exists(fnout):
            fout=h5py.File(fnout,'w')
            groupout=fout.create_group("main")
            
            print((ftirdata.shape))
            maxlen=len(np.array(img.bands.centers))
            maxpoints=ftirdata.shape[0]#*rawmcadata.shape[1]
            mcadata=groupout.create_dataset("mcadata",(maxpoints,ftirdata.shape[1]),maxshape=(None,ftirdata.shape[1]),dtype='float',compression="gzip",compression_opts=4)
            mcadataxv=groupout.create_dataset("xdata",(maxlen),maxshape=(maxlen),dtype='float',compression="gzip",compression_opts=4)
            
            mcadata[:,:]=ftirdata
            mcadataxv[:]=np.array(img.bands.centers)
            
            fout.flush() 
            fout.close()

        

        
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dtshaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## imzML - MS Imaging Format
####################################

class imzmlLoad(SuperClass):
    
    def __init__(self,fn,temp,wd):
        self.type='IMZML'
        (basefn,ext)=os.path.splitext(fn)
        img=ImzMLParser(fn)
        print (img)
        
        xstep=float(img.imzmldict['pixel size x'])/1000
        ystep=float(img.imzmldict['pixel size y'])/1000
        
        xmax=float(img.imzmldict['max dimension x'])/1000
        ymax=float(img.imzmldict['max dimension y'])/1000
        
        sp = img.getspectrum(0)
        mzmid = (sp[0][0]+sp[0][-1])/2.0
        mzwid = mzmid - sp[0][0]
        speclen=len(sp[0])
        
        dall = pyimzml.ImzMLParser.getionimage(img,mzmid,mzwid)
        
        self.xvals=[]
        self.yvals=[]
        self.labels=['imzML']
        self.channels=1
        self.energy=1 
        mstypelist = img.metadata.pretty()['instrument_configurations']['instrumentConfiguration0']['components']
        self.comments=''
        for s in mstypelist:
            self.comments+=list(s.keys())[-1]+'  '
            
        self.nxpts = int(img.imzmldict['max count of pixels x'])
        self.nypts = int(img.imzmldict['max count of pixels y'])
        self.xvals=np.arange(self.nxpts)*xstep
        self.xvals=self.xvals+(xmax - self.xvals[-1])
        self.yvals=np.arange(self.nypts)*ystep
        self.yvals=self.yvals+(ymax - self.yvals[-1])
        
        dims=[self.nypts,self.nxpts,self.channels+2]
        dtshaped=np.zeros(tuple(dims),dtype=np.float32)
        dtshaped[:,:,2]=dall

        print((self.channels,dtshaped.shape,self.nxpts,self.nypts))
        
        #add coordinates to dt matrix
        for i in range(self.nxpts):
            dtshaped[:,i,1]=np.ones((self.nypts))*self.xvals[i]
        for j in range(self.nypts):
            dtshaped[j,:,0]=np.ones((self.nxpts))*self.yvals[j]

        print((dtshaped.shape))
        
        #extract m/z data
        fnout=os.path.splitext(fn)[0]+"_mz.hdf5"
        print (fnout)
        if not os.path.exists(fnout):
            fout=h5py.File(fnout,'w')
            groupout=fout.create_group("main")
            
            allspec=[]
            allmz=[]
            inx=[]
            maxlen = 0
            sti = 0
            endi = 0
            for ix, (x,y,z) in enumerate (img.coordinates):
                #print (x,y,ix)
                mz, intensities = img.getspectrum(ix)
                #print (x,y,ix,len(mz))
                #print (len(intensities),mz[0],mz[-1])
                maxlen = max(maxlen,len(intensities))
                allspec.append(intensities)
                allmz.append(mz)
                inx.append([y-1,x-1])
                if ix==0:
                    sti=mz[0]
                    endi=mz[-1]
                else:
                    sti=max(sti,mz[0])
                    endi=min(endi,mz[-1])
            print (sti,endi,maxlen)
            #fix spectra....
            newmz = globalfuncs.frange(sti,end=endi,inc=(endi-sti)/(maxlen-1))
            maxpoints = self.nxpts*self.nypts
            newspec=np.zeros((self.nypts,self.nxpts,maxlen))
            for (omz,osp,xyc) in zip(allmz,allspec,inx):
                newy = np.interp(newmz,omz,osp)
                newspec[xyc[0],xyc[1],:]=newy
            
            newspec = newspec.reshape(maxpoints,maxlen)

            print (newspec.shape)
            maxlen=len(newmz)
            mcadata=groupout.create_dataset("mcadata",(maxpoints,maxlen),maxshape=(None,maxlen),dtype='float',compression="gzip",compression_opts=4)
            mcadataxv=groupout.create_dataset("xdata",(maxlen),maxshape=(maxlen),dtype='float',compression="gzip",compression_opts=4)
                        
            mcadata[:,:]=newspec
            mcadataxv[:]=newmz
            
            fout.flush() 
            fout.close()
           
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dtshaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## Opus - Bruker OPUS  Format
####################################

class opusLoad(SuperClass):
    
    def __init__(self,fn,temp,wd):
        self.type='OPUS'
        (basefn,ext)=os.path.splitext(fn)
        db=opusFC.listContents(fn)
        img=opusFC.getOpusData(fn,db[0])
        
        self.xvals = img.mapX
        self.yvals = img.mapY

        
        dall = img.spectra.sum(2)
        
        self.labels=['FTIR']
        self.channels=1
        self.energy=1 

        self.comments=''
            
        self.nxpts = len(self.xvals)
        self.nypts = len(self.yvals)
        
        dims=[self.nypts,self.nxpts,self.channels+2]
        dtshaped=np.zeros(tuple(dims),dtype=np.float32)
        dtshaped[:,:,2]=dall

        print((self.channels,dtshaped.shape,self.nxpts,self.nypts))
        
        #add coordinates to dt matrix
        for i in range(self.nxpts):
            dtshaped[:,i,1]=np.ones((self.nypts))*self.xvals[i]
        for j in range(self.nypts):
            dtshaped[j,:,0]=np.ones((self.nxpts))*self.yvals[j]

        print((dtshaped.shape))
        
        #extract IR data
        #img.x has the x-coordinates...
        fnout=os.path.splitext(fn)[0]+"_ftir.hdf5"
        print (fnout)
        if not os.path.exists(fnout):
            fout=h5py.File(fnout,'w')
            groupout=fout.create_group("main")
            
            maxlen = img.spectra.shape[2]
            maxpoints = self.nxpts*self.nypts
            irdat = img.spectra.reshape(maxpoints,maxlen)
            print (irdat.shape)
            mcadata=groupout.create_dataset("mcadata",(maxpoints,maxlen),maxshape=(None,maxlen),dtype='float',compression="gzip",compression_opts=4)
            mcadataxv=groupout.create_dataset("xdata",(maxlen),maxshape=(maxlen),dtype='float',compression="gzip",compression_opts=4)
            
            mcadata[:,:]=irdat
            mcadataxv[:]=img.x
            
            fout.flush() 
            fout.close()
           
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dtshaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
## Horiba - Horiba Lab Spec TXT output
####################################

class horibaText(SuperClass):
    
    def __init__(self,fn,temp,wd):
        self.type='HORIBA'
        (basefn,ext)=os.path.splitext(fn)

        fid=open(fn)
        lines=fid.read().split('\n')
        fid.close()        
        
        dt=[]
        self.xvals=[]
        self.yvals=[]
        self.labels=['RAMAN']
        self.channels=1
        self.energy=1
        self.comments=''
        yv=None
        xvadv=0
        yfull=0

        #process header line
        specxv = np.array(list(map(float,lines[0].split())))
        rspec = []
        print (len(specxv),'entries in spectra')

        for line in lines:
            if len(line)==0 or line=='' or line==' ': continue
            if len(line)>0 and line[0]=='#': continue
            if line[0]=='\t': continue
            #append data
            ttemp=[]
            tl=line.split()
            if len(tl)<2: continue
            xvadv=0
            if yv==None:
                yv=float(tl[1])
                self.xvals.append(yv)
            elif yv!=float(tl[1]):
                xvadv=1
                if not yfull:
                    self.xvals.append(float(tl[1]))
            else:
                yfull=1            
            if not xvadv:
                self.yvals.append(float(tl[0]))
            tl=list(map(float,tl))
            ttemp.append([tl[0],tl[1],np.array(tl[2:],dtype=np.float32).sum()])
            rspec.append(np.array(tl[2:],dtype=np.float32))
            dt.append(ttemp)
        self.nypts=len(self.yvals)
        self.nxpts=len(self.xvals)
        self.xvals=np.array(self.xvals)
        self.yvals=np.array(self.yvals)
        dt=np.array(dt)        
        
        print((self.channels,dt.shape,self.nxpts,self.nypts,yv))
        #print self.labels
        dataShaped=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))

        print((dataShaped.shape))
        if not temp: self.hdf5=h5py.File(os.path.join(wd[0],'workingfile'+str(wd[1])+'.hdf5'),'w', **HD5OPT)
        else: self.hdf5=h5py.File(os.path.join(wd[0],'temp.hdf5'),'w', **HD5OPT)
        self.hdf5group=self.hdf5.create_group("main")
        print((self.hdf5group.name))
        self.hdf5data=self.hdf5group.create_dataset("mapdata",(self.nypts,self.nxpts,self.channels+2),data=dataShaped,maxshape=(5000,5000,None),dtype='float')
        print((self.hdf5data.size,self.hdf5data.shape))
        self.hasHDF5=True
        self.data=HDF5get(self.hdf5data)

        self.isVert=0

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
        
        
        
        #extract IR data
        fnout=os.path.splitext(fn)[0]+"_ram.hdf5"
        print (fnout)
        if not os.path.exists(fnout):
            fout=h5py.File(fnout,'w')
            groupout=fout.create_group("main")
            
            maxlen = len(specxv)
            maxpoints = len(rspec)
            irdat = np.array(rspec).reshape(maxpoints,maxlen)
            print (irdat.shape)
            mcadata=groupout.create_dataset("mcadata",(maxpoints,maxlen),maxshape=(None,maxlen),dtype='float',compression="gzip",compression_opts=4)
            mcadataxv=groupout.create_dataset("xdata",(maxlen),maxshape=(maxlen),dtype='float',compression="gzip",compression_opts=4)
            
            mcadata[:,:]=irdat
            mcadataxv[:]=specxv
            
            fout.flush() 
            fout.close()
           
 

        
####################################
## Main
####################################

def ImageGet(fn,root,large=0,temp=False,special=None,workdir=None):
    #for file type determination
    if workdir==None:
        wd=['',0]
    else:
        if workdir.get()==None:
            wd=['',workdir.wfn]
        else:
            wd=[workdir.get(),workdir.wfn]
    print (wd)
    fp=fn.split('.')
    exten=fp[-1]
    fid=open(fn, 'rb')
    #with  open(fn, 'rb') as fid:
    buf=fid.readline()
    try:
        buf2=fid.readline()
    except:
        buf2=''
    try:
        buf3=fid.readline()
    except:
        buf3=''
    
    fid.close()
    #HDF5 file
    #exten=exten.decode()
    if len(exten)>3 and exten.upper()=="HDF5" or len(exten)>2 and exten.upper()=="HDF":
        return HDF5load(fn,temp,wd)
    #GSE CARS or APS-MAPS h5 file?
    if len(exten) in [2,3] and exten.upper() in ("H5","H50","H51","H52","H53"):
        return GSEH5load(fn,root,temp,wd)
    #SOLEIL 
    if len(exten)==3 and exten.upper()=="NXS":
        return SOLEILload(fn,root,temp,wd,special)        
    #ESRF 
    if len(exten)==3 and exten.upper()=="EDF":
        return EDFload(fn,temp,wd)
    #agilent data
    if exten in ['dms','dmt','seq','bsp']:
        return agilentload(fn,temp,wd)
    if exten == 'imzML':
        if pyimzmlInstalled:
            return imzmlLoad(fn,temp,wd)
        else:
            print ('imzML extension not loaded')
            return
    if exten == '0':
        if opusInstalled:
            return opusLoad(fn,temp,wd)
        else:
            print ('OpusFC extension not loaded')
            return
    #zip'd tof-ms
    if exten in ['zip','vit']:
        return ziptofms(fn,temp,wd)
    #Raw JPG or TIFF
    if (exten).lower() in ['jpg','jpeg','tif','tiff','gif','bmp','png']:
        if (exten).lower() not in ['tiff','tif']: return fromRawImage(fn,temp,wd)
        else: return fromRawImage(fn,temp,wd,t=True)
    buf=buf.decode()
    buf2= buf2.decode()
    buf3=buf3.decode()
    #SUPER file
    if len(exten)>3 and exten[-1]=='G':
        return SUPER(fn,exten[:-1],temp,wd)
    #ROBL SPEC
    if len(buf)>3 and len(buf2)>3 and len(buf3)>3 and buf[0:2]=='#F' and buf2[0:2]=='#E'  and buf3[0:2]=='#D':
        return SPEC(fn,temp,wd)
    #SCANE file
    if buf.split()[0]=='*' and buf.split()[1]=='Abscissa':
        return SCANE(fn,large,root,temp,wd)
    #RAS ASCII file
    if len(buf.split())>1 and buf.split()[1]=='Raster':
        return RAS(fn,temp,wd)
    #APS file
    if len(buf.split())>1 and buf.split()[1]=='Epics':
        return APS_GSE(fn,temp,wd)
    #ALS file
    if exten=='xrf' and buf.split()[0]=='Title':
        return ALS1032(fn,temp,wd)
    if exten=='xrf':
        return ALS1032_fmt2(fn,temp,wd)
    #PNC-CAT file
    if len(buf.split())>3 and buf.split()[1]=='2-D' and buf.rfind('Panel')!=-1: #buf.split()[-1]=='Panel':
        return PNC(fn,temp,wd)
    #NSLS ASC file
    if exten=='asc' and buf.split()[0]=='File:':
        return NSLSASCII(fn,temp,wd)
    if exten=="hdr":
        return enviload(fn,temp,wd)
    #BL6-2 TXM File
    if len(buf.split())==3 and isnumberlist(buf.split()):
        return BL62TXM(fn,temp,wd)
    #Diamond RGB file
    if exten=='rgb':
        return DIAMOND_RGB(fn,temp,wd)
    #APS MRCAT
    if buf2!='' and ("APS 10ID" in buf2.split('"')):
        return MRCAT(fn,temp,wd)
    #AXIS XIM
    if exten=='xim':
        return XIM(fn,temp,wd)
    #AXIS stack binary
    if exten=='ncb':
        return NCB(fn,temp,wd)

    #Text output 3 column
    print (len(buf.split()),  buf[0]=='\t')
    if exten=='txt' and len(buf.split())==3 and buf.split()[0]=='0':
        return text3column(fn,temp,wd)
    
    if exten=='txt' and len(buf.split())>200 and buf[0]=='\t':
        return horibaText(fn,temp,wd)

    #ICP-MS TYPE
    if exten=='txt' and len(buf)>5 and buf[0:6]=='#ICPMS':
        return ICPMS(fn,temp,wd)

    if len(buf)>100:
        #try NSLS X26 binary?
        return NSLSBINARY(fn,temp,wd)
    #No idea
    print ('File type not recognized')
    return
    
