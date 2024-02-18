import tkinter

import numpy as np
import Pmw 
from scipy.optimize import minimize

import globalfuncs
import histclass
from MasterClass import MasterClass
import MyGraph
import PmwTtkButtonBox


class MakeHistogramWindowParams():
    def __init__(self, DTICRchanval, maindisp, dodt, activeFileBuffer, dataFileBuffer, filenb, root, status):
        self.DTICRchanval = DTICRchanval
        self.maindisp = maindisp
        self.dodt= dodt
        self.activeFileBuffer = activeFileBuffer
        self.dataFileBuffer = dataFileBuffer
        self.filenb = filenb
        self.root = root
        self.status = status


class MakeHistogramWindow(MasterClass):
    def _create(self):

        self.hdata=None
        #create window
        self.win=Pmw.MegaToplevel(self.imgwin)
        self.win.title('Data Histogram Window')
        self.win.userdeletefunc(func=self.kill)
        intr=self.win.interior()
        intr.configure(background='#d4d0c8')
        mf=tkinter.Frame(intr,background='#d4d0c8')
        mf.pack(side=tkinter.TOP)
        lf=tkinter.Frame(mf,background='#d4d0c8')
        lf.pack(side=tkinter.LEFT,fill='both',padx=20,pady=20)
        rf=tkinter.Frame(mf,height=300,width=300,background='#d4d0c8')
        rf.pack(side=tkinter.LEFT,fill='both',pady=20,padx=20)
        #data selection
        self.fitHdata=Pmw.ScrolledListBox(lf,labelpos='n',label_text='Select Channels',items=self.mapdata.labels,listbox_selectmode=tkinter.EXTENDED,
                                          listbox_exportselection=tkinter.FALSE,selectioncommand=self.makeHupdate,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.fitHdata.pack(side=tkinter.TOP,padx=4,pady=5,fill='both')
        #histogram type
        self.histDataType=Pmw.RadioSelect(lf,buttontype='radiobutton',orient='vertical',command=self.makeHupdate,hull_background='#d4d0c8')
        for text in ('Active File','All Files','Compare Files'):
            self.histDataType.add(text,background='#d4d0c8')
        self.histDataType.setvalue('Active File')
        self.histDataType.pack(side=tkinter.TOP,padx=3,pady=10)
        #plot and def's entry
        self.histgraph=MyGraph.MyGraph(rf,whsize=(4.5,4),padx=5,pady=5,graphpos=[[.15,.1],[.9,.9]])
        #self.histgraph.legend_configure(hide=1)
        #self.histgraph.pack(side=tkinter.TOP,expand=1,fill='both',padx=5,pady=5)
        hof=tkinter.Frame(intr,background='#d4d0c8')
        hof.pack(side=tkinter.TOP)
        g=Pmw.Group(hof,tag_text='Histogram Options',tag_background='#d4d0c8',ring_background='#d4d0c8',hull_background='#d4d0c8')
        g.pack(side=tkinter.LEFT,padx=15,pady=5,expand='yes',fill='both')
        g.interior().configure(background='#d4d0c8')
        self.histbins=Pmw.EntryField(g.interior(),labelpos='w',label_text='No. of Bins: ',validate='integer',entry_width=10,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.histbins.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)
        self.histbins.setvalue(25)
        self.histmin=Pmw.EntryField(g.interior(),labelpos='w',label_text='Min Value: ',validate='real',entry_width=10,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.histmin.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)        
        self.histmin.setvalue(0)
        self.histmax=Pmw.EntryField(g.interior(),labelpos='w',label_text='Max Value: ',validate='real',entry_width=10,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.histmax.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)
        self.histmax.setvalue(1)
        Pmw.alignlabels([self.histbins,self.histmin,self.histmax])
        
        g=Pmw.Group(hof,tag_text='Fit Options',tag_background='#d4d0c8',ring_background='#d4d0c8',hull_background='#d4d0c8')
        g.pack(side=tkinter.LEFT,padx=15,pady=5,expand='yes',fill='both')
        g.interior().configure(background='#d4d0c8')
        ff=tkinter.Frame(g.interior(),background='#d4d0c8')
        ff.pack(side=tkinter.LEFT)
        ff2=tkinter.Frame(g.interior(),background='#d4d0c8')
        ff2.pack(side=tkinter.LEFT)
        self.histfitnumdists=Pmw.EntryField(ff,labelpos='w',label_text='No. of Distributions: ',validate='integer',entry_width=10,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.histfitnumdists.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)
        self.histfitnumdists.setvalue(2)
        self.histfitfwhm=Pmw.EntryField(ff,labelpos='w',label_text='Dist. FWHM: ',validate='real',entry_width=10,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.histfitfwhm.pack(side=tkinter.TOP,padx=2,pady=2,anchor=tkinter.W)        
        self.histfitfwhm.setvalue(.25)

        Pmw.alignlabels([self.histfitnumdists,self.histfitfwhm])        
        
        b=PmwTtkButtonBox.PmwTtkButtonBox(ff2,orient='vertical',hull_background='#d4d0c8')
        b.add('Fit',command=self.doHistGaussFit,style='ORANGE.TButton',width=15)
        b.pack(side=tkinter.LEFT,padx=5,pady=10)
        
        self.histfitresult=Pmw.ScrolledText(ff2,hull_background='#d4d0c8',hull_width=400,hull_height=100,usehullsize=1)
        self.histfitresult.pack(side=tkinter.LEFT,padx=15,pady=5,fill='both')
        
        b=PmwTtkButtonBox.PmwTtkButtonBox(intr,orient='horizontal',hull_background='#d4d0c8')
        b.add('Update',command=self.doHupdate,style='SBLUE.TButton',width=15)
        b.add('Export',command=self.doHexport,style='GREEN.TButton',width=15)
        b.pack(side=tkinter.TOP,padx=5,pady=10)
        self.histmultiflag=False

    # def kill(self):
    #     self.win.destroy()
    #     self.histogramexist=0

    def makeHupdate(self,*args):
        if self.fitHdata.getvalue() is None:
            print('select channel for histogram')
            return
        self.hdataname=[]
        #get data, applying zoom, masks, etc
        if self.histDataType.getvalue()=='Active File':
            xind=self.mapdata.labels.index(self.fitHdata.getvalue()[0])+2
            xdata=self.mapdata.data.get(xind)
            icrdata=self.mapdata.data.get(self.ps.DTICRchanval)
            if self.ps.maindisp.zmxyi[2]!=-1 and self.ps.maindisp.zmxyi[3]!=-1:
                xdata=xdata[::-1,:]
                icrdata=icrdata[::-1,:]
                xdata=xdata[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
                icrdata=icrdata[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
                xdata=xdata[::-1,:]
                icrdata=icrdata[::-1,:]
            xv=np.ravel(xdata)
            nodtx=0
            if self.fitHdata.getvalue()[0] in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodtx=1
            if self.ps.dodt.get()==1 and not nodtx:
                #DT: corFF=FF*exp(tau*1e-6*ICR)
                icr=np.ravel(icrdata)
                dtcor=np.exp(float(self.deadtimevalue.getvalue())*1e-6*icr)
                xv=xv*dtcor
            self.hdata=xv
            self.hdataname=[self.ps.activeFileBuffer]
            #find max, sub in to entry
            self.histmax.setvalue(np.maximum.reduce(self.hdata))
            self.histmultiflag=False
            self.doHupdate()
        else:
            self.hdata=[]
            for nbuf in list(self.ps.dataFileBuffer.keys()):
                buf=self.ps.dataFileBuffer[nbuf]
                self.hdataname.append(nbuf)
                if nbuf==self.ps.filenb.getcurselection():
                    buf['zoom']=self.ps.maindisp.zmxyi
                if self.fitHdata.getvalue()[0] not in buf['data'].labels:
                    continue
                xind=buf['data'].labels.index(self.fitHdata.getvalue()[0])+2
                xdata=buf['data'].data.get(xind)
                icrdata=buf['data'].data.get(self.ps.DTICRchanval)
                if buf['zoom'][2]!=-1 and buf['zoom'][3]!=-1:
                    xdata=xdata[::-1,:]
                    icrdata=icrdata[::-1,:]
                    xdata=xdata[buf['zoom'][1]:buf['zoom'][3],buf['zoom'][0]:buf['zoom'][2]]
                    icrdata=icrdata[buf['zoom'][1]:buf['zoom'][3],buf['zoom'][0]:buf['zoom'][2]]
                    xdata=xdata[::-1,:]
                    icrdata=icrdata[::-1,:]
                xv=np.ravel(xdata)
                nodtx=0
                if self.fitHdata.getvalue()[0] in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodtx=1
                if self.ps.dodt.get()==1 and not nodtx:
                    #DT: corFF=FF*exp(tau*1e-6*ICR)
                    icr=np.ravel(icrdata)
                    dtcor=np.exp(float(self.deadtimevalue.getvalue())*1e-6*icr)
                    xv=xv*dtcor
                if self.histDataType.getvalue()=='All Files':
                    self.hdata.extend(xv)
                    self.hdataname=['AllData']
                if self.histDataType.getvalue()=='Compare Files':
                    self.hdata.append(np.array(xv))

            # find max, sub in to entry
            if self.histDataType.getvalue()=='All Files':
                self.hdata=np.array(self.hdata)
                self.histmax.setvalue(np.maximum.reduce(self.hdata))
                self.histmultiflag=False
                self.doHupdate()
            else:
                maxval=0
                for s in self.hdata:
                    maxval=max(maxval,np.maximum.reduce(s))
                self.histmax.setvalue(maxval)
                self.histmultiflag=True
                self.doHupdate()

    def doHupdate(self,passback=0):
        if self.hdata is None: return
        #send to histogram maker
        nb=int(self.histbins.getvalue())
        if nb<1: nb=1
        if passback:
            hc=[]
            if self.histmultiflag:
                for dv in self.hdata:
                    hc.append(histclass.Histogram(dv,bins=nb,nmin=self.histmin.getvalue(),nmax=self.histmax.getvalue()))
            else:
                hc.append(histclass.Histogram(self.hdata,bins=nb,nmin=self.histmin.getvalue(),nmax=self.histmax.getvalue()))
            return hc
        if not self.histmultiflag:
            curhdata=[self.hdata]
        else:
            curhdata=self.hdata
        #remove old
        self.histgraph.cleargraphs()
        c=[ '#488f31', '#de425b', '#ffff9d', '#51a676', '#ea714e', '#88c580', '#f7a258', '#c2e38c', '#fdd172' ]
        i=0
        for dv in curhdata:
            hplotdata=histclass.Histogram(dv,bins=nb,nmin=self.histmin.getvalue(),nmax=self.histmax.getvalue())
            #if multi comparison, normalize?
            if self.histmultiflag:
                hplotdata.normalize()
            #plot data
            #self.histgraph.bar_create('H',xdata=tuple(hplotdata[:,0]),ydata=tuple(hplotdata[:,1]),background='green',foreground='green')
            ac=c[i%9]
            self.histgraph.bar(tuple(hplotdata[:,0]),tuple(hplotdata[:,1]),text='H',color=ac,edge=ac)
            i+=1
        self.histgraph.draw()

    def doHexport(self):
        data=self.doHupdate(passback=1)
        nhistos=len(data)
        #print nhistos, self.hdataname
        text='Bin\t'
        for i in range(nhistos):
            text+='Frequency_'+self.hdataname[i]+'\t'
        text+='\n'
        for i in range(len(data[0][:,0])):
            text +=str(data[0][i, 0])+'\t'
            for j in range(nhistos):
                text+=str(data[j][i,1])+'\t'
            text+='\n'
        #export to clipboard
        self.ps.root.clipboard_clear()
        self.ps.root.clipboard_append(text)
        globalfuncs.setstatus(self.ps.status,"Histogram data saved to clipboard")


    def doHistGaussFit(self):
        
        rt=self.doHupdate(passback=1)
        data=rt[0].hist
        maxN=int(self.histfitnumdists.getvalue())
        fwhm=float(self.histfitfwhm.getvalue())
        fitobj=MultiGaussObj(data[:,0],data[:,1],maxN,fwhm)
        result=minimize(fitobj.eqn,fitobj.initguess,method='Nelder-Mead')
        fp=result.x
        print(result.message)
        print(fp)
        fitobj.calc(fp)
        #plot it
        self.doHupdate()
        if fp is None: return
        rtext='Fit Result to '+str(maxN)+' distributions: \n'
        for i in range(maxN):
            self.histgraph.plot(tuple(data[:,0]),tuple(fitobj.yfit[i]),text='CV'+str(i),color='red') 
            rtext=rtext+"G"+str(i+1)+"=> amp: "+str(fp[i*3+0])+"\tcenter: "+str(fp[i*3+1])+"\tFWHM: "+str(abs(fp[i*3+2]))+"\n"
        self.histgraph.plot(tuple(data[:,0]),tuple(fitobj.yfit[i+1]),text='CV'+str(i),color='yellow')  
        self.histgraph.draw()
        self.histfitresult.setvalue(rtext)

class MultiGaussObj:
    def __init__(self,xd,yd,maxN,fwhm):
        self.xd=xd
        self.yd=yd
        self.maxN=maxN
        self.yfit=[]
        self.xpvs=[]
        self.initguess=np.ones(maxN*3)
        
        for i in range(maxN):
            ev=tkinter.simpledialog.askfloat(title='MultiGauss',prompt='Enter starting position for gauss '+str(i+1),initialvalue=0)
            if ev!='' or ev is not None:
                self.initguess[i*3+1]=ev
            self.initguess[i*3+2]=fwhm
            self.initguess[i*3+0]=1000
            
        self.initguess=tuple(self.initguess)

    def eqn(self,pars):
        yf=np.zeros(self.yd.shape)
        for j in range(self.maxN):
            yf=yf+globalfuncs.gausseqn((pars[j*3+0],pars[j*3+1],abs(pars[j*3+2]),0),self.xd)
#            yf.append(np.where(self.yd>0,(self.yd-self.xd*j)**2,0))
#            yf.append(np.where(self.yd>0,(self.yd-self.xd*j)**2/(self.yd**2),0))
        mv=(self.yd-yf)**2   
        return sum(mv)
        
    def calc(self,pars):

        yf=np.zeros(self.yd.shape)
        for j in range(self.maxN):
            nf=globalfuncs.gausseqn((pars[j*3+0],pars[j*3+1],abs(pars[j*3+2]),0),self.xd)
            self.yfit.append(nf)
            yf=yf+nf
        self.yfit.append(yf)
