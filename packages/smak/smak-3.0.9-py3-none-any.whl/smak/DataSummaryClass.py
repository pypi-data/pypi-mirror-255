import numpy as np
import Pmw 
import tkinter


import globalfuncs
from MasterClass import MasterClass
import MomentMathClass



class DataSummaryParams:
    def __init__(self, maindisp, mask, usemaskinimage, contoursOn, status):
        self.maindisp = maindisp
        self.mask = mask
        self.usemaskinimage = usemaskinimage
        self.contoursOn = contoursOn
        self.status = status

class DataSummary(MasterClass):
    def _create(self):
        self.win=Pmw.TextDialog(self.imgwin,title="Data Channel Summary",defaultbutton=0,scrolledtext_hull_height=400,scrolledtext_hull_width=750,scrolledtext_usehullsize=1)
        self.doDataSummary(self.ps.contoursOn)

    def doDataSummary(self, contoursOn):
        self.ps.contoursOn = contoursOn
        res, contourresults, numpix = self.datacompresssummarymath()

        #clear
        self.win.clear()
        self.win.tag_config("b",font="Courier 9 bold")
        #display SNR yet????
        text='Channel Name'.ljust(20)+'Total Intensity'.ljust(20)+'Mean'.ljust(20)+'Median'.ljust(20)+'StdDev'.ljust(20)+'\n'
        self.win.insert('end',text,"b")
        text=''
        sk=list(res.keys())
        sk.sort()
        for n in sk:
            text=text+n.ljust(20)+str(res[n][0]).ljust(20)+str(res[n][1]).ljust(20)+str(res[n][3]).ljust(20)+str(res[n][2]).ljust(20)+'\n'

        
        i=1

        text=text+'\n'
        for r in contourresults:
            text=text+'C'+str(i)+'\t\t\t'+str(r[0])+'\t\t'
            if len(str(r[0]))<9: text=text+'\t'
            text=text+'NA'+'\t\t\t'
            text=text+str(r[1])+'\t\t'
            if len(str(r[1]))<5:
                text=text+'\t'
            elif len(str(r[1]))<7:
                text=text+'\t\t'
            elif len(str(r[1]))<17:
                text=text+'\t'
            text=text+str(r[2])+'\n'
            i+=1
        text=text+'\n\n'
        text=text+'Data contains '+str(numpix)+' pixels'
        self.win.insert('end',text)
        self.win.show()
        #if self.win.state()=='withdrawn': self.win.show()
        globalfuncs.setstatus(self.ps.status,"Ready")

    def datacompresssummarymath(self):
        res={}
        snr={}
        #worry about mask
        if len(self.ps.mask.mask)!=0 and self.ps.usemaskinimage:
            pm=self.ps.mask.mask[::-1,:]
        else:
            pm=np.ones(self.mapdata.data.get(0)[::-1,:].shape)
        if self.ps.maindisp.zmxyi[0:4]!=[0,0,-1,-1]:
            pm=pm[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
        numpix=sum(sum(pm))
        for n in self.mapdata.labels:
            datind=self.mapdata.labels.index(n)+2
            data=self.mapdata.data.get(datind)[::-1,:]#[::-1,:,datind]
            #worry about zoom
            if self.ps.maindisp.zmxyi[0:4]!=[0,0,-1,-1]:            
                data=data[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
            data=data*np.where(data>0,1,0)
            data=data*pm
            s=sum(sum(data))
            try:
                r=globalfuncs.getSNR(np.ravel(data))
            except:
                r='NA'
            statdata=[]
            rd=np.ravel(data)
            rp=np.ravel(pm)
            if len(self.ps.mask.mask)!=0 and self.ps.usemaskinimage:
                for id in range(len(rd)):
                    if rp[id]: statdata.append(float(rd[id]))
            else:
                statdata=np.ravel(data)
            res[n]=[s,np.mean(np.array(statdata)),np.std(np.array(statdata)),MomentMathClass.median(np.array(statdata))]
            snr[n]=r
        

        #if contours On...
        contourresults=[]
        if self.ps.contoursOn.get()==1:
            #get colormap info
            if self.ps.maindisp.colmap.getvalue()[0].lower() in ['contours6','contours4']:
                #get current data
                datind=self.mapdata.labels.index(self.datachan.getvalue()[0])+2
                data=self.mapdata.data.get(datind)[::-1,:]#[::-1,:,datind]
                #worry about zoom
                if self.ps.maindisp.zmxyi[0:4]!=[0,0,-1,-1]:            
                    data=data[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
                data=data*np.where(data>0,1,0)
                data=data*pm
                data=np.ravel(data)
                #this should be the best current data
                datafrac=data/max(data)
                statdata=[]
                hival=float(self.ps.maindisp.intenvarhi.get())
                loval=float(self.ps.maindisp.intenvarlo.get())
                delta=hival-loval
                if self.ps.maindisp.colmap.getvalue()[0][-1]=='4':
                    ranges=[[0.0,loval+delta/4.],[loval+delta/4.,loval+delta/2.],[loval+delta/2.,loval+3*delta/4.],[loval+3*delta/4.,1.0]]
                else:
                    ranges=[[0.0,loval+delta/6.],[loval+delta/6.,loval+delta/3.],[loval+delta/3.,loval+delta/2.],[loval+delta/2.,loval+delta*2./3.],[loval+delta*2./3.,loval+delta*5./6.],[loval+delta*5./6.,1.0]]
                i=1
                for r in ranges:
                    rdata=[]
                    incontA=np.where(datafrac<=r[1],1,0)
                    if r[0]==0.:
                        incontB=np.where(datafrac>=r[0],1,0)
                    else:
                        incontB=np.where(datafrac>r[0],1,0)
                    incont=incontA*incontB
                    for id in range(len(data)):
                        if incont[id]: rdata.append(float(data[id]))
                    if len(rdata)>1:
                        contourresults.append([sum(rdata),np.mean(np.array(rdata)),np.std(np.array(rdata))])
                    elif len(rdata)==1:
                        contourresults.append([sum(rdata),np.mean(np.array(rdata)),0])
                    else: contourresults.append([0,0,0])
                    print(i,len(rdata))
                    i+=1
        return res, contourresults, numpix
        