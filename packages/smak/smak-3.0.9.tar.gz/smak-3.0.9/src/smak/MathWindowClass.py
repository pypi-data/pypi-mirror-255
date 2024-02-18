import imutils
import math
import tkinter
from tkinter.ttk import Button

import cv2
import imreg_dft as ird
from imreg_dft import tiles as irdTiles
import numpy as np
import Pmw

#local
import align_images
import globalfuncs
import imgFuse
from MasterClass import MasterClass



def HFlipOp(ad):
    return MathOp('Horz Flip', ad, None)
    
def VFlipOp(ad):
    return MathOp('Vert Flip', ad, None)

def MathOp(oper,Adata,Bdata,option={}):

    if oper=='Add':
        newdata=Adata+Bdata
    if oper=='Subtract':
        newdata=Adata-Bdata
    if oper=='Multiply':
        newdata=Adata*Bdata
    if oper=='Divide':
        bd=Bdata
        if type(bd)==type(0.2):
            if bd==0:
                newdata=Adata#[:,:,Aind]
            else:
                newdata=Adata/bd
        else:
            (xlen,ylen)=Adata.shape
            newdata=np.zeros((xlen,ylen),dtype=np.float32)
            ad=Adata
            for i in range(xlen):
                for j in range(ylen):
                    if bd[i,j]!=0:
                        newdata[i,j]=ad[i,j]/bd[i,j]
    if oper=='Smooth':
        (xlen,ylen)=Adata.shape
        newdata=np.zeros((xlen,ylen),dtype=np.float32)
        filter=np.array([[.11,.11,.11],[.11,.12,.11],[.11,.11,.11]])
        newdata=globalfuncs.filterconvolve(Adata,filter)
    if oper=='Sharpen':
        (xlen,ylen)=Adata.shape
        newdata=np.zeros((xlen,ylen),dtype=np.float32)
        filter=np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]])
        newdata=globalfuncs.filterconvolve(Adata,filter)            
    if oper=='Derivative':
        (xlen,ylen)=Adata.shape
        newdata=np.zeros((xlen,ylen),dtype=np.float32)
        newdata2=np.zeros((xlen,ylen),dtype=np.float32)
        filter=np.array([[1,2,1],[0,0,0],[-1,-2,-1]])            
        filter2=np.array([[1,0,-1],[2,0,-2],[1,0,-1]])
        newdata=globalfuncs.filterconvolve(Adata,filter)
        newdata2=globalfuncs.filterconvolve(Adata,filter2)
        newdata=newdata+newdata2
    if oper=='Abs Deriv':
        (xlen,ylen)=Adata
        newdata=np.zeros((xlen,ylen),dtype=np.float32)
        newdata2=np.zeros((xlen,ylen),dtype=np.float32)
        filtershape=np.array([[1,2,1],[0,0,0],[-1,-2,-1]])            
        filter2=np.array([[1,0,-1],[2,0,-2],[1,0,-1]])            
        newdata=globalfuncs.filterconvolve(Adata,filter,z=1)
        newdata2=globalfuncs.filterconvolve(Adata,filter2,z=1)
    if oper=='Deadtime':
        newdata=Adata.copy()
        if 'icr' in option and 'dtv' in option:
            dtcor=np.exp(option['dtv']*1e-6*option['icr'])
            newdata=newdata*dtcor
        else:
            print('Deadtime parameters not set...')
            (xlen,ylen)=Adata.shape
            return np.zeros((xlen,ylen),dtype=np.float32)
    if oper=='Apply Mask':
        if 'mask' in option:
            mask=option['mask']
        else:
            print ('No mask provided')
            return Adata
        (xlen,ylen)=Adata.shape
        if Adata.shape!=mask.shape:
            print("Improper mask size")
            return np.zeros((xlen,ylen),dtype=np.float32)
        newdata=mask*Adata#[:,:,Aind]
    if oper=='Laplacian':
        (xlen,ylen)=Adata.shape
        newdata=np.zeros((xlen,ylen),dtype=np.float32)
        filter=np.array([[0,1,0],[1,-4,1],[0,1,0]])
        newdata=globalfuncs.filterconvolve(Adata,filter)
    if oper=='Abs Laplacian':
        (xlen,ylen)=Adata.shape
        newdata=np.zeros((xlen,ylen),dtype=np.float32)
        filter=np.array([[0,1,0],[1,-4,1],[0,1,0]])
        newdata=globalfuncs.filterconvolve(Adata,filter,z=1)
    if oper=='Log':
        ad=Adata#[:,:,Aind]
        newdata=np.where(ad>0,ad,1)
        newdata=np.log(newdata)
    if oper=='Exp':
        newdata=np.exp(Adata)#[:,:,Aind])
    if oper=='AbsVal':
        newdata=np.abs(Adata)#[:,:,Aind])
    if oper=='2^x':
        newdata=2**Adata
    if oper=='Sqrt':
        newdata=np.where(Adata>0,1,0)
        newdata=np.sqrt(newdata*Adata)#[:,:,Aind])
    if oper =='Horz Flip':
        newdata=Adata[:,::-1]
    if oper =='Vert Flip':    
        newdata=Adata[::-1,:]
    if oper=='Vert Shift':
        print (Bdata)
        try: r=int(Bdata)
        except: r=0
        newdata=Adata#[:,:,Aind]
        if r>0:
            nr=np.zeros((r,newdata.shape[1]),dtype=np.float32)
            newdata=np.concatenate((newdata,nr),axis=0)
            newdata=newdata[r:,:]
        elif r<0:
            nr=np.zeros((-r,newdata.shape[1]),dtype=np.float32)
            newdata=np.concatenate((nr,newdata),axis=0)
            newdata=newdata[:newdata.shape[0]+r,:]
    if oper=='Horz Shift':
        try: r=int(Bdata)
        except: r=0
        r=-r
        newdata=Adata#[:,:,Aind]
        if r>0:
            nr=np.zeros((newdata.shape[0],r),dtype=np.float32)
            newdata=np.concatenate((newdata,nr),axis=1)
            newdata=newdata[:,r:]
        elif r<0:
            nr=np.zeros((newdata.shape[0],-r),dtype=np.float32)
            newdata=np.concatenate((nr,newdata),axis=1)
            newdata=newdata[:,:newdata.shape[1]+r]                
    if oper=='Translate':
        #wm = cv2.MOTION_TRANSLATION
        resample = 5
        inA = irdTiles.resample(Adata,resample)
        inB = irdTiles.resample(Bdata,resample)
        result = ird.translation(inA,inB)
        print(result['success'],result['tvec']/float(resample))
        newdata=ird.transform_img(option['fullB'],tvec=result["tvec"]/float(resample))

    if oper=='Register':
        #wm = cv2.MOTION_TRANSLATION
        result = ird.translation( Adata,Bdata)
        print(result['success'],result['tvec'],np.round(result['tvec']))
        newdata=ird.transform_img(option['fullB'],tvec=np.round(result["tvec"]))
    if oper=='Transform':
        #wm = cv2.MOTION_TRANSLATION
        resample = 5
        inA = irdTiles.resample(Adata,resample)
        inB = irdTiles.resample(Bdata,resample)
        result = ird.similarity(inA,inB,constraints={'scale':[1.0,0]},numiter=3)
        print(result['success'],result['tvec']/float(resample),result['angle'],result['scale'])
        newdata=ird.transform_img(option['fullB'],tvec=result["tvec"]/float(resample),scale=result['scale'],angle=result['angle'])
    if oper=='FuseMean':
        newdata=imgFuse.doFuse(Adata,Bdata,'mean')
    if oper=='FuseMin':
        newdata=imgFuse.doFuse(Adata,Bdata,'min')
    if oper=='FuseMax':
        newdata=imgFuse.doFuse(Adata,Bdata,'max')
    if oper=='Xcoords':
        newdata=Adata
    if oper=='Ycoords':
        newdata=Adata
    if oper=='AddIndex':
        newdata=np.ravel(Adata)
        newdata=np.arange((len(newdata)))
        newdata=newdata.reshape(Adata.shape)     

    if oper=='Align':
        
        print("[INFO] aligning images...")
        aligned,t,tempGray = align_images(Bdata, Adata, debug=False, maxFeatures=200000, keepPercent=0.5,
                         ptsOverride=None, color=False)
        
        #check validity?
        print ("translation x:",t['tx'])
        print ("translation y:",t['ty'])
        print ("scale x:",t['scx'])
        print ("scale x:",t['scy'])
        print ("shear:",t['sh'])
        print ("rotate:",math.degrees(t['rot']))         
        
        newdata = cv2.warpPerspective(option['fullB'], t['H'], t['wh'])
                
    return newdata

