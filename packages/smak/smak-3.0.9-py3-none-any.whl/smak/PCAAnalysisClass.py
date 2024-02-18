#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 23:11:15 2023

@author: samwebb
"""

import h5py
import math
import os
import struct
import time
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog

import numpy as np

import Display
import globalfuncs
from MasterClass import MasterClass
import MyGraph
import PCAAnalysisMathClass
import Pmw
import PmwTtkButtonBox
import PmwTtkMenuBar
import PmwTtkRadioSelect
import ScrollTree
import varimax


#MCA PCA type

class pcacompobj:
    def __init__(self):
        self.active=0
        self.eigen=0
        self.var=0
        self.vartot=0
        self.ind=0
        self.cind=0
        self.xdat=[]
        self.ydat=[]

class PCAParams:
    def __init__(self, getMCAfile, MCAfilename,  status, addchannel, dataFileBuffer, activeFileBuffer, filedir, PCAhdf5fout, HDFCOMPRESS):
        self.getMCAfile = getMCAfile
        self.MCAfilename = MCAfilename
        self.status = status
        self.addchannel = addchannel
        self.dataFileBuffer = dataFileBuffer
        self.activeFileBuffer = activeFileBuffer
        self.filedir = filedir
        self.PCAhdf5fout = PCAhdf5fout
        self.HDFCOMPRESS = HDFCOMPRESS
        

class PCAFullWindow(MasterClass):
    
    def _create(self):
        self.PCAdataLoaded=0
        #make window and unpack
        
        self.win=Pmw.MegaToplevel(self.imgwin)
        self.win.title('PCA Analysis')
        self.win.userdeletefunc(func=self.kill)           
        h=self.win.interior()
        h.configure(background='#d4d0c8')
        #menubar
        menubar=PmwTtkMenuBar.PmwTtkMenuBar(h)
        if os.sys.platform=='win32': menubar.component('hull').configure(bg='#d4d0c8')
        menubar.addmenu('Save','')
        menubar.addmenuitem('Save','command',label='Export Vectors to clipboard',command=self.curcomponenttoclip)
        menubar.addmenuitem('Save','separator')
        menubar.addmenuitem('Save','command',label='Save Vectors to Data',command=self.doMenuVectorSave)
        menubar.addmenuitem('Save','command',label='Save Components to File',command=self.curcomponenttofile)
        menubar.addmenu('Data','')
        menubar.addmenuitem('Data','command',label='Map data',command=self.PCAMAPbutpress)
        menubar.addmenuitem('Data','command',label='EXAFS data',command=self.PCAEXAFSbutpress)            
        menubar.addmenuitem('Data','separator')
        menubar.addmenuitem('Data','command',label='Define MCA file',command=self.loadMCAforPCA) #getPMCAfile)
        self.PCAcompressMCAplottoggle=tkinter.IntVar()
        self.PCAcompressMCAplottoggle.set(0)
        menubar.addmenuitem('Data','checkbutton',label='Compress MCA',command=tkinter.DISABLED,variable=self.PCAcompressMCAplottoggle)
        menubar.addmenu('Analysis','')
        self.PCAanalysisType=tkinter.StringVar()
        menubar.addcascademenu('Analysis','PCA Type')   #'sPCA','CCIPCA','FA','NMF',"FastICA",'Dictionary'
        menubar.addmenuitem('PCA Type','radiobutton',label='CCIPCA',command=tkinter.DISABLED,variable=self.PCAanalysisType)        
        menubar.addmenuitem('PCA Type','radiobutton',label='sPCA',command=tkinter.DISABLED,variable=self.PCAanalysisType)        
        menubar.addmenuitem('PCA Type','radiobutton',label='FA',command=tkinter.DISABLED,variable=self.PCAanalysisType) 
        menubar.addmenuitem('PCA Type','radiobutton',label='NMF',command=tkinter.DISABLED,variable=self.PCAanalysisType)
        menubar.addmenuitem('PCA Type','radiobutton',label='FastICA',command=tkinter.DISABLED,variable=self.PCAanalysisType)
        #menubar.addmenuitem('PCA Type','radiobutton',label='LDA',command=tkinter.DISABLED,variable=self.PCAanalysisType)            
        menubar.addmenuitem('PCA Type','radiobutton',label='Dictionary',command=tkinter.DISABLED,variable=self.PCAanalysisType)
        menubar.addmenuitem('Analysis','separator')            
        menubar.addmenuitem('Analysis','command',label='Do PCA',command=self.doPCA)
        menubar.addmenuitem('Analysis','command',label='Change Max PCA Components',command=self.editPCAMAX)
        menubar.addmenuitem('Analysis','command',label='Change MCA Range',command=self.editPCArange)
        menubar.addmenuitem('Analysis','separator')   
        #menubar.addmenuitem('Analysis','command',label='Do Varimax Rotation',command=self.dovarimax)
        menubar.addmenuitem('Analysis','command',label='Flip Negative Vectors',command=self.doNnorm)
        menubar.addmenuitem('Analysis','command',label='Save Vectors to Data',command=self.doMenuVectorSave)
        menubar.addmenuitem('Analysis','separator')  
        menubar.addmenuitem('Analysis','command',label='Channel Reconstruction',command=self.doPCAReconstruction)
        menubar.pack(side=tkinter.TOP,fill=tkinter.X)
        self.PCAanalysisType.set('sPCA')
        #buttons on left
        bf=tkinter.Frame(h,background='#d4d0c8')
        bf.pack(side=tkinter.TOP,fill='both')
        mf=tkinter.Frame(bf,relief=tkinter.SUNKEN,bd=2,background='#d4d0c8')
        mf.pack(side=tkinter.TOP,fill='both')
        ###################### no need for lft/lf division if only one plot bar
        lf=tkinter.Frame(mf,background='#d4d0c8')
        lf.pack(side=tkinter.LEFT,fill='both')
        lft=tkinter.Frame(lf,background='#d4d0c8')
        lft.pack(side=tkinter.LEFT,fill='both',padx=5)
        bb=PmwTtkButtonBox.PmwTtkButtonBox(lft,labelpos='n',label_text='Data Options',orient='vertical',pady=3,frame_background='#d4d0c8',hull_background='#d4d0c8',label_background='#d4d0c8')
        w=15
        #JOY Q: replaced swidth with width, tkinter.W with w
        self.PCAMCAbut=bb.add('Map data',command=self.PCAMAPbutpress,style='FIREB.TButton',width=w)
        self.PCASCAbut=bb.add('EXAFS data',command=self.PCAEXAFSbutpress,style='FIREB.TButton',width=w)
        bb.add('Define MCA file',command=self.loadMCAforPCA,style='NAVY.TButton',width=w)
        bb.pack(side=tkinter.TOP,fill='both',pady=5)
        bb=PmwTtkButtonBox.PmwTtkButtonBox(lft,labelpos='n',label_text='Analysis',orient='vertical',pady=3,frame_background='#d4d0c8',hull_background='#d4d0c8',label_background='#d4d0c8')
        bb.add('Do Analysis',command=self.doPCA,style='NAVY.TButton',width=w)
        #bb.add('Do Varimax',command=self.dovarimax,style='NAVY.TButton',width=tkinter.W)
        bb.add('Flip Negative',command=self.doNnorm,style='NAVY.TButton',width=w)
        self.PCAsavebut=bb.add('Save',command=self.doVectorSave,style='BROWN.TButton',width=w)            
        bb.pack(side=tkinter.TOP,fill='both',pady=5)
        #display on right
        rf=tkinter.Frame(mf,background='#d4d0c8')
        rf.pack(side=tkinter.LEFT,fill='both')
        self.PCAgraph=MyGraph.MyGraph(rf,whsize=(6,3),tool=1)
        #self.PCAgraph.legend_configure(hide=1)
        #self.PCAgraph.pack(side=tkinter.TOP,expand=1,fill='both',padx=2)
        #self.PCAgraph.bind(sequence="<ButtonPress>",   func=self.PCAmouseDown)
        #self.PCAgraph.bind(sequence="<ButtonRelease>", func=self.PCAmouseUp  )
        #self.PCAgraph.bind(sequence="<Motion>", func=self.PCAcoordreport)
        xyf=tkinter.Frame(rf,background='#d4d0c8')
        xyf.pack(side=tkinter.TOP,fill='both')
        #self.PCAxcoord=tkinter.Label(xyf,text="X=     ",width=15,bd=2,relief=tkinter.RIDGE,anchor=tkinter.W,fg='red')
        #self.PCAycoord=tkinter.Label(xyf,text="Y=     ",width=15,bd=2,relief=tkinter.RIDGE,anchor=tkinter.W,fg='red')
        #self.PCAycoord.pack(side=tkinter.RIGHT,fill=tkinter.X)
        #self.PCAxcoord.pack(side=tkinter.RIGHT,fill=tkinter.X)
        #component list at bottom
        cf=tkinter.Frame(bf,background='#d4d0c8')
        cf.pack(side=tkinter.TOP,fill='both')
        l=tkinter.Label(cf,text='Component Info',bd=2,relief=tkinter.RAISED,background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill='both')  
        #limit component display to 10 values?
        self.PCAcompMAXNO=10
        self.PCAminbin=0
        self.PCAmaxbin=2048
        #add btree legend
        self.complist=ScrollTree.ScrolledTreeViewBox(cf,width=400)
        self.complist.setMode('browse')
        self.complist.setColNames((" ","Comp.","Eigen","Var.","Cum Var.","IND"))
        self.complist.setDefaultWA()
        self.complist.setOpen(self.choosecomp)
        self.complist.setSelect(self.PCAplotcomponent)
        self.complist.pack(side=tkinter.TOP,fill=tkinter.BOTH,expand=1,padx=2,pady=2)
        #init variables for PCA components
        self.compfiles=[]
        self.compvars={}
        self.PCAdataStruct=None
        #reset PCA data type to null            
        self.PCAdatatype='none'            
        self.win.show()

    def kill(self):
        self.exist=0
        self.PCAdatatype='none' 
        try:
            del self.PCAdataStruct
        except:
            pass
        self.PCAdataStruct=None        
        self.win.destroy()

    def getPMCAfile(self):
        self.ps.getMCAfile()
        self.win.focus()
        
    def PCAMAPbutpress(self):
        if self.ps.MCAfilename=='' or self.PCAdatatype=='none':
            result,self.ps.MCAfilename=self.ps.getMCAfile(retval=True)
            if not result:
                self.win.focus()
                return
        self.win.focus()
        self.PCAMCAbut.configure(style='GREEN.TButton')
        self.PCASCAbut.configure(style='FIREB.TButton')
        self.PCAdatatype='MAP'
        self.PCAsavebut.config(command=self.doVectorSave,text='Save to Map')
        self.loadMCAforPCA()

    def PCAEXAFSbutpress(self):
        if self.ps.MCAfilename=='' or self.PCAdatatype=='none':
            result,self.ps.MCAfilename=self.ps.getMCAfile(pex=True,retval=True)
            if not result:
                self.win.focus()
                return
        self.win.focus()
        self.PCAMCAbut.configure(style='FIREB.TButton')
        self.PCASCAbut.configure(style='GREEN.TButton')
        self.PCAdatatype='EXAFS'
        self.PCAsavebut.config(command=self.doVectorEXAFSSave,text='Save to EXAFS')        
        self.loadMCAforPCA()
        
    def editPCAMAX(self):
        new=tkinter.simpledialog.askinteger('PCA Components','Enter max number of PCA components: ',initialvalue=self.PCAcompMAXNO)
        self.PCAcompMAXNO=new
        if new==0:
            self.PCAcompMAXFixed=False
        else:
            self.PCAcompMAXFixed=True
        try:
            self.win.focus()
        except:
            pass       


    def doPCA(self):
        #check arrays
        print(self.PCAdatatype)
        if self.PCAdatatype[-1]!='L':
            print("Import MCA data first")
            globalfuncs.setstatus(self.ps.status,"Import MCA data first")
            return
        globalfuncs.setstatus(self.ps.status,"WORKING ON PCA")        
        #try new
        ntm=[]
        ntm.append(time.process_time())
        self.PCAdataStruct.donewPCA(pcatype=self.PCAanalysisType.get(),MCA=True)
        ntm.append(time.process_time())
        print('PCA complete in '+str(ntm[1]-ntm[0])+' seconds')
        #compute sum
        esum=sum(self.PCAdataStruct.PCAeval)
        ecsum=[]
        for i in range(len(self.PCAdataStruct.PCAeval)):
            ecsum.append(sum(self.PCAdataStruct.PCAeval[0:i+1]))
        ecsum=np.array(ecsum)
        varcomp=self.PCAdataStruct.PCAeval/esum
        varexp=ecsum/esum
        #clear old results
        self.compfiles=[]
        self.compvars={}
        self.complist.clear()
        #give results in list window
        evect=np.transpose(self.PCAdataStruct.PCAevect) #put eigenvectors back to rows
        for c in range(self.PCAcompMAXNO): #not cols in this case -- LIMIT
            #add component...
            wid=pcacompobj()
            #wid.xdat=arange(self.mcamaxno)
            ytemp=np.take(evect,(c,),axis=0) #slice of eigevector
            ytup=tuple(ytemp[0])
            wid.ydat=np.array(ytup)
            wid.xdat=np.arange(len(wid.ydat))+self.PCAminbin         
            wid.eigen=self.PCAdataStruct.PCAeval[c]
            wid.var=varcomp[c]
            wid.vartot=varexp[c]
            wid.ind=0#rateind[c]
            wid.cind=c
            rn=str(c+1)
            name='Comp'+rn
            self.compfiles.append(name)
            self.compvars.update({name:wid})
            #self.complist.add(name,text=" ",state=tkinter.NORMAL)
            #self.complist.item_create(name,1,text=name)
            #self.complist.item_create(name,2,text=globalfuncs.valueclip_d(wid.eigen,4))
            #self.complist.item_create(name,3,text=globalfuncs.valueclip_d(wid.var,4))
            #self.complist.item_create(name,4,text=globalfuncs.valueclip_d(wid.vartot,4))
            if wid.ind !=0:
                e6=globalfuncs.valueclip_d(wid.ind,6)#self.complist.item_create(name,5,text=globalfuncs.valueclip_d(wid.ind,6))
            else:
                e6=' NA '#self.complist.item_create(name,5,text=' NA ')
            self.complist.insert((" ",name,globalfuncs.valueclip_d(wid.eigen,4),globalfuncs.valueclip_d(wid.var,4),globalfuncs.valueclip_d(wid.vartot,4),e6),addchild=True)    
            #self.complist.listbox.selection_set([])

            #make active
            ##self.complist.item_configure(name,0,text=' ')
        self.PCAplotcomponent()
        globalfuncs.setstatus(self.ps.status,"PCA Analysis complete")             

    def dovarimax(self):
        scale=0  #do varimax on unscaled vectors???
        #make sure pca is run
        if self.compfiles==[]:
            print('Do PCA first')
            globalfuncs.setstatus(self.ps.status,"Do PCA first")   
            return
        #unselect last component if all are checked... and get active components
        i=0
        ii=0
        ind=[]
        for npc in self.compfiles:
            dat=self.compvars.get(npc)
            if dat.active==1:
                i=i+1
                ind.append(ii)
            ii=ii+1
        if i==len(self.compfiles):
            dat.active=0
            cwid=self.complist.listbox.item(i-1)
            self.complist.listbox.itemelement_config(cwid,self.complist.listbox.column(0),self.complist.listbox.element('text'),text=' ')            
            #self.complist.item_configure(np,0,text=' ')
            ind.pop()
        if len(ind)==0:
            print('Please select componenets to rotate')
            globalfuncs.setstatus(self.ps.status,"Please select componenets to rotate")   
            return
        globalfuncs.setstatus(self.ps.status,"Doing Varimax rotation")          
        #make new uevect matrix
        if scale==0:
            newevect=np.take(self.PCAdataStruct.PCAuevect,ind,axis=1)
        else:
            newevect=np.take(self.PCAdataStruct.PCAevect,ind,axis=1)
        (a,b)=varimax.varimax(newevect.copy())
        #make new comp matrix
        rotevect=b
        trevect=np.transpose(rotevect)
        #put these back in the data columns... (ugh)
        i=0
        for npc in self.compfiles:
            dat=self.compvars.get(npc)
            if dat.active==1:
                #replace
                ytemp=np.take(trevect,(i,),axis=0) #slice of eigevector
                ytup=tuple(ytemp[0])
                dat.ydat=np.array(ytup)
            else:
                #replace with zeros
                ytemp=np.zeros(np.take(trevect,(0,),axis=0).shape)
                ytup=tuple(ytemp[0])
                dat.ydat=np.array(ytup)
            i=i+1
        #rotate proportions?
        tprop=self.PCAdataStruct.PCAprop.copy()#transpose(self.PCAprop)
        nprop=np.take(tprop,ind,axis=1)
        if scale==0:
            neweval=np.take(self.PCAdataStruct.PCAeval,ind,axis=0)
            newevalmat=np.identity(len(neweval))*neweval
            first=np.dot(np.transpose(a),newevalmat)
            rtprop=np.dot(first,np.transpose(nprop))
        if scale==1:
            rtprop=np.dot(np.transpose(a),np.transpose(nprop))
        rtprop=np.transpose(rtprop)
        #make the rest of the props zeros
        newprop=np.zeros(self.PCAdataStruct.PCAprop.shape,dtype=np.float64)
        ii=0
        l=newprop.shape[0]
        for i in ind:
            #replace rows/cols?
            newprop[:,i]=rtprop[:,ii]#put(newprop,range(i*l,(i+1)*l),rtprop[ii,:])
            ii=ii+1
        self.PCAdataStruct.PCAprop=newprop.copy()     
        self.PCAplotcomponent()  
        globalfuncs.setstatus(self.ps.status,"Varimax rotation of selected scaled components completed")
  
    def PCAplotcomponent(self,*args):
        ind=self.complist.curselection()##self.complist.info_selection()
        if len(ind)==0:
            print (ind)
            return
        ind=ind[0]
        cur=self.compfiles[ind]
        dat=self.compvars.get(cur)
        xd=tuple(dat.xdat)
        yd=tuple(dat.ydat)
        #make plot          
        #first remove current plot(s) if not stacking
        self.PCAgraph.cleargraphs()
##        glist=self.PCAgraph.element_names()
##        if glist !=():
##            for g in glist:
##                self.PCAgraph.element_delete(g)
        #make plot
        #self.PCAgraph.line_create('PCA',xdata=xd,ydata=yd,symbol='',color='green')
        self.PCAgraph.plot(xd,yd,text='PCA',color='green')
        self.PCAgraph.draw()
        
    def doNnorm(self):
        #check for negative eigenvectors and reverse sign -- and props.
        #make sure pca is run
        if self.compfiles==[]:
            print('Do PCA first')
            globalfuncs.setstatus(self.ps.status,"Do PCA first")   
            return
        globalfuncs.setstatus(self.ps.status,"Checking for negative eigenvectors")         
        for npc in self.compfiles:
            wid=self.compvars.get(npc)
            #find max/min of y values
            dmax=max(wid.ydat)
            dmin=min(wid.ydat)
            if abs(dmin)>abs(dmax):
                #needs to be inversed
                wid.ydat=-wid.ydat
                #need to adjust in uevect and evect
                t=self.PCAdataStruct.PCAevect[wid.cind,:]
                self.PCAdataStruct.PCAevect[wid.cind,:]=-t
                t=self.PCAdataStruct.PCAuevect[wid.cind,:]
                self.PCAdataStruct.PCAuevect[wid.cind,:]=-t
                #need to adjust wt matrix:
                z=np.transpose(self.PCAdataStruct.PCAprop)
                t=z[wid.cind,:]
                z[wid.cind,:]=-t
                self.PCAdataStruct.PCAprop=np.transpose(z)
        self.PCAplotcomponent()        
        globalfuncs.setstatus(self.ps.status,"Ready")         

    def doVectorSave(self):
        #want to export wieght matrix as a data set for active components...
        #make sure pca is run
        if self.compfiles==[]:
            print('Do PCA first')
            globalfuncs.setstatus(self.ps.status,"Do PCA first")   
            return
        globalfuncs.setstatus(self.ps.status,"Exporting selected component weights to map dataset...")         
        for npc in self.compfiles:
            wid=self.compvars.get(npc)
            if wid.active==1:
                #export this one...
                noexit=1
                name='Comp'
                while noexit:
                    name=name+str(wid.cind+1)
                    if name not in self.mapdata.labels:
                        noexit=0
                data=self.PCAdataStruct.PCAprop[:,wid.cind]
                #if compression on, reset lengths:
                if self.PCAcompressMCAplottoggle.get()==1:
                    x=int(self.mapdata.nxpts/2)
                    y=int(self.mapdata.nypts/2)
                    data=np.reshape(data,(y,x))
                    #print self.mapdata.data.shape,data.shape,self.mapdata.nxpts,self.mapdata.nypts
                    ndata=np.zeros(self.mapdata.data.get(0).shape,dtype=np.float64)
                    for i in range(self.mapdata.nxpts):
                        for j in range(self.mapdata.nypts):
                            try:
                                ndata[j,i]=data[int(j/2),int(i/2)]
                            except:
                                #print i,j
                                pass
                    data=np.ravel(ndata)
                #reshape data and check lengths
                data=data[:len(np.ravel(self.mapdata.data.get(0)))]
                ##print data.shape,self.mapdata.data[:,:,0].shape
                data=np.reshape(data,(self.mapdata.data.get(0).shape))
                #add to mapdata
                self.ps.addchannel(data,name)
        globalfuncs.setstatus(self.ps.status,"Done!")

    def doVectorEXAFSSave(self):
        #make sure pca is run
        if self.compfiles==[]:
            print('Do PCA first')
            globalfuncs.setstatus(self.ps.status,"Do PCA first")   
            return
        exind='none'
        for npc in self.compfiles:
            wid=self.compvars.get(npc)
            if wid.active==1:
                #export this one...
                exind=wid.cind
                data=self.PCAdataStruct.PCAprop[:,wid.cind]
        if exind=='none':
            print('No components selected')
            globalfuncs.setstatus(self.ps.status,"No components selected")   
            return        
        globalfuncs.setstatus(self.ps.status,"Exporting selected component weights to an EXAFS dataset...")
        #get EXAFS file name now.
        fty=[("avg files","*.avg"),("dat files","*.dat"),("all files","*")]
        efn=globalfuncs.ask_for_file(fty,self.filedir.get())
        if efn=='':
            print('Save cancelled')
            globalfuncs.setstatus(self.ps.status,'Save cancelled')
            return
        #read energy values...
        fid=open(efn,'rU')
        lines=fid.read().split('\n')
        fid.close()
        #parse
        exafsx=[]
        for line in lines:
            if len(line)>0 and (line[0] not in ['#','%','!','*']):
                exafsx.append(float(line.split()[0]))
        #check lengths of files/weights
        print(len(exafsx),len(data))
        if len(exafsx)!=len(data):
            print('WARNING: MCA data size does not match EXAFS data size')
        #get save file name
        efn=globalfuncs.trimdirext(efn)+'_PCA.avg'
        fn=globalfuncs.ask_save_file(efn,self.filedir.get())
        if fn=='':
            print('Save cancelled')
            globalfuncs.setstatus(self.ps.status,'Save cancelled')
            return
        fid=open(fn,'w')
        fid.write('# EXAFS data created from PCA data in SMAK\n')
        maxdatlen=min(len(exafsx),len(data))
        for i in range(maxdatlen):
            fid.write(str(exafsx[i])+'\t'+str(data[i])+'\n')
        fid.close()        
        self.win.focus()
        globalfuncs.setstatus(self.ps.status,"Save completed")        

    def doMenuVectorSave(self):
        #make sure pca is run
        if self.compfiles==[]:
            print('Do PCA first')
            globalfuncs.setstatus(self.ps.status,"Do PCA first")   
            return
        if self.PCAdatatype[0]=='M':
            self.doVectorSave()
        if self.PCAdatatype[0]=='E':
            self.doVectorEXAFSSave()
        print('ERROR IN PCA DATA TYPE')

    def doPCAReconstruction(self):
        #make sure pca is run
        if self.compfiles==[]:
            print('Do PCA first')
            globalfuncs.setstatus(self.ps.status,"Do PCA first")   
            return
        [cset,ind]=self.getcurcomponents(full=True)
        cset=np.array(cset)
        if ind==0:
            print('no components')
            return
        length=len(ind)
        #get limits
        n=tkinter.simpledialog.askinteger(title='PCA Reconstruction Limits',prompt='Set Minimum MCA Bin for PCA',initialvalue=str(self.PCAminbin))
        if n is None:
            return
        recminbin=n-self.PCAminbin       
        if recminbin<self.PCAminbin or recminbin<0:
            print("requested minimum outside of PCA range")
            return
        n=tkinter.simpledialog.askinteger(title='PCA Reconstruction Limits',prompt='Set Maximum MCA Bin for PCA',initialvalue=str(cset.shape[1]+self.PCAminbin))
        if n is None:
            return
        recmaxbin=n-self.PCAminbin
        if recmaxbin>self.PCAmaxbin:
            print("requested maximum outside of PCA range")
            return
        #integrate
        iset=np.sum(cset[:,recminbin:recmaxbin],axis=1)
        #make reconstruction
        
        data=[]
        for i in range(length):
            data.append(self.PCAdataStruct.PCAprop[:,ind[i]]*iset[i])
        data=np.array(data)
        data=np.sum(data,axis=0)
        print(data.shape)
        #create channel            
        #reshape data and check lengths
        data=data[:len(np.ravel(self.mapdata.data.get(0)))]
        ##print data.shape,self.mapdata.data[:,:,0].shape
        data=np.reshape(data,(self.mapdata.data.get(0).shape))
        #add to mapdata
        noexit=1
        name='Recon'
        nindex=1
        while noexit:
            tname=name+str(nindex)
            if tname not in self.mapdata.labels:
                noexit=0   
            nindex+=1
        self.ps.addchannel(data,tname)
        globalfuncs.setstatus(self.ps.status,"Done!")           

    def getcurcomponents(self,full=False):
        #make sure pca is run
        if self.compfiles==[]:
            print('Do PCA first')
            globalfuncs.setstatus(self.ps.status,"Do PCA first")   
            return [0,0]
        ind=[]
        data=[]
        for npc in self.compfiles:
            wid=self.compvars.get(npc)
            if wid.active==1:
                #export this one...
                ind.append(wid.cind)
                data.append(wid.ydat)
        if ind==[]:
            print('No components selected')
            globalfuncs.setstatus(self.ps.status,"No components selected")   
            return [0,0]
        if not full: return [data,len(ind)]
        else: return [data,ind]

    def curcomponenttoclip(self):
        globalfuncs.setstatus(self.ps.status,"Ready")        
        [data,nocomp]=self.getcurcomponents()
        if data==0:
            return
        text='MCA Bin\t'
        for i in range(nocomp):
            text=text+'Comp'+str(i+1)+'\t'
        text=text+'\n'
        #parse list now
        for i in range(len(data[0])):
            #setup text
            text=text+str(i+1)+'\t'
            for j in range(nocomp):
                text=text+str(data[j][i])+'\t'
            text=text+'\n'
        #export to clipboard
        self.imgwin.clipboard_clear()
        self.imgwin.clipboard_append(text)
        globalfuncs.setstatus(self.ps.status,"Active component data saved to clipboard")
        


    def curcomponenttofile(self):
        globalfuncs.setstatus(self.ps.status,"Ready")  
        [data,nocomp]=self.getcurcomponents()
        if data==0:
            return
        fn=globalfuncs.ask_save_file(globalfuncs.trimdirext(self.ps.dataFileBuffer[self.ps.activeFileBuffer]['fname'])+'_PCAcomp.dat',self.ps.filedir.get())
        if fn=='':
            print('Save cancelled')
            globalfuncs.setstatus(self.ps.status,'Save cancelled')
            return
        fid=open(fn,'w')
        fid.write('# Principal componets for '+globalfuncs.trimdirext(self.ps.dataFileBuffer[self.ps.activeFileBuffer]['fname'])+'\n')
        fid.write('MCA Bin\t')
        for i in range(nocomp):
            fid.write('Comp'+str(i)+'\t')
        fid.write('\n')
        #parse list now
        for i in range(len(data[0])):
            #setup text
            fid.write(str(i+1)+'\t')
            for j in range(nocomp):
                fid.write(str(data[j][i])+'\t')
            fid.write('\n')
        fid.close()
        globalfuncs.setstatus(self.ps.status,"Active component data saved to file:"+fn)        

    
    def editPCArange(self):
        n=tkinter.simpledialog.askinteger(title='PCA MCA Limits',prompt='Set Minimum MCA Bin for PCA',initialvalue=str(self.PCAminbin))
        if n is None:
            return
        self.PCAminbin=n        
        n=tkinter.simpledialog.askinteger(title='PCA MCA Limits',prompt='Set Maximum MCA Bin for PCA',initialvalue=str(self.PCAmaxbin))
        if n is None:
            return
        self.PCAmaxbin=n 
        if not(self.ps.MCAfilename=='' or self.PCAdatatype=='none'):
            self.loadMCAforPCA()
    

    def choosecomp(self, arg):
        ind=arg
        print (arg)
        if type(ind)==type((1,)) or type(ind)==type([0]): ind=ind[0]
        if ind==-1: return
        cur=self.compfiles[ind]
        wid=self.compvars.get(cur)
        cwid=self.complist.getitem(ind)
        if wid.active==0:
            
            #turn on
            wid.active=1
            self.complist.itemEditAtPos(cwid,0,'X')
        else:
            #turn off
            wid.active=0
            self.complist.itemEditAtPos(cwid,0,' ')
        self.compvars.update({cur:wid})


    def loadMCAforPCA(self,justload=0):  
        globalfuncs.setstatus(self.ps.status,'Loading MCA data...')
        i=0
        #open MCA file and read all!:
        (fn,ext)=os.path.splitext(self.ps.MCAfilename)
        if ext==".bmd":
            pcarawdata=self.getBinaryMCAforPCA()
        elif ext==".hdf5":
            pcarawdata=self.getHDF5MCAforPCA()
            justload=2
        else:
            fid=open(self.ps.MCAfilename,"rU")
            if self.mapdata.type=='BL62TXM':
                self.mcamaxno=int(fid.readline().split()[2])
                fid.readline()
            else:
                self.mcamaxno=2048
            pcarawdata=[]
            lines=fid.read().split('\n')
            fid.close()
            lnum=0
            inc=10
            next=inc
            for i in range(self.MCA1stpixoffs):
                pcarawdata.append(np.zeros(self.mcamaxno,dtype=np.float32))
            for line in lines:
                i=0
                temp=[]
                for p in line.split():
                    if i!=0:
                        temp.append(float(p))
                    i=i+1
                pcarawdata.append(np.array(temp).astype(np.float32))
                lnum=lnum+1
                if divmod(lnum,self.mapdata.nxpts)[1]==0 and self.MCApixoffs!=0:
                    for j in range(abs(self.MCApixoffs)):
                        pcarawdata.append(np.zeros(self.mcamaxno,dtype=np.float32))
                        lnum=lnum+1
                if lnum>=next*len(lines)/100:
                    print(str(next)+'% loaded')
                    next=next+inc
            i=0
        print('verifying...')
        if not justload:
            for m in pcarawdata:
                if len(m) !=len(pcarawdata[1]):
                    if i==0:
                        pcarawdata[i]=pcarawdata[1]
                    else:
                        pcarawdata[i]=pcarawdata[i-1]
                i=i+1
        while len(pcarawdata)<self.mapdata.nxpts*self.mapdata.nypts:
            pcarawdata.append(np.zeros(self.mcamaxno,dtype=np.float32))
        #make this a loop?
        while len(pcarawdata)>self.mapdata.nxpts*self.mapdata.nypts:
            pcarawdata.pop()
        pcarawdata=np.array(pcarawdata).astype(np.float32)
        #check for "oversize"
        #print pcarawdata.shape
        if justload==1: return
        if pcarawdata.shape[0]>15000 and self.PCAcompressMCAplottoggle.get()==0: #may be to big for 2GB ram machines to do PCA...
            print("MCA data may be too large for 2GB of RAM -- use MCA compression")
        if self.PCAcompressMCAplottoggle.get()==1:
            #do averaging:
            x=int(self.mapdata.nxpts/2)
            y=int(self.mapdata.nypts/2)
            mdata=np.zeros((y,x,self.mcamaxno),dtype=np.float64)
            pcarawdata=np.reshape(pcarawdata,(self.mapdata.nypts,self.mapdata.nxpts,self.mcamaxno))
            for j in range(x):
                for i in range(y):
                    t=[]
                    try:
                        t.append(pcarawdata[2*i,2*j,:])
                    except:
                        pass
                    try:
                        t.append(pcarawdata[2*i+1,2*j,:])
                    except:
                        pass
                    try:
                        t.append(pcarawdata[2*i+1,2*j+1,:])
                    except:
                        pass
                    try:
                        t.append(pcarawdata[2*i,2*j+1,:])
                    except:
                        pass
                    l=len(t)
                    t=np.array(t)
                    mdata[i,j,:]=sum(t)/l
##                    cx=2*i+1
##                    cy=2*j+1
##                    t=pcarawdata[cx+self.mapdata.nxpts*cy,:]
##                    t=t+pcarawdata[cx+self.mapdata.nxpts*cy-1,:]
##                    t=t+pcarawdata[cx+self.mapdata.nxpts*cy+1,:]
##                    t=t+pcarawdata[cx+self.mapdata.nxpts*(cy-1),:]
##                    t=t+pcarawdata[cx+self.mapdata.nxpts*(cy+1),:]
##                    mdata[i+j,:]=t/5
            #print pcarawdata.shape,mdata.shape
            mdata=mdata.astype(np.float32)
            pcarawdata=np.reshape(mdata,(x*y,self.mcamaxno))
        self.PCAdatatype=self.PCAdatatype+'L'
        print("Done")
        globalfuncs.setstatus(self.ps.status,"MCA data import complete.")
        self.PCAdataStruct = PCAAnalysisMathClass.PCADataStructure(pcarawdata,self.PCAcompMAXNO,self.imgwin)


    def getBinaryMCAforPCA(self):
        fid=open(self.ps.MCAfilename,"rb")
        self.mcamaxno=struct.unpack('i',fid.read(4))[0]
        newdata=[]
        for i in range(self.MCA1stpixoffs):
            newdata.append(np.zeros(self.mcamaxno,dtype=np.float32))
        lnum=0
        linenum=0
        inc=10
        early=0
        next=inc
        matsize=self.mapdata.data.shape[0]*self.mapdata.data.shape[1]
        while linenum<matsize:
            try:
                linenum=int(struct.unpack("f",fid.read(4))[0])
                line=fid.read(self.mcamaxno*4)
            except:
                early=1
                linenum+=1
                globalfuncs.setstatus(self.ps.status,'MCA data, EOF...')
            if not early:
                fmt=str(self.mcamaxno)+"f"
                newdata.append(np.array(struct.unpack(fmt,line)).astype(np.float32))            
                lnum+=1
            else:
                newdata.append(np.zeros(self.mcamaxno,dtype=np.float32))
                lnum+=1
            if divmod(lnum,self.mapdata.nxpts)[1]==0 and self.MCApixoffs!=0:
                for j in range(abs(self.MCApixoffs)):
                    newdata.append(np.zeros(self.mcamaxno,dtype=np.float32))
                    lnum=lnum+1
            if lnum>=next*matsize/100:
                print(str(next)+'% loaded')
                next=next+inc

        fid.close()
        return newdata        

    def getHDF5MCAforPCA(self):

        fid=h5py.File(self.ps.MCAfilename)
        if "/main/mcadata" in fid:
            mcadata=fid['/main/mcadata']
        elif "/main/oodata" in fid:
            mcadata=fid['/main/oodata']
        else:
            print('no mcadata found')
            return
        self.mcamaxno=mcadata.shape[1]
        maxlines=mcadata.shape[0]
        print('hdf',self.mcamaxno,maxlines)
        
        if self.ps.PCAhdf5fout is not None:
            self.ps.PCAhdf5fout.close()
        self.ps.PCAhdf5fout=h5py.File("mcatemp.hdf5",'w')
        groupout=self.ps.PCAhdf5fout.create_group("main")
        matsize=self.mapdata.data.shape[0]*self.mapdata.data.shape[1]

        pcasize=self.PCAmaxbin-self.PCAminbin

        if self.ps.HDFCOMPRESS.get()=="GZIP 4":
            newdata=groupout.create_dataset("mcadata",(matsize,pcasize),maxshape=(None,pcasize),dtype='int',compression="gzip",compression_opts=4)
        elif self.ps.HDFCOMPRESS.get()=="GZIP 9":
            newdata=groupout.create_dataset("mcadata",(matsize,pcasize),maxshape=(None,pcasize),dtype='int',compression="gzip",compression_opts=9)
        elif self.ps.HDFCOMPRESS.get()=="LZF":
            newdata=groupout.create_dataset("mcadata",(matsize,pcasize),maxshape=(None,pcasize),dtype='int',compression="lzf")           
        else:
            newdata=groupout.create_dataset("mcadata",(matsize,pcasize),maxshape=(None,pcasize),dtype='int')

        #newdata=np.zeros((matsize,2048))

        if maxlines==matsize:
            newdata=np.array(mcadata[:,self.PCAminbin:self.PCAmaxbin])

        if maxlines<matsize:
            newdata[self.MCA1stpixoffs:self.MCA1stpixoffs+maxlines,:pcasize]=mcadata[:,self.PCAminbin:self.PCAmaxbin]

        if maxlines>matsize:
            newdata[:,:pcasize]=mcadata[:matsize,self.PCAminbin:self.PCAmaxbin]
        
                
        
        fid.close()
        return newdata        
            
     
            
