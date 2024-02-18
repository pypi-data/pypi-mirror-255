#standard 
import os
import re
import sys
import time
import tkinter
from tkinter.ttk import Button


#third party
import numpy as np
import Pmw
import scipy.optimize

#local
import globalfuncs
from MasterClass import MasterClass
import NNLS
import PmwTtkMenuBar


global XHISTORY
XHISTORY=[]

class xanesfitobj:
    def __init__(self,frame,display=True):
        self.columns=[]
        ini=['Names','Fit1','Fit2']
        self.columns.append(ini)
        self.frame=frame
        self.widlist=[]
        self.dataindex=[]
        self.display=display
        if display: self.makewids()

    def makewids(self):
        uw=12
        #kill all
        for w in self.widlist:
            w.destroy()
        self.widlist=[]
        self.dataindex=[]
        #make anew...
        for c in self.columns:
            ind=[]
            f=tkinter.Frame(self.frame,background='#d4d0c8')
            #add header
            l=tkinter.Label(f,text=c[0],width=uw,background='#d4d0c8')
            l.pack(side=tkinter.TOP)
            ind.append(l)
            for i in range(1,len(c)):
                #add components
                l=Pmw.EntryField(f,value=c[i],entry_width=uw,hull_background='#d4d0c8')
                l.pack(side=tkinter.TOP)
                ind.append(l)
            f.pack(side=tkinter.LEFT,fill=tkinter.BOTH)
            self.widlist.append(f)
            self.dataindex.append(ind)
            
    def update(self,data,stds):
        global XHISTORY
        stds=int(stds)
        #update data
        olddata=[]
        for c in self.dataindex:
            temp=[]
            for i in range(len(c)):
                if i==0: temp.append(c[i].cget('text'))
                else: temp.append(c[i].getvalue())
            olddata.append(temp)
        #update history
        for c in olddata[1:]:
            hind=0
            ins=1
            for h in XHISTORY:
                if c[0]==h[0]:
                    if len(c)>=len(h):
                        XHISTORY.pop(hind)
                        XHISTORY.append(c)
                        ins=0
                hind=hind+1
            if ins: XHISTORY.append(c)
        #create index
        oldnames=[]
        for d in XHISTORY:#olddata:
            if d[0]!='Names': oldnames.append(d[0])
        self.columns=[]
        #make new title column
        newc=[]
        for i in range(stds+1):
            try:
                newc.append(olddata[0][i])
            except:
                newc.append('Fit'+str(i))
        self.columns.append(newc)
        for d in data:
            newc=[]
            newc.append(d)
            for i in range(stds):
                newc.append(0.0)
            #check for old data
            if d in oldnames:
                dind=oldnames.index(d)
                for i in range(stds):
                    try:
                        newc[i+1]=XHISTORY[dind][i+1] #olddata
                    except:
                        pass
            #append
            self.columns.append(newc)
        #make display    
        if self.display: self.makewids()