class MathWindowParams():
    def __init__(self, displayParams, docalcimage, addchannel, mask):
        self.displayParams = displayParams
        self.docalcimage = docalcimage
        self.addchannel = addchannel
        self.mask= mask

class MathWindow(MasterClass):

    def _create(self):
        #make window
        self.win=Pmw.MegaToplevel(self.imgwin)
        self.win.title('Calculate Math Window')
        self.win.userdeletefunc(func=self.kill)
        h=self.win.interior()
        h.configure(background='#d4d0c8')
        #Menu bar??
        f=tkinter.Frame(h,background='#d4d0c8')
        f.pack(side=tkinter.LEFT,fill='both',pady=20)
        #new channel name and action buttons
        self.newchannel=Pmw.EntryField(f,labelpos='w',label_text='New Channel Name: ',entry_width=15,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.newchannel.pack(side=tkinter.TOP,fill=tkinter.X,pady=10)
        self.docalcbut=Button(f,text='Do Calculation',command=self.docalculation,style='GREEN.TButton',width=15)
        self.docalcbut.pack(side=tkinter.TOP,fill=tkinter.Y,pady=5)
        self.savecalcbut=Button(f,text='Save Calculation',command=self.savecalculation,style='RRED.TButton',width=15)
        self.savecalcbut.pack(side=tkinter.TOP,fill=tkinter.Y,pady=5)        
        #have channel select
        f=tkinter.Frame(h,background='#d4d0c8')
        f.pack(side=tkinter.LEFT,fill='both')
        lab=tkinter.Label(f,text=' = ',background='#d4d0c8')
        lab.pack(side=tkinter.LEFT,fill='both',padx=10)
        self.mathA=Pmw.ScrolledListBox(f,labelpos='n',label_text='Data Channel',listbox_height=5,
                        selectioncommand=self.checkmathA,listbox_exportselection=0,listbox_takefocus=tkinter.TRUE,
                        hull_background='#d4d0c8',label_background='#d4d0c8')
        #bind to move
        self.mathA.bind(sequence="<Up>", func=self.arrowmathA)
        self.mathA.bind(sequence="<Down>", func=self.arrowmathA)
        self.mathA.pack(side=tkinter.LEFT,fill='both')
        self.mathA.setlist(self.mapdata.labels)
        #operation select
        self.mathop=Pmw.ScrolledListBox(f,labelpos='n',label_text='Operation',listbox_height=5,
                        selectioncommand=self.checkmathop,listbox_exportselection=0,listbox_takefocus=tkinter.TRUE,
                        hull_background='#d4d0c8',label_background='#d4d0c8')
        #bind to move
        self.mathop.bind(sequence="<Up>", func=self.arrowmathop)
        self.mathop.bind(sequence="<Down>", func=self.arrowmathop)
        self.mathop.pack(side=tkinter.LEFT,fill='both')
        self.mathop.setlist(['Add','Subtract','Multiply','Divide',
                             'Smooth','Sharpen',
                             'Derivative','Abs Deriv',
                             'Apply Mask','Deadtime',
                             'Laplacian','Abs Laplacian','Log','Exp','2^x','Sqrt','AbsVal',
                             'Vert Shift','Horz Shift','Register','Translate','Transform','Align',
                             'Vert Flip','Horz Flip',
                             'FuseMean','FuseMin','FuseMax',
                             #'AddIndex','Xcoords','Ycoords'
                             ])
        #constant/channel select 2
        self.mathB=Pmw.ScrolledListBox(f,labelpos='n',label_text='Data Channel',listbox_height=5,
                        selectioncommand=self.checkmathscalar,listbox_exportselection=0,listbox_takefocus=tkinter.TRUE,
                        hull_background='#d4d0c8',label_background='#d4d0c8')
        #bind to move
        self.mathB.bind(sequence="<Up>", func=self.arrowmathB)
        self.mathB.bind(sequence="<Down>", func=self.arrowmathB)
        self.mathB.pack(side=tkinter.LEFT,fill='both')
        mathBlist=self.mapdata.labels
        mathBlist.append('Scalar')        
        self.mathB.setlist(mathBlist)
        self.mapdata.labels.pop()
        self.mathfr=tkinter.Frame(h,background='#d4d0c8')
        self.mathfr.pack(side=tkinter.LEFT,fill='both',padx=10)
        self.scalarpresent=0
        #idk status fix
 

    def checkmathA(self,*args):
        self.mathA.focus_set()

    def checkmathop(self):
        self.mathop.focus_set()
        if self.mathop.getvalue()==():
            return
        if self.mathop.getvalue()[0] in ('Smooth','Sharpen','Derivative','Abs Deriv','Apply Mask','Deadtime','Laplacian','Abs Laplacian','Log','Exp','2^x','Sqrt','AbsVal','Vert Flip','Horz Flip','AddIndex','Xcoords','Ycoords'):
            #deactivate selection B
            self.mathB.selection_clear()
            self.mathB.setvalue(())
            self.mathB.component('listbox').config(fg='dark grey')
        elif self.mathop.getvalue()[0] in ('Vert Shift','Horz Shift'):
            self.mathB.selection_clear()
            self.mathB.setvalue('Scalar')
            self.mathB.component('listbox').config(fg='dark grey')
            self.checkmathscalar(op=0)
        else:
            self.mathB.component('listbox').config(fg='black')

    def checkmathscalar(self,op=1):
        if op: self.checkmathop()
        self.mathB.focus_set()
        if self.mathB.getvalue()==():
            if self.scalarpresent==1:
                self.mathscalar.destroy()
                self.scalarpresent=0                
            return
        if self.scalarpresent==0 and self.mathB.getvalue()[0]=='Scalar':
            #create new scalar box
            self.mathscalar=Pmw.EntryField(self.mathfr,labelpos='n',label_text='Scalar: ',entry_width=10,validate='real')
            self.mathscalar.pack(side=tkinter.TOP,fill='both',pady=15)
            self.scalarpresent=1
        if self.scalarpresent==1 and self.mathB.getvalue()[0]!='Scalar':
            self.mathscalar.destroy()
            self.scalarpresent=0



    def docalculation(self):
        if self.mathA.getvalue()==() or self.mathop.getvalue()==() or (self.mathop.getvalue()[0] not in ('Smooth','Sharpen','Derivative','Abs Deriv','Apply Mask','Deadtime','Laplacian','Abs Laplacian','Log','Exp','2^x','Sqrt','AbsVal','Vert Flip','Horz Flip','AddIndex','Xcoords','Ycoords') and self.mathB.getvalue()==()):
            #not enough info
            print('Choose sets to manipulate')
            globalfuncs.setstatus(self.ps.displayParams.status,'Choose sets to manipulate')
            return
        globalfuncs.setstatus(self.ps.displayParams.status,'CALCULATING...')
        #set dataA
        Aind=self.mapdata.labels.index(self.mathA.getvalue()[0])+2
        if self.mathop.getvalue()[0]=='Xcoords': Aind=0
        if self.mathop.getvalue()[0]=='Ycoords': Aind=1
        if len(self.mathB.getvalue())>0 and self.mathB.getvalue()[0] != 'Scalar':
            Bind=self.mapdata.labels.index(self.mathB.getvalue()[0])+2
        else:
            Bind=None
        #iterate on math operation:
        option={}
        if self.mathop.getvalue()[0]=='Apply Mask':
            option['mask']=self.mask.mask
        if self.mathop.getvalue()[0]=='Deadtime':
            if self.DTICRchanval!=-1 and self.deadtimevalue is not None:
                #DT: corFF=FF*exp(tau*1e-6*ICR)
                option['icr']=self.mapdata.data.get(self.DTICRchanval)#[:,:,self.DTICRchanval]
                option['dtv']=float(self.deadtimevalue.getvalue())
            else:
                print('Deadtime parameters not set...')
                globalfuncs.setstatus(self.ps.displayParams.status,'Deadtime parameters not set!')
                (xlen,ylen)=self.getAdata(Aind).shape
                return np.zeros((xlen,ylen),dtype=np.float32)
        if self.mathop.getvalue()[0] in ['Translate','Register','Transform','Align']:
            option['fullB']=self.getBdata(Bind,limit=False)
            newdata = MathOp(self.mathop.getvalue()[0],self.getAdata(Aind,limit=True),self.getBdata(Bind,limit=True),option)
        else:
            newdata = MathOp(self.mathop.getvalue()[0],self.getAdata(Aind),self.getBdata(Bind),option)

        #display new data
        self.ps.docalcimage(newdata)
        return newdata

    def getAdata(self,index,limit=False):
        if limit and self.ps.displayParams.zmxyi[0:4]!=[0,0,-1,-1]:  
            return self.mapdata.data.get(index)[self.ps.displayParams.zmxyi[1]:self.ps.displayParams.zmxyi[3],self.ps.displayParams.zmxyi[0]:self.ps.displayParams.zmxyi[2]]
        else:
            return self.mapdata.data.get(index)

    def getBdata(self,index,limit=False):

        #set dataB
        if self.scalarpresent:
            try: r=float(self.mathscalar.getvalue())
            except: r=0
            return r
        elif index is None:
            return None
        elif self.mathB.getvalue()[0]!='Scalar':

            if limit and self.ps.displayParams.zmxyi[0:4]!=[0,0,-1,-1]: 
                return self.mapdata.data.get(index)[self.ps.displayParams.zmxyi[1]:self.ps.displayParams.zmxyi[3],self.ps.displayParams.zmxyi[0]:self.ps.displayParams.zmxyi[2]]
            else:
                return self.mapdata.data.get(index)
                
    
        


    def arrowmathA(self,event):
        dlist=self.mathA.get()
        ind=dlist.index(self.mathA.getvalue()[0])
        if event.keysym == 'Down':
            ind=ind+1
        if event.keysym == 'Up':
            ind=ind-1
        if ind<0: ind=0
        if ind>len(dlist)-1: ind=len(dlist)-1
        self.mathA.setvalue(dlist[ind])
        self.mathA.see(ind)
        self.checkmathA()

    def arrowmathB(self,event):
        dlist=self.mathB.get()
        ind=dlist.index(self.mathB.getvalue()[0])
        if event.keysym == 'Down':
            ind=ind+1
        if event.keysym == 'Up':
            ind=ind-1
        if ind<0: ind=0
        if ind>len(dlist)-1: ind=len(dlist)-1
        self.mathB.setvalue(dlist[ind])
        self.mathB.see(ind)
        self.checkmathscalar()

    def arrowmathop(self,event):
        dlist=self.mathop.get()
        ind=dlist.index(self.mathop.getvalue()[0])
        if event.keysym == 'Down':
            ind=ind+1
        if event.keysym == 'Up':
            ind=ind-1
        if ind<0: ind=0
        if ind>len(dlist)-1: ind=len(dlist)-1
        self.mathop.setvalue(dlist[ind])
        self.mathop.see(ind)
        self.checkmathop()

    def checkname(self):
        #make sure name present
        if self.newchannel.getvalue()=='':
            print('Enter new channel name')
            globalfuncs.setstatus(self.ps.displayParams.status,'Enter new channel name')
            return False
        #make sure name unique
        new=globalfuncs.fixlabelname(self.newchannel.getvalue())
        if new in self.mapdata.labels:
            print('Enter unique channel name')
            globalfuncs.setstatus(self.ps.displayParams.status,'Enter unique channel name')
            return False  
        return new     

    def savecalculation(self):
        new = self.checkname()
        if new != False:    
            #do calculation
            data=self.docalculation()
            #save new channel        
            self.ps.addchannel(data,new)
        else:
            return




    