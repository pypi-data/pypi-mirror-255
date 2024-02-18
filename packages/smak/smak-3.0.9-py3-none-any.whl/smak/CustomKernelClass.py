import os
import tkinter

import numpy as np
import Pmw

import globalfuncs
from MasterClass import MasterClass
import PmwTtkMenuBar

class CustomKernelWindowParams:
    def __init__(self, status, maindisp, showmap, savedeconvcalculation, filedir):
        self.status = status
        self.maindisp = maindisp
        self.showmap = showmap
        self.savedeconvcalculation = savedeconvcalculation
        self.filedir = filedir

class CustomKernelWindow(MasterClass):
    def _create(self):
        # self. ps = ps
        # self.mapdata = mapdata
        # self.imgwin = imgwin
        self.win=Pmw.Dialog(self.imgwin,title="Custom Kernel Filtering",buttons=('Preview','Save','Done'),defaultbutton='Done', command=self.enterCustFilter)
        h=self.win.interior()
        h.configure(background='#d4d0c8')

        menubar=PmwTtkMenuBar.PmwTtkMenuBar(h)
        if os.sys.platform=='win32': menubar.component('hull').configure(bg='#d4d0c8')
        #file menu
        menubar.addmenu('File','')
        menubar.addmenuitem('File','command',label='Load Parameters',command=self.loadKernelParams)
        menubar.addmenuitem('File','command',label='Save Parameters',command=self.saveKernelParams)
        menubar.pack(side=tkinter.TOP,fill=tkinter.X)
        
        lf=tkinter.Frame(h,background='#d4d0c8')
        lf.pack(side=tkinter.LEFT,fill='both')
        #data selection
        self.custfiltersel=Pmw.ScrolledListBox(lf,labelpos='n',label_text='Select Channel',items=self.mapdata.labels,listbox_selectmode=tkinter.SINGLE,
                                              listbox_exportselection=tkinter.FALSE,selectioncommand=self.selectcustfilterdata,listbox_height=15)
        self.custfiltersel.pack(side=tkinter.TOP,padx=4,pady=5,fill='both')
        #new data name
        self.newcustfiltername=Pmw.EntryField(lf,labelpos='w',label_text='New Channel Name: ',entry_width=15,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.newcustfiltername.pack(side=tkinter.TOP,fill=tkinter.X,pady=10)

        rf=tkinter.Frame(h,background='#d4d0c8')
        rf.pack(side=tkinter.LEFT,fill=tkinter.X,padx=15,anchor='n')
        l=tkinter.Label(rf,text='Filter Parameters',bd=2,relief=tkinter.RAISED,background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill=tkinter.X,expand=1,pady=5)

        #filter size
        self.custfilterFS=Pmw.ComboBox(rf,
                        scrolledlist_items=["3","5","7","9"],dropdown=1,
                        labelpos='w',label_text='Filter Size',history=0,label_background='#d4d0c8',hull_background='#d4d0c8',
                        selectioncommand=self.updatecustfiltinput)
        self.custfilterFS.selectitem('3',setentry=1)
        self.custfilterFS.pack(side=tkinter.TOP,fill=tkinter.X,expand=1,padx=5,pady=10)

        #data input area
        self.custfilterMat=customfilterDataObj(rf)

        self.win.show()
        self.win.userdeletefunc(func=self.kill)


    def updatecustfiltinput(self,*args):
        self.custfilterMat.update(self.custfilterFS.getvalue()[0])

    def selectcustfilterdata(self,*args):
        if self.custfiltersel.getvalue()==(): return
        name=self.custfiltersel.getvalue()[0]
        newname=name+'-ckf'
        i=1
        while newname in self.mapdata.labels:
            newname=name+'-ckf'+str(i)
            i+=1
        self.newcustfiltername.setvalue(newname)

    def enterCustFilter(self,result):
        if result=='Done':
            self.win.withdraw()
            return
        if len(self.custfiltersel.getvalue())<1:
            print('Select a data channel')
            return
        globalfuncs.setstatus(self.ps.status,"FILTERING...")

        datind=self.mapdata.labels.index(self.custfiltersel.getvalue()[0])+2
        old=self.mapdata.data.get(datind)#[:,:,datind]
        #make filter
        s=int(self.custfilterFS.getvalue()[0])
        self.custfilterMat.update(s)
        fs=sum(sum(self.custfilterMat.matrix[0:s,0:s]))
        if fs==0:
            fs=1
            print('warning, filter sum is zero, normalizing to 1')
        newd=globalfuncs.filterconvolve(old,self.custfilterMat.matrix[0:s,0:s])
        newd=newd/fs

        globalfuncs.setstatus(self.ps.status,"DISPLAYING...")
        self.ps.maindisp.placeData(np.transpose(newd[::-1,:]),np.transpose(self.mapdata.mapindex[::-1,:]),self.ps.status,xax=self.mapdata.xvals,yax=self.mapdata.yvals)
        self.ps.showmap()        
        if result=='Save':
            self.ps.savedeconvcalculation(newd,self.newcustfiltername.getvalue())
            self.custfiltersel.setlist(self.mapdata.labels)

    def saveKernelParams(self):
        #get fn
        fn=globalfuncs.ask_save_file('',self.ps.filedir.get())
        if fn=='':
            print('Save cancelled')
            return
        (fn,ext)=os.path.splitext(fn)
        fn=fn+'.kpm'
        fid=open(fn,'w')
        #assemble contents        
        text='SMAK KERNEL\n'
        text+=self.custfilterFS.getvalue()[0]+'\n' #squares
        text+='DATA\n'

        #make filter
        s=int(self.custfilterFS.getvalue()[0])
        self.custfilterMat.update(s)
        for i in range(s):
            nt=''
            for j in range(s):
                nt+=str(self.custfilterMat.matrix[i,j])+'\t'
            text+=nt+'\n'

        fid.write(text)
        fid.close()

    def loadKernelParams(self):
        global XHISTORY
        #get fn
        fty=[("KPM param files","*.kpm"),("all files","*")]
        fn=globalfuncs.ask_for_file(fty,self.ps.filedir.get())
        if fn=='':
            print('Load cancelled')
            return 
        #read first line
        fid=open(fn,'rU')
        l=fid.readline()
        if l!='SMAK KERNEL\n':
            print('Invalid parameter file!')
            fid.close()
            return    
        #read data
        numplaces=int(fid.readline())
        
        fid.readline() #data start
        mat=[]
        for n in range(numplaces):
            l=fid.readline().split()
            mat.append(list(map(float,l)))
        fid.close()

        #setup matrices
        self.custfilterFS.selectitem(str(numplaces),setentry=1)
        self.updatecustfiltinput()
        #place data
        self.custfilterMat.place(mat)
        ##self.custfilterMat
        
    def kill(self):
        self.win.withdraw()



#######################################
## Custom Kernel classes and funcs
#######################################

class customfilterDataObj:
    def __init__(self,frame):
        self.size=3
        self.frame=frame
        self.widlist=[]
        self.dataindex=[]
        self.matrix=np.zeros((9,9),dtype=np.float32)
        self.makewids()

    def makewids(self):
        uw=12
        #kill all
        for w in self.widlist:
            w.destroy()
        self.widlist=[]
        self.dataindex=[]
        #make anew...
        for r in range(self.size):
            ind=[]
            f=tkinter.Frame(self.frame,background='#d4d0c8')
            for i in range(self.size):
                #add data components
                l=Pmw.EntryField(f,value=self.matrix[r,i],entry_width=uw,validate='real',hull_background='#d4d0c8')
                l.pack(side=tkinter.LEFT)
                ind.append(l)
            f.pack(side=tkinter.TOP,fill=tkinter.BOTH)
            self.widlist.append(f)
            self.dataindex.append(ind)
            
    def update(self,size):
        size=int(size)
        #update data
        j=0
        for c in self.dataindex:
            for i in range(self.size):
                self.matrix[j,i]=float(c[i].getvalue())
            j+=1
        #make display if needed    
        if self.size!=size:
            self.size=size
            self.makewids()

    def place(self,mat):
        for i in range(len(mat)):
            for j in range(len(mat[i])):
                self.dataindex[i][j].setvalue(mat[i][j])