class xanesMuLoadObject:
    def __init__(self,master,name,dir=''):

        self.dir=dir        
        
        f=tkinter.Frame(master,bd=2,background='#d4d0c8')
        self.cb=Pmw.RadioSelect(f,label_text =name,labelpos='w',hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        self.cb.pack(side=tkinter.LEFT,padx=5,pady=5)
        for bt in ["Yes","No"]:
            self.cb.add(bt,background='#d4d0c8')
        self.cb.invoke("No")
        filebar=tkinter.Frame(f,bd=2,background='#d4d0c8')
        self.fe=Pmw.EntryField(filebar, label_text="Mu Data File:",labelpos=tkinter.W,validate=None,entry_width=38,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.fe.pack(side=tkinter.LEFT,padx=5,pady=2,fill=tkinter.X)
        b=Button(filebar,text="Open",command=self.load,width=7)
        b.pack(side=tkinter.LEFT,padx=2,pady=2)
        filebar.pack(side=tkinter.LEFT,padx=2,pady=2,fill=tkinter.X)
        f.pack(side=tkinter.TOP,pady=2,fill=tkinter.X)

    def load(self):
        fty=[("mu files","*.mu"),("Xdi data files","*.xdi"),("all files","*")]
        fn=globalfuncs.ask_for_file(fty,self.dir)
        if fn!='':
            globalfuncs.entry_replace(self.fe,fn)

class XanesFitWindowParams:
    def __init__(self, status, XFITOPT, addchannel, filedir):
        self.status = status
        self.XFITOPT = XFITOPT
        self.addchannel = addchannel
        self.filedir = filedir

class XanesFitWindow(MasterClass):
    def _create(self):
        #create window
        self.win=Pmw.Dialog(self.imgwin,title="XANES Fitting",buttons=('OK','Validate','Cancel'),defaultbutton='Cancel',
                                                command=self.fitXANESenter)

        self.win.userdeletefunc(func=self.kill)

        # #JOY ADD VALIDATE AND OK Buttons
        
        # self.win=Pmw.MegaToplevel(self.imgwin)
        # self.win.title("XANES Fitting")
        # self.win.userdeletefunc(func=self.kill)


        intex=self.win.interior()
        intex.configure(background='#d4d0c8')
        #Menu bar
        menubar=PmwTtkMenuBar.PmwTtkMenuBar(intex)
        if os.sys.platform=='win32': menubar.component('hull').configure(bg='#d4d0c8')
        #file menu
        menubar.addmenu('File','')
        menubar.addmenuitem('File','command',label='Load Parameters',command=self.loadXFparams)
        menubar.addmenuitem('File','command',label='Save Parameters',command=self.saveXFparams)
        menubar.addmenuitem('File','separator')   
        menubar.addmenuitem('File','command',label='Get mu Parameters',command=self.getXFparamsFromMu)
        menubar.pack(side=tkinter.TOP,fill=tkinter.X)        

        sf=Pmw.ScrolledFrame(intex,usehullsize=1,hull_width=550,hull_height=330,vertflex='expand',horizflex='expand')
        sf.pack(side=tkinter.TOP,fill='both')
        int=sf.interior()
        int.configure(background='#d4d0c8')
        lf=tkinter.Frame(int,background='#d4d0c8')
        lf.pack(side=tkinter.LEFT,fill='both')
        rf=tkinter.Frame(int,height=330,width=300,background='#d4d0c8')
        rf.pack(side=tkinter.LEFT,fill='both',pady=20,padx=20)
        #data selection
        self.fitXdata=Pmw.ScrolledListBox(lf,labelpos='n',label_text='Select Channels',items=self.mapdata.labels,listbox_selectmode=tkinter.EXTENDED,
                                          listbox_exportselection=tkinter.FALSE,selectioncommand=self.fitXupdate,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.fitXdata.pack(side=tkinter.TOP,padx=4,pady=5,fill='both')
        #standard selection
        self.fitXnumstds=Pmw.OptionMenu(lf,labelpos='n',label_text='Number Standards',items=(1,2,3,4,5,6,7,8,9),
                                       command=self.fitXupdate,hull_background='#d4d0c8',label_background='#d4d0c8')
        self.fitXnumstds.setvalue(2)
        self.fitXnumstds.pack(side=tkinter.TOP,padx=4,pady=5,fill='both')
        #update button
        b=Button(lf,text='Update',command=self.fitXupdate,style='GREEN.TButton',width=15)
        b.pack(side=tkinter.TOP,fill=tkinter.Y,pady=10)
        #array entry
        self.fitXstruct=xanesfitobj(rf)
        self.fitXANESactive=1
        self.win.show()

    def saveXFparams(self):
        #make sure paramters are there
        rt=self.fitXANESvalidate(0)
        if not rt:
            return
        #get fn
        fn=globalfuncs.ask_save_file('',self.ps.filedir.get())
        if fn=='':
            print('Save cancelled')
            return
        (fn,ext)=os.path.splitext(fn)
        if ext=='': fn=fn+'.fpm'
        fid=open(fn,'w')
        #assemble contents
        text='SMAK XFIT\n'
        text=text+str(len(self.fitXstruct.columns[0][1:]))+'\n'
        for n in self.fitXstruct.columns[0][1:]:
            text=text+str(n)+'\n'
        text=text+str(len(self.fitXdata.getvalue()))+'\n'
        for n in self.fitXdata.getvalue():
            text=text+str(n)+'\n'
        text=text+'DATA\n'
        for c in self.fitXstruct.columns[1:]:
            for n in c[1:]:
                text=text+str(n)+'\t'
            text=text+'\n'
        fid.write(text)
        fid.close()
        ##globalfuncs.setstatus(self.ps.status,"Save fit paramters completed")
           
    def getXFparamsFromMu(self):
        
        print(self.fitXnumstds.getvalue())
        #print len(self.fitXstruct.columns[0][1:]),len(self.fitXdata.getvalue())
        #self.fitXnumstds.invoke(index=int(self.fitXnumstds.getvalue()))
        self.fitXupdate()
        #checks --
        valid=1
        #check selection
        if self.fitXdata.getvalue()==():
            globalfuncs.setstatus(self.ps.status,'Choose data selection for XANES fit')
            valid=0
            tkinter.messagebox.showwarning("XANES fit Validation","Choose data selection for XANES fit first")
            return valid
        #check names
        for n in self.fitXstruct.columns[0][1:]:
            if n in self.mapdata.labels: valid=0
            if self.fitXstruct.columns[0][1:].count(n)>1: valid=0
        if not valid:
            globalfuncs.setstatus(self.ps.status,'Invalid names for XANES fit')
            tkinter.messagebox.showwarning("XANES fit Validation","Invalid names for XANES fit")
            return valid

        #start load dialog...
        self.getMuDataDialog=Pmw.Dialog(self.imgwin,title="Use for Data Load",buttons=('OK','Cancel'),defaultbutton='OK',
                                        command=self.getMuDataDone)
        intex=self.getMuDataDialog.interior()
        intex.configure(background='#d4d0c8')
        self.xfmuloaddict={}
        
        l=tkinter.Label(intex,text='Channel Energies',bd=2,relief=tkinter.RAISED,background='#d4d0c8')
        l.pack(side=tkinter.TOP,fill=tkinter.X,expand=1,pady=5)

        self.xfcdmu={}
        for m in self.fitXdata.getvalue():
            ivList=re.findall('\d+',m)
            if len(ivList)>1: iv=str(ivList[0])+"."+str(ivList[1])
            if len(ivList)<1: iv=0
            else: iv=str(ivList[0])
            ef=Pmw.EntryField(intex,label_text =m,labelpos='w',validate='real',value=float(iv),hull_background='#d4d0c8',label_background='#d4d0c8')
            ef.pack(side=tkinter.TOP,padx=5,pady=5)
            self.xfcdmu[m]=ef
        Pmw.alignlabels(list(self.xfcdmu.values()))

        for n in self.fitXstruct.columns[0][1:]:
            obj=xanesMuLoadObject(intex,n,dir=self.ps.filedir.get())
            self.xfmuloaddict[n]=obj
        #Pmw.alignlabels(self.xfmuloaddict.values())
        self.getMuDataDialog.show()

    def getMuDataDone(self,result):
        if result=='Cancel':
            print('Load cancelled')
            self.getMuDataDialog.withdraw()   
            return
        
        #interate on files...
        fin=1
        for fi in self.fitXstruct.columns[0][1:]:
            wid=self.xfmuloaddict[fi]
            if wid.cb.getvalue()=="No": continue
                        
            fifn=wid.fe.getvalue()
            xdat,ydat=self.dataMuRead(fifn)
            
            #iterate on energies
            for kv in self.fitXdata.getvalue():
                fval=float(self.xfcdmu[kv].getvalue())
                ix=globalfuncs.find_nearest(xdat,fval)
                if fval<min(xdat) or fval>max(xdat):
                    print("WARNING: requested value out of range of data file")
                
                self.fitXstruct.dataindex[self.fitXdata.getvalue().index(kv)+1][fin].setvalue(ydat[ix])
            
            fin+=1
        
        self.getMuDataDialog.withdraw()   

    def dataMuRead(self,fifn):
        comchars=['#','!','%','*']
        xdat=[]
        ydat=[]
        #read file
        fid=open(fifn,"rU")
        lines=fid.read().split('\n')
        for line in lines:
            if line !='' and line[0] not in comchars:
                dr=str.replace(line,',',' ')
                parsed=str.split(dr)
                xdat.append(float(parsed[0]))
                ydat.append(float(parsed[1]))
        fid.close()
        #turn into arrays
        xdat=np.array(xdat)
        ydat=np.array(ydat)
        return xdat,ydat
                
    def loadXFparams(self):
        global XHISTORY
        #get fn
        fty=[("FPM param files","*.fpm"),("all files","*")]
        fn=globalfuncs.ask_for_file(fty,self.ps.filedir.get())
        if fn=='':
            print('Load cancelled')
            return 
        #clear all?
        #read first line
        fid=open(fn,'rU')
        l=fid.readline()
        if l!='SMAK XFIT\n':
            print('Invalid parameter file!')
            fid.close()
            return
        #read data
        numstd=int(fid.readline())
        stdname=[]
        for n in range(numstd):
            stdname.append(str.strip(fid.readline()))
        numdat=int(fid.readline())
        datname=[]
        for n in range(numdat):
            datname.append(str.strip(fid.readline()))
        fid.readline() #data start
        mat={}
        for n in datname:
            l=fid.readline().split()
            mat[n]=l
        fid.close()
        #correlate file names with current data labels
        self.xfitloadcorrel(datname)
        #select names and numchans
        self.fitXnumstds.setvalue(numstd)
        sel=[]
        for n in list(self.xfcd.keys()):
            sel.append(self.xfcd[n])
        self.fitXdata.setvalue(sel)
        self.fitXupdate()
        #place 'em
        print(self.fitXstruct.columns)
        newX=[]
        newc=['Names']
        for i in range(numstd):
            newc.append(stdname[i])
        newX.append(newc)
        for i in range(numdat):
            newc=[]
            newc.append(self.xfcd[datname[i]])
            for n in mat[datname[i]]:
                newc.append(n)
            newX.append(newc)
        self.fitXstruct.columns=newX
        self.fitXstruct.makewids()
        self.fitXupdate()

    def xfitloadcorrel(self,datname):
        self.XANESloadCdialog=Pmw.Dialog(self.imgwin,title="Correlate Channels",buttons=('OK','Cancel'),defaultbutton='OK',
                                        command=self.xfitcdone)
        intex=self.XANESloadCdialog.interior()
        self.xfcd={}
        for n in datname:
            cb=Pmw.ComboBox(intex,label_text =n,labelpos='w',history=0,scrolledlist_items=self.mapdata.labels,dropdown=1)
            cb.pack(side=tkinter.TOP,padx=5,pady=5)
            if n in self.mapdata.labels:
                cb.selectitem(n,setentry=1)
            self.xfcd[n]=cb
        Pmw.alignlabels(list(self.xfcd.values()))
        self.XANESloadCdialog.activate()

    def xfitcdone(self,result):
        if result=='Cancel':
            print('Load cancelled')
            self.XANESloadCdialog.deactivate()
        else:
            #check validity
            for n in list(self.xfcd.keys()):
                if self.xfcd[n].get()=='':
                    print('Need all channels corrlated')
                    return
                else:
                    self.xfcd[n]=self.xfcd[n].get()
            self.XANESloadCdialog.deactivate()

    def fitXupdate(self,*args):
        self.fitXstruct.update(self.fitXdata.getvalue(),self.fitXnumstds.getvalue())

    def fitXANESenter(self,result):
        if result=='Cancel':
            globalfuncs.setstatus(self.ps.status,'No action taken')
            self.win.withdraw()
            return
        if result=='Validate':
            rt=self.fitXANESvalidate(1)
            if rt:
                globalfuncs.setstatus(self.ps.status,'XANES fitting matrix valid')
        if result=='OK':
            rt=self.fitXANESvalidate(0)
            if not rt:
                return
            self.win.withdraw()
            globalfuncs.setstatus(self.ps.status,'Performing fitting...')
            #do
            self.dofitXANES()
            globalfuncs.setstatus(self.ps.status,'Fit complete!')

    def fitXANESvalidate(self,display):
        #update...
        self.fitXupdate()
        #check and make sure entries are kosher
        valid=1
        #check selection
        if self.fitXdata.getvalue()==():
            globalfuncs.setstatus(self.ps.status,'Choose data selection for XANES fit')
            valid=0
            if display:
                tkinter.messagebox.showwarning("XANES fit Validation","Choose data selection for XANES fit")
            return valid
        #check names
        for n in self.fitXstruct.columns[0][1:]:
            if n in self.mapdata.labels: valid=0
            if self.fitXstruct.columns[0][1:].count(n)>1: valid=0
        if not valid:
            globalfuncs.setstatus(self.ps.status,'Invalid names for XANES fit')
            if display:
                tkinter.messagebox.showwarning("XANES fit Validation","Invalid names for XANES fit")
            return valid
        #check numbers
        for c in self.fitXstruct.columns[1:]:
            for n in c[1:]:
                try:
                    m=float(n)
                except:
                    valid=0
        if not valid:
            globalfuncs.setstatus(self.ps.status,'Non-numeric entry in standard matrix')
            if display:
                tkinter.messagebox.showwarning("XANES fit Validation","Non-numeric entry in standard matrix")
            return valid            
        return valid

    def dofitXANES(self):
        stdnum=int(self.fitXnumstds.getvalue())
        #make standard matrix and data index
        stdmat=[]
        datind=[]
        bigdat=[]
        for c in self.fitXstruct.columns[1:]:
            newc=[]
            datind.append(self.mapdata.labels.index(c[0])+2)
            bigdat.append(self.mapdata.data.get(self.mapdata.labels.index(c[0])+2))
            for n in c[1:]:
                newc.append(float(n))
            stdmat.append(newc)
        stdmat=np.array(stdmat)
        bigdat=np.array(bigdat)
        #iterate through data
        t=time.process_time()
        (xlen,ylen)=self.mapdata.data.shape[:2]

        resShape=list(self.mapdata.data.shape)
        resShape[2]=stdnum
        result=np.zeros(tuple(resShape),dtype=np.float32)
        error=np.zeros(self.mapdata.data.shape[:2],dtype=np.float32)
        noexit=1
        if False: #self.ps.XFITOPT.get()=='NNLS Fit-A':
            nptsfit=bigdat.shape[1]*bigdat.shape[2]
            bigdat=bigdat.reshape((bigdat.shape[0],nptsfit))
            print(bigdat.shape, stdmat.shape)
            [calc,err]=scipy.optimize.nnls(stdmat,bigdat)
            print(calc.shape)
            print(err.shape)
            print(time.process_time()-t)
            return
        else:
            for i in range(xlen):
                for j in range(ylen):
                    pe=0
                    #get data for this pixel
                    dat=[]
                    td=self.mapdata.data.getPix(i,j)
                    for k in datind:
                        dat.append(td[k])#[i,j,k])
                    dat=np.array(dat)
                    if self.ps.XFITOPT.get()=='LS Fit':
                        [calc,err,y,z]=np.linalg.lstsq(stdmat,dat)
                    if self.ps.XFITOPT.get()=='NNLS Fit-A':

                        [calc,err]=scipy.optimize.nnls(stdmat,dat)
                        err=[err]
                    if self.ps.XFITOPT.get()=='NNLS Fit-B':
                        noexit=1
                        indc=[]
                        tempstd=stdmat.copy()
                        while noexit!=0:
                            [calc,err,y,z]=np.linalg.lstsq(tempstd,dat)
                            #test for negatives
                            for y in indc:
                                calc[y]=0
                            if NNLS.all(calc>=0):
                                #can exit
                                noexit=0
                            else:
                                noexit+=1
                                for k in range(stdnum):
                                    if calc[k]<0:
                                        indc.append(k)
                                        for z in range(len(dat)):
                                            tempstd[z,k]=0
                            if noexit>stdnum+1:
                                sys.stdout.write('^')
                                pe=1
                                #print 'NNLS iterations exceeded...'
                                ##calc=np.zeros(stdnum,Float)
                                err=[0]
                                noexit=0
                    for k in range(stdnum):
                        result[i,j,k]=calc[k]*1.0
                    try:
                        error[i,j]=err[0]
                    except:
                        #print i,j,err
                        if not pe: sys.stdout.write('!')
                        error[i,j]=0
                sys.stdout.write('.')
            sys.stdout.write('\n')    
        #add to data    
        csum=0
        for i in range(stdnum):
            self.ps.addchannel(result[:,:,i],globalfuncs.fixlabelname(self.fitXstruct.columns[0][i+1]))
            csum+=result[:,:,i]
        base='sumFIT'
        i=1
        while 1:
            if base+str(i) in self.mapdata.labels:
                i=i+1
            else:
                base=base+str(i)
                break     
        self.ps.addchannel(csum,base)        
        base='fiterror'
        i=1
        while 1:
            if base+str(i) in self.mapdata.labels:
                i=i+1
            else:
                base=base+str(i)
                break
        self.ps.addchannel(error,base)
        print(time.process_time()-t)        
