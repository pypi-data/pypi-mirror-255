import tkinter

import Pmw
import numpy as np 


import globalfuncs
import Deconv
from MasterClass import MasterClass


class BeamDeconvolutionWindowParams:
    def __init__(self, status, maindisp, showmap, savedeconvcalculation):
        self.status = status
        self.maindisp = maindisp
        self.showmap = showmap
        self.savedeconvcalculation = savedeconvcalculation


class BeamDeconvolutionWindow(MasterClass):
    def _create(self):
        # self.imgwin = imgwin
        # self.mapdata = mapdata
        # self.ps = ps
        self.win=Pmw.Dialog(self.imgwin,title="Beam Deconvolution",buttons=('Preview','Save','Done'),defaultbutton='Done',
                                     command=self.enterDeconv)
        h=self.win.interior()
        h.configure(background='#d4d0c8')
        lf=tkinter.Frame(h,background='#d4d0c8')
        lf.pack(side=tkinter.LEFT,fill='both')
        #data selection
        self.deconvsel=Pmw.ScrolledListBox(lf,labelpos='n',label_text='Select Channel',items=self.mapdata.labels,listbox_selectmode=tkinter.SINGLE,
                                              listbox_exportselection=tkinter.FALSE,selectioncommand=self.selectdecdata,listbox_height=15,
                                           hull_background='#d4d0c8',label_background='#d4d0c8')
        self.deconvsel.pack(side=tkinter.TOP,padx=4,pady=5,fill='both')
        #new data name
        self.newdecname=Pmw.EntryField(lf,labelpos='w',label_text='New Channel Name: ',entry_width=15,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.newdecname.pack(side=tkinter.TOP,fill=tkinter.X,pady=10)
        
        rf=tkinter.Frame(h,background='#d4d0c8')
        rf.pack(side=tkinter.LEFT,fill='both',padx=5)
        l=tkinter.Label(rf,text='Deconvolution Parameters',bd=2,relief=tkinter.RAISED,background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill=tkinter.X,expand=1,pady=5)
        l=tkinter.Label(rf,text='X pixel='+str(abs(self.mapdata.xvals[2]-self.mapdata.xvals[1])*1000)+' microns',background='#d4d0c8')
        l.pack(side=tkinter.TOP,pady=5,padx=5)
        l=tkinter.Label(rf,text='Y pixel='+str(abs(self.mapdata.yvals[2]-self.mapdata.yvals[1])*1000)+' microns',background='#d4d0c8')
        l.pack(side=tkinter.TOP,pady=5,padx=5)
        #filter size
        self.deconvFSvar=tkinter.IntVar()
        self.deconvFSvar.set(5)
        self.deconvFS=tkinter.Scale(rf,label='Filter Size',background='#d4d0c8',variable=self.deconvFSvar,width=10,from_=3,to=49,orient=tkinter.HORIZONTAL,resolution=1)
        self.deconvFS.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=10)
        #PSF Type
        self.deconvPSF=Pmw.RadioSelect(rf,buttontype='radiobutton',orient='horizontal',command=self.selectDeconPSF,hull_background='#d4d0c8')
        for text in ('Gauss','Circle','Arcs','Meas'):
            self.deconvPSF.add(text,background='#d4d0c8')
        self.deconvPSF.pack(side=tkinter.TOP,padx=3,pady=3)
        #beam FWHM        
        self.deconvFWHMvar=tkinter.DoubleVar()
        self.deconvFWHMvar.set(2.0)
        self.deconvFWHM=tkinter.Scale(rf,label='Beam Size (microns)',background='#d4d0c8',variable=self.deconvFWHMvar,width=10,from_=0.1,to=50.0,orient=tkinter.HORIZONTAL,resolution=.1)
        self.deconvFWHM.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=10)
        #beam FWHM        
        self.deconvFWHMvar2=tkinter.DoubleVar()
        self.deconvFWHMvar2.set(1.0)
        self.deconvFWHM2=tkinter.Scale(rf,label='Ring Width (microns)',background='#d4d0c8',variable=self.deconvFWHMvar2,width=10,from_=0.1,to=50.0,orient=tkinter.HORIZONTAL,resolution=.1,state=tkinter.DISABLED,fg='gray70')
        self.deconvFWHM2.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=10)
        self.deconvFWHMvar3=tkinter.DoubleVar()
        self.deconvFWHMvar3.set(100.0)
        self.deconvFWHM3=tkinter.Scale(rf,label='PSF Fill (pct) ',background='#d4d0c8',variable=self.deconvFWHMvar3,width=10,from_=1.0,to=100.0,orient=tkinter.HORIZONTAL,resolution=1.0,state=tkinter.DISABLED,fg='gray70')
        self.deconvFWHM3.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=10)
        self.deconvPSF.setvalue('Gauss')
        #NSR
        self.deconvNSR=Pmw.EntryField(rf,labelpos='w',label_text='Noise-Signal Power Ratio: ',entry_width=15,validate='real',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.deconvNSR.setvalue(0)
        self.deconvNSR.pack(side=tkinter.TOP,fill=tkinter.X,pady=5)
        #get estimate
        self.deconvNSRest=tkinter.Label(rf,text='NSR estimate: 0',bd=2,relief=tkinter.SUNKEN,background='#d4d0c8')
        self.deconvNSRest.pack(side=tkinter.TOP,fill=tkinter.X,pady=5)
        #apply window
        self.deconvWIN=Pmw.RadioSelect(rf,buttontype='checkbutton',labelpos='w',label_text='FT Windowing',frame_background='#d4d0c8',label_background='#d4d0c8',hull_background='#d4d0c8')
        self.deconvWIN.add('Yes',background='#d4d0c8')
        self.deconvWIN.pack(side=tkinter.TOP,fill='both',padx=5,pady=7)
        self.deconvWINp=Pmw.EntryField(rf,labelpos='w',label_text='Window Size: ',entry_width=15,validate='numeric',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.deconvWINp.setvalue(5)
        self.deconvWINp.pack(side=tkinter.TOP,fill=tkinter.X,pady=10)
        
        self.win.show()
        self.win.userdeletefunc(func=self.kill)


    def selectDeconPSF(self,*args):
        if self.deconvPSF.getvalue()=='Arcs':
            self.deconvFWHM2.configure(state=tkinter.NORMAL)
            self.deconvFWHM2.configure(fg='black')
            self.deconvFWHM3.configure(state=tkinter.NORMAL)
            self.deconvFWHM3.configure(fg='black')
        elif self.deconvPSF.getvalue()=='Circle':
            self.deconvFWHM2.configure(state=tkinter.NORMAL)
            self.deconvFWHM2.configure(fg='black')
            self.deconvFWHM3.configure(state=tkinter.DISABLED)
            self.deconvFWHM3.configure(fg='gray70')
        else:
            self.deconvFWHM2.configure(state=tkinter.DISABLED)
            self.deconvFWHM2.configure(fg='gray70')
            self.deconvFWHM3.configure(state=tkinter.DISABLED)
            self.deconvFWHM3.configure(fg='gray70')        

    def selectdecdata(self,*args):
        name=self.deconvsel.getvalue()[0]
        i=1
        newname=name+'-dec'
        while newname in self.mapdata.labels:
            newname=name+'-dec'+str(i)
            i+=1
        self.newdecname.setvalue(newname)
        #calculate NSR
        datind=self.mapdata.labels.index(self.deconvsel.getvalue()[0])+2
        old=np.ravel(self.mapdata.data.get(datind))#[:,:,datind])
        nsr=1./globalfuncs.getSNR(old)
        globalfuncs.setstatus(self.deconvNSRest,'NSR Estimate: '+globalfuncs.valueclip_d(nsr,5))
        
    def savedeconvcalculation(self,newd,name):
        #make sure name present
        if name=='':
            print('Enter new channel name')
            globalfuncs.setstatus(self.ps.status,'Enter new channel name')
            return
        #make sure name unique
        newname=globalfuncs.fixlabelname(name)
        if newname in self.mapdata.labels:
            print('Enter unique channel name')
            globalfuncs.setstatus(self.ps.status,'Enter unique channel name')
            return            
        #save new channel        
        self.addchannel(newd,newname)

    def enterDeconv(self,result):
        if result=='Done':
            self.win.withdraw()
            return
        if len(self.deconvsel.getvalue())<1:
            print('Select a data channel')
            return
        globalfuncs.setstatus(self.ps.status,"DECONVOLVING...")
        if self.deconvPSF.getvalue() not in ['Meas']:
            fwhm=self.deconvFWHMvar.get()/(abs(self.mapdata.xvals[2]-self.mapdata.xvals[1])*1000.)
            print(fwhm)
            psf=Deconv.fspecial(self.deconvFSvar.get(),fwhm)

            if self.deconvPSF.getvalue() in ['Circle','Arcs']:
                fwhm2=self.deconvFWHMvar2.get()/(abs(self.mapdata.xvals[2]-self.mapdata.xvals[1])*1000.)
                print(fwhm2)
                psf2=Deconv.fannular(self.deconvFSvar.get(),fwhm,fwhm2)
                if self.deconvPSF.getvalue() in ['Arcs']:
                    nr=(1-self.deconvFWHMvar3.get()/100.0) * float(self.deconvFSvar.get())
                    nr=int(round(nr/2))
                    print("nr",nr)
                    if nr!=0:
                        psf=np.zeros(psf.shape)
                        psf[nr:-nr,:]=psf2[nr:-nr,:]
                    else:
                        psf=psf2
                else:
                    psf=psf2                        
        else:
            h,w= self.ps.maindisp.savedPSF.shape
            crop=min(h,w)
            print(h,w,crop)
            psf=self.ps.maindisp.savedPSF[0:crop,0:crop]
            sump=sum(sum(psf))
            if sump != 0:
                psf =psf/sump
                
        datind=self.mapdata.labels.index(self.deconvsel.getvalue()[0])+2
        old=self.mapdata.data.get(datind)#[:,:,datind]
        if self.deconvWIN.getvalue()!=():
            newd=Deconv.deconvwnr(old,psf,filter=float(self.deconvWINp.getvalue()),NSR=float(self.deconvNSR.getvalue()))
        else:
            newd=Deconv.deconvwnr(old,psf,NSR=float(self.deconvNSR.getvalue()))
        globalfuncs.setstatus(self.ps.status,"DISPLAYING...")
        self.ps.maindisp.placeData(np.transpose(newd[::-1,:]),np.transpose(self.mapdata.mapindex[::-1,:]),self.ps.status,xax=self.mapdata.xvals,yax=self.mapdata.yvals)
        self.ps.showmap()        
        if result=='Save':
            self.ps.savedeconvcalculation(newd,self.newdecname.getvalue())
    
    def kill(self):
        self.win.withdraw()