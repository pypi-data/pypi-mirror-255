import os
import tkinter

#third party
import numpy as np
import Pmw 

#local
import globalfuncs
import MyGraph
import PmwTtkButtonBox
import PmwTtkMenuBar



def dataAveragingMath(data, axis, zoom = None, mask = None):
    if mask is not None and len(mask.mask)!=0:
        pm=mask.mask[::-1,:]
        pm=np.where(pm>0,1,0)
    else:
        pm=np.ones(data[::-1,:].shape)
    data=data*pm

    if zoom is not None:
        if zoom[0:4]!=[0,0,-1,-1]:
            temppm=np.zeros(pm.shape)
            tempdata=np.zeros(data.shape)
            temppm[zoom[1]:zoom[3],zoom[0]:zoom[2]]=pm[zoom[1]:zoom[3],zoom[0]:zoom[2]]
            tempdata[zoom[1]:zoom[3],zoom[0]:zoom[2]]=data[zoom[1]:zoom[3],zoom[0]:zoom[2]]
            pm=temppm
            data=tempdata
    print(data.shape)
    if axis=='Y':
        pix=np.sum(pm,axis=0)
        tdat=np.sum(data,axis=0)#/data.shape[0]
        adat=np.where(pix==0,0,tdat/pix)
        #xv=self.mapdata.xvals
    else:
        pix=np.sum(pm,axis=1)
        tdat=np.sum(data,axis=1)#/data.shape[1]
        adat=np.where(pix==0,0,tdat/pix)
        #xv=self.mapdata.yvals[::-1]
    return adat

class DataAveragingParams:
    def __init__(self, status, datachan, mask, maindisp, usemaskinimage):
        self.status = status
        self.datachan = datachan
        self.mask = mask
        self.maindisp = maindisp
        self.usemaskinimage = usemaskinimage

class DataAveraging:
    def __init__(self, imgwin, mapdata, ps):
        self.imgwin = imgwin
        self.mapdata = mapdata
        self.ps = ps
        self.exist = 0
        self.dialog=Pmw.SelectionDialog(self.imgwin,title='Data Averaging',buttons=('OK', 'Cancel'),defaultbutton='OK',
        scrolledlist_labelpos='n',label_text='Choose axis to average over:',
        scrolledlist_items=('X', 'Y'),command=self.dodatacompress)

    def dodatacompress(self,result):
        print("in do data compress")
        self.dialog.withdraw()
        if result=='Cancel':
            print('Data averaging cancelled')
            globalfuncs.setstatus(self.ps.status,'Data averaging cancelled')
            return
        globalfuncs.setstatus(self.ps.status,"AVERAGING...")
        axis=self.dialog.getcurselection()[0]
        #get current channel
        datind=self.mapdata.labels.index(self.ps.datachan.getvalue()[0])+2
        data=self.mapdata.data.get(datind)[::-1,:]#[::-1,:,datind]
        #worry about mask

        if len(self.ps.mask.mask)!=0 and self.ps.usemaskinimage:
            mask = self.ps.mask
        else: 
            mask = None

        #     pm=self.ps.mask.mask[::-1,:]
        #     pm=np.where(pm>0,1,0)
        # else:
        #     pm=np.ones(self.mapdata.data.get(0)[::-1,:].shape)
        # data=data*pm
        #worry about zoom
        if self.ps.maindisp.zmxyi[0:4]!=[0,0,-1,-1]:
            zoom = self.ps.maindisp.zmxyi
        else:
            zoom = None
        #     temppm=np.zeros(pm.shape)
        #     tempdata=np.zeros(data.shape)
        #     temppm[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]=pm[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
        #     tempdata[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]=data[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
        #     pm=temppm
        #     data=tempdata
        #average data
        # print(data.shape)
        if axis=='Y':
        #     pix=np.sum(pm,axis=0)
        #     tdat=np.sum(data,axis=0)#/data.shape[0]
        #     adat=np.where(pix==0,0,tdat/pix)
            xv=self.mapdata.xvals
        else:
        #     pix=np.sum(pm,axis=1)
        #     tdat=np.sum(data,axis=1)#/data.shape[1]
        #     adat=np.where(pix==0,0,tdat/pix)
            xv=self.mapdata.yvals[::-1]
        #define new window if needed
        adat = dataAveragingMath(data, axis, zoom = zoom, mask = mask)
        if not self.exist:
            self.exist=1
            self.datacompresswin=Pmw.MegaToplevel(self.imgwin)
            self.datacompresswin.title('Averaged Data View')
            self.datacompresswin.userdeletefunc(func=self.kill)           
            h=self.datacompresswin.interior()
            #menubar for data export:
            menubar=PmwTtkMenuBar.PmwTtkMenuBar(h)
            if os.sys.platform=='win32': menubar.component('hull').configure(bg='#d4d0c8')
            menubar.addmenu('Export','')
            menubar.addmenuitem('Export','command',label='Export data to clipboard',command=self.exportdatacompress)
            menubar.pack(side=tkinter.TOP,fill=tkinter.X)            
            self.dagraph=MyGraph.MyGraph(h,whsize=(6,4),side=tkinter.LEFT,padx=2)

        else:
            #clear old
            self.dagraph.cleargraphs()

        self.dagraph.plot(tuple(xv),tuple(adat),text='data',color='green')        
         
        globalfuncs.setstatus(self.ps.status,"Averaging complete.")
        self.dagraph.draw()
        self.datacompresswin.show()


    def kill(self):
        self.exist=0
        self.datacompresswin.destroy()

    def exportdatacompress(self):
        globalfuncs.setstatus(self.ps.status,"Ready")
        if not self.hasdata:
            print('No Data')
            globalfuncs.setstatus(self.ps.status,'No Data')
            return
        #test for data to exist:
        if not self.exist:
            print('No averaged plot')
            globalfuncs.setstatus(self.ps.status,'No averaged plot')
            return
        globalfuncs.setstatus(self.ps.status,"Saving averaged data to clipboard...")
        #get data for clipboard save
        self.clipboardexport(self.dagraph,'Averaged Data')

    

 