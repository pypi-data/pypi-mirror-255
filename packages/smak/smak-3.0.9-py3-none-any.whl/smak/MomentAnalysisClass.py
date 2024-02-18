import tkinter

import numpy as np
import Pmw 

import globalfuncs
from MasterClass import MasterClass
import MomentMathClass
import PmwTtkButtonBox


class MomentAnalysisParams:
    def __init__(self, status, datachan, dodt, mask, maindisp, plotmarkermain, PMupdate, addmarker):
        self.status = status
        self.datachan=datachan
        self.dodt=dodt
        self.mask = mask 
        self.maindisp= maindisp
        self.plotmarkermain = plotmarkermain
        self.PMupdate = PMupdate
        self.addmarker = addmarker



class MomentAnalysisWindow(MasterClass):
    #def __init__(self, imgwin, mapdata, status, datachan, dodt, mask, maindisp, plotmarkermain, PMupdate, addmarker):
    def _create(self):

         #create window
        self.win=Pmw.MegaToplevel(self.imgwin)
        self.win.title('Data Moments Window')        
        self.win.userdeletefunc(func=self.kill)
        int=self.win.interior()
        int.configure(background='#d4d0c8')
        mf=tkinter.Frame(int,background='#d4d0c8')
        mf.pack(side=tkinter.TOP)
        lf=tkinter.Frame(mf,background='#d4d0c8')
        lf.pack(side=tkinter.LEFT,fill='both',padx=20,pady=20)
        rf=tkinter.Frame(mf,height=300,width=300,background='#d4d0c8')
        rf.pack(side=tkinter.LEFT,fill='both',pady=20,padx=20)
        #data selection
        self.fitMdata=Pmw.ScrolledListBox(lf,labelpos='n',label_text='Select Channels',items=self.mapdata.labels,listbox_selectmode=tkinter.EXTENDED,
                                          listbox_exportselection=tkinter.FALSE,selectioncommand=self.domoments,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.fitMdata.pack(side=tkinter.TOP,padx=5,pady=5,fill='both')        

        g=Pmw.Group(rf,tag_text='Moment Results',tag_background='#d4d0c8',ring_background='#d4d0c8',hull_background='#d4d0c8')
        g.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')
        g.interior().configure(background='#d4d0c8')
        self.momtypes=['Area','Average','Median','Mode','Min','Max','StdDev','xCent','yCent','xxVar','yyVar','xyVar','xSkew','ySkew','xKurt','yKurt']
        self.momentwids={}
        for t in self.momtypes:
            wid=Pmw.EntryField(g.interior(),labelpos='w',label_text=t+':',entry_width=15,value='-',label_background='#d4d0c8',hull_background='#d4d0c8')
            self.momentwids[t]=wid
            wid.pack(side=tkinter.TOP,padx=3,pady=3,anchor=tkinter.W)
        #align and disable
        Pmw.alignlabels(list(self.momentwids.values()))
        for l in list(self.momentwids.values()):
            l.component('entry').configure(state=tkinter.DISABLED)

        b=PmwTtkButtonBox.PmwTtkButtonBox(int,orient='horizontal',hull_background='#d4d0c8')
        b.add('Add Marker',command=self.doPMupdate,style='SBLUE.TButton',width=15)
        b.pack(side=tkinter.TOP,padx=5,pady=10)



    def doPMupdate(self):
        if self.momentwids["xCent"].getvalue()=='-' or self.momentwids["yCent"].getvalue()=='-':
            return
        self.ps.plotmarkermain()
        new=self.ps.addmarker()
        new.xpos.setvalue(self.momentwids["xCent"].getvalue())
        new.ypos.setvalue(self.momentwids["yCent"].getvalue())
        new.marker.selectitem('sm circle')    
        self.ps.PMupdate(new)        

    def domoments(self,datind=None):
        globalfuncs.setstatus(self.ps.status,"Calculating...")
        if datind is None:
            datind=self.mapdata.labels.index(self.fitMdata.getvalue()[0])+2
        xv=np.ravel(self.mapdata.data.get(datind))#[:,:,datind])
        #deadtimes
        nodtx=0
        if self.ps.datachan.getvalue()[0] in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodtx=1
        if self.ps.dodt.get()==1 and not nodtx:
            #DT: corFF=FF*exp(tau*1e-6*ICR)
            icr=np.ravel(self.mapdata.data.get(self.DTICRchanval))   #icr=np.ravel(tdata[:,:,self.DTICRchanval])
            dtcor=np.exp(float(self.deadtimevalue.getvalue())*1e-6*icr)
            xv=xv*dtcor
        pic=np.reshape(xv,np.shape(self.mapdata.data.get(0)))#[:,:,0]))
        #mask
        if len(self.ps.mask.mask)!=0 and self.usemaskinimage:
            pm=self.ps.mask.mask#[::-1,:]
        else:
            pm=None
        #zooms
        if self.ps.maindisp.zmxyi[2]!=-1 and self.ps.maindisp.zmxyi[3]!=-1:     
            pic=pic[::-1,:]
            xc=self.mapdata.data.get(0)[::-1,:]#[::-1,:,1]
            yc=self.mapdata.data.get(1)[::-1,:]#[::-1,:,0]
            pic=pic[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
            xc=xc[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
            yc=yc[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
            pic=pic[::-1,:]
            xc=xc[::-1,:]
            yc=yc[::-1,:]
        else:
            xc=self.mapdata.data.get(0)#[:,:,1]
            yc=self.mapdata.data.get(1)#[:,:,0]

        d=MomentMathClass.MomentClass(xc,yc,pic,mask=pm)
        for i in list(d.moms.keys()):
            print(i,d.moms[i])

        #place in results  ['Area','Average','Median','Mode','Min','Max','StdDev','xCent','yCent','xxVar','yyVar','xyVar','xSkew','ySkew','xKurt','yKurt']
        self.momentwids["Area"].setvalue(d.A)
        self.momentwids["Average"].setvalue(d.avg)
        self.momentwids["Median"].setvalue(d.median)
        self.momentwids["Mode"].setvalue(str(d.mode[0][0])+"x"+str(d.mode[1][0]))
        self.momentwids["Min"].setvalue(d.min)
        self.momentwids["Max"].setvalue(d.max)
        self.momentwids["StdDev"].setvalue(d.stddev)
        self.momentwids["xCent"].setvalue(d.medx)
        self.momentwids["yCent"].setvalue(d.medy)
        self.momentwids["xxVar"].setvalue(d.xxvar)
        self.momentwids["yyVar"].setvalue(d.yyvar)
        self.momentwids["xyVar"].setvalue(d.xyvar)
        self.momentwids["xSkew"].setvalue(d.xskew)
        self.momentwids["ySkew"].setvalue(d.yskew)
        self.momentwids["xKurt"].setvalue(d.xkurt)
        self.momentwids["yKurt"].setvalue(d.ykurt)
        
        
        globalfuncs.setstatus(self.ps.status,"Ready")     

