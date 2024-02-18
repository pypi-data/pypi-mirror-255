import tkinter
from tkinter.ttk import Button
import math

#third party
import Pmw
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

#local
import globalfuncs
import MyGraph
import MomentMathClass

class RadialProfileParams:
    def __init__(self,maindisp, root, datachan):
        self.maindisp = maindisp
        self.root = root
        self.datachan = datachan

class ElipProfileParams:
    def __init__(self,maindisp, root, datachan, domapimage, status, dataFileBuffer, activeFileBuffer, filedir):
        self.maindisp = maindisp
        self.root = root
        self.datachan = datachan    
        self.domapimage = domapimage
        self.status= status
        self.dataFileBuffer = dataFileBuffer
        self.activeFileBuffer = activeFileBuffer
        self.filedir = filedir
        

class RadialProfile():
    def __init__(self, imgwin, mapdata, ps):
                #get center coordinate... (use dialog)
        self.ps = ps
        self.imgwin = imgwin
        self.mapdata = mapdata
        
        self.radprofDialog=Pmw.Dialog(self.imgwin,title="Radial Profile",buttons=('OK','Cancel'),defaultbutton='OK',
                                     command=self.enterRadDialog)
        h=self.radprofDialog.interior()
        h.configure(background='#d4d0c8')
        #two entries and get pos button
        self.radxcentpos=Pmw.EntryField(h,labelpos='w',label_text='x:',entry_width=7,validate='real',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.radycentpos=Pmw.EntryField(h,labelpos='w',label_text='y:',entry_width=7,validate='real',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.radxcentpos.pack(side=tkinter.LEFT,padx=2,pady=2)
        self.radycentpos.pack(side=tkinter.LEFT,padx=2,pady=2)
        #get position button        
        b=Button(h,text='Get Pos',command=self.getradcentpos,style='ORANGE.TButton',width=7)
        b.pack(side=tkinter.LEFT,padx=2,pady=2)

        self.radprofDialog.show()

        self.radprofDialog.userdeletefunc(func=self.kill)

    def kill(self):
        self.radprofDialog.withdraw()



    def getradcentpos(self):
        self.ps.maindisp.main.show()
        self.ps.maindisp.PMlock.acquire()
        self.ps.maindisp.startPMgetpos()
        self.putradcentpos()

    def putradcentpos(self):
        if self.ps.maindisp.PMlock.locked():
            self.ps.root.after(250,self.putradcentpos)
        else:
            self.radxcentpos.setvalue(self.ps.maindisp.markerexport[0])
            self.radycentpos.setvalue(self.ps.maindisp.markerexport[1])            
        
    def enterRadDialog(self,result):
        #check result
        if result=='Cancel':
            #close too
            self.radprofDialog.destroy()
            return
        #verify
        if not self.radxcentpos.valid() or not self.radycentpos.valid():
            print('need center values')
            return
        #get image data
        if self.ps.datachan.get()==():
            print('select data channel')
            return
        datind=self.mapdata.labels.index(self.ps.datachan.getvalue()[0])+2
        
        #get search indices
        if self.ps.maindisp.zmxyi[0:4]!=[0,0,-1,-1]:            
            dindices=self.ps.maindisp.zmxyi
        else:
            dindices=[0,0,self.mapdata.data.shape[0],self.mapdata.data.shape[1]]

        print(dindices)
        #do calc
        x0=float(self.radxcentpos.getvalue())
        y0=float(self.radycentpos.getvalue())
        #get pixels from data
        x0i=globalfuncs.indexme(self.mapdata.xvals,x0)
        y0i=globalfuncs.indexme(self.mapdata.yvals,y0)
        rad=max(self.mapdata.data.get(0).shape) #NEED TO CALC in pixels
        
        gridX=self.mapdata.data.get(0)[dindices[1]:dindices[3],dindices[0]:dindices[2]]-x0
        gridY=self.mapdata.data.get(1)[dindices[1]:dindices[3],dindices[0]:dindices[2]]-y0
        R=np.sqrt(gridX**2 + gridY**2)
        pz=abs(gridX[0,0]-gridX[0,1])
        print (pz)
        R=np.rint(R/(pz)).astype(int)

        gd=self.mapdata.data.get(datind)[dindices[1]:dindices[3],dindices[0]:dindices[2]]
        nval=np.bincount(R.ravel())
        ints=np.bincount(R.ravel(),weights=gd.ravel())
        ints=ints/nval
        print (ints)
        dist=np.arange(len(ints))*pz
        
        if not self.ps.maindisp.linegraph2present:
            self.ps.maindisp.linegraph2present=1
            self.ps.maindisp.newlineplot2=Pmw.MegaToplevel(self.ps.maindisp.master)
            self.ps.maindisp.newlineplot2.title('Radial Plot View')
            self.ps.maindisp.newlineplot2.userdeletefunc(func=self.ps.maindisp.killlineplot2)           
            h=self.ps.maindisp.newlineplot2.interior()
            self.ps.maindisp.graphx2=MyGraph.MyGraph(h,whsize=(4.5,4),side=tkinter.LEFT,padx=2,graphpos=[[.15,.1],[.9,.9]])

        else:
            #clear old
            self.ps.maindisp.newlineplot2.title('Radial Plot View')
            self.ps.maindisp.graphx2.cleargraphs()
      
        self.ps.maindisp.graphx2.plot(tuple(dist),tuple(ints),text='XV',color='green')        
        self.ps.maindisp.graphx2.draw()
        self.ps.maindisp.newlineplot2.show()
        
        
class ElipProfile():
    def __init__(self, imgwin, mapdata, ps):
                #get center coordinate... (use dialog)
        self.ps = ps
        self.imgwin = imgwin
        self.mapdata = mapdata
        
        #get image data
        if self.ps.datachan.get()==():
            print('select data channel')
            return
        datind=self.mapdata.labels.index(self.ps.datachan.getvalue()[0])+2
        #get search indices
        if self.ps.maindisp.zmxyi[0:4]!=[0,0,-1,-1]:            
            dindices=self.ps.maindisp.zmxyi
        else:
            dindices=[0,0,-1,-1]            #dindices=[0,0,self.mapdata.data.shape[0],self.mapdata.data.shape[1]]  
        ma=self.mapdata.data.get(datind)[dindices[1]:dindices[3],dindices[0]:dindices[2]]
        cm = self.makeContourFromMask(ma)
        elip = MomentMathClass.EllipseClass(cm)
        if elip.elp is None:
            print ('calc error')
            return
        
        angle = elip.angle
      
        
        print (angle,elip.d1,elip.d2,elip.xc,elip.yc)
        
        self.ma = ma
        self.elip=elip
        self.updateElipProf()
        
        #make GUI
        self.elipprofDialog=Pmw.Dialog(self.imgwin,title="Elliptical Profiler",buttons=('Update','Calc','Save','Export','Done'),defaultbutton='Update',
                                     command=self.activityElipDialog)
        h=self.elipprofDialog.interior()
        h.configure(background='#d4d0c8')    
        mf=tkinter.Frame(h,background='#d4d0c8')
        mf.pack(side=tkinter.TOP)        
        
        #center info
        g=Pmw.Group(mf,tag_text='Ellipse Values',tag_background='#d4d0c8',hull_background='#d4d0c8',ring_background='#d4d0c8')
        g.pack(side=tkinter.TOP,padx=15,pady=5,expand='yes',fill='both')
        g.interior().configure(background='#d4d0c8')
        
        mf2=tkinter.Frame(g.interior(),background='#d4d0c8')
        mf2.pack(side=tkinter.TOP,padx=2,pady=2)   
        #two entries and get pos button
        self.elpxcentpos=Pmw.EntryField(mf2,labelpos='w',label_text='x:',entry_width=7,validate='real',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.elpycentpos=Pmw.EntryField(mf2,labelpos='w',label_text='y:',entry_width=7,validate='real',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.elpxcentpos.pack(side=tkinter.LEFT,padx=2,pady=2)
        self.elpycentpos.pack(side=tkinter.LEFT,padx=2,pady=2)
        #get position button        
        b=Button(mf2,text='Get Pos',command=self.getelpcentpos,style='ORANGE.TButton',width=7)
        b.pack(side=tkinter.LEFT,padx=2,pady=2)
        
        #elipse info
        mf3=tkinter.Frame(g.interior(),background='#d4d0c8')
        mf3.pack(side=tkinter.TOP,padx=2,pady=2)   
        #entry
        self.elpangle=Pmw.EntryField(mf3,labelpos='w',label_text='angle:',entry_width=7,validate='real',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.elpangle.pack(side=tkinter.LEFT,padx=2,pady=2)
        self.elpd1=Pmw.EntryField(mf3,labelpos='w',label_text='major:',entry_width=7,validate='real',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.elpd1.pack(side=tkinter.LEFT,padx=2,pady=2)        
        self.elpd2=Pmw.EntryField(mf3,labelpos='w',label_text='minor:',entry_width=7,validate='real',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.elpd2.pack(side=tkinter.LEFT,padx=2,pady=2)
        
        ym=self.ma.shape[1]
        cc = self.convertToCoords([elip.xc,elip.yc],ym)
        self.elpxcentpos.setvalue(cc[0])
        self.elpycentpos.setvalue(cc[1])          
        self.elpangle.setvalue(elip.angle)   
        self.elpd1.setvalue(elip.d1)
        self.elpd2.setvalue(elip.d2)

        #data selection
        self.profdata=Pmw.ScrolledListBox(mf,labelpos='n',label_text='Select Channels',items=self.mapdata.labels,listbox_selectmode=tkinter.EXTENDED,
                                          listbox_exportselection=tkinter.FALSE,selectioncommand=None,label_background='#d4d0c8',hull_background='#d4d0c8')
        self.profdata.pack(side=tkinter.TOP,padx=4,pady=5,fill='both')


        #data params
        g2=Pmw.Group(mf,tag_text='Data Wedge Parameters',tag_background='#d4d0c8',hull_background='#d4d0c8',ring_background='#d4d0c8')
        g2.pack(side=tkinter.TOP,padx=15,pady=5,expand='yes',fill='both')
        g2.interior().configure(background='#d4d0c8')
        
        mf4=tkinter.Frame(g2.interior(),background='#d4d0c8')
        mf4.pack(side=tkinter.TOP,padx=2,pady=2)   
        self.intarcstart=Pmw.EntryField(mf4,labelpos='w',label_text='start angle:',entry_width=7,validate='real',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.intarcstart.pack(side=tkinter.TOP,padx=2,pady=2)
        self.intarcextent=Pmw.EntryField(mf4,labelpos='w',label_text='arc extent:',entry_width=7,validate='real',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.intarcextent.pack(side=tkinter.TOP,padx=2,pady=2)        
        self.intdistance=Pmw.EntryField(mf4,labelpos='w',label_text='dist fact:',entry_width=7,validate='real',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.intdistance.pack(side=tkinter.TOP,padx=2,pady=2)
        self.intstep=Pmw.EntryField(mf4,labelpos='w',label_text='step:',entry_width=7,validate='real',hull_background='#d4d0c8',label_background='#d4d0c8')
        self.intstep.pack(side=tkinter.TOP,padx=2,pady=2)
        self.intwids=[self.intarcstart,self.intarcextent,self.intdistance,self.intstep]
        Pmw.alignlabels(self.intwids)


        
        self.elipprofDialog.show()
        self.elipprofDialog.userdeletefunc(func=self.kill)

    def kill(self):
        self.elipprofDialog.withdraw()        
        
    def activityElipDialog(self,result):
        if result=='Done':
            #close
            self.elipprofDialog.destroy()
            return
        if result=='Update':
            self.updateData()
            self.updateElipProf()
            for w in self.intwids:
                if not w.valid():
                    print ('need ',w.cget('label_text'))
                    return
            self.updateIntSlice()
            return
        if result in ['Save','Export']:
            globalfuncs.setstatus(self.ps.status,"Ready")
                    
            if not self.ps.maindisp.linegraph2present:
                globalfuncs.setstatus(self.ps.status,'No elliptical calculation')           
                return

            ft=self.ps.maindisp.savexyplotelip(labels=self.profdata.getvalue())
            if ft=='':
                return    
            
            if result=='Export':
                #export to clipboard
                self.ps.root.clipboard_clear()
                self.ps.root.clipboard_append(ft)
                globalfuncs.setstatus(self.ps.status,"Elliptical calculation data saved to clipboard")            
                return
            else:
                #save to file
                fn=globalfuncs.trimdirext(self.ps.dataFileBuffer[self.ps.activeFileBuffer]['fname'])+'_elipprof'+'.txt'
                fn=globalfuncs.ask_save_file(fn,self.ps.filedir.get())
                if fn=='':
                    print('Save cancelled')
                    globalfuncs.setstatus(self.ps.status,'Save cancelled')
                    return
                fid=open(fn,'w')
                fid.write(ft)
                fid.close()   
                globalfuncs.setstatus(self.ps.status,'Save complete')
            
        #must be calc...
        self.updateData()
        self.updateElipProf()
        for w in self.intwids:
            if not w.valid():
                print ('need ',w.cget('label_text'))
                return
        self.updateIntSlice()            
        if self.profdata.getvalue()==():
            print ('need data')
            return           

        #get search indices
        if self.ps.maindisp.zmxyi[0:4]!=[0,0,-1,-1]:            
            dindices=self.ps.maindisp.zmxyi
        else:
            dindices=[0,0,-1,-1]            #dindices=[0,0,self.mapdata.data.shape[0],self.mapdata.data.shape[1]]  
            
        xc = float(self.elpxcentpos.getvalue())
        yc = float(self.elpycentpos.getvalue())

        gridX=self.mapdata.data.get(0)[dindices[1]:dindices[3],dindices[0]:dindices[2]]-xc
        gridY=self.mapdata.data.get(1)[dindices[1]:dindices[3],dindices[0]:dindices[2]]-yc
        
        pz=abs(gridX[0,0]-gridX[0,1])
        print (pz)
        
        #make distance arrays
        rx=[0]
        ry=[0]
        for rs in range(int(self.elip.d1/2*float(self.intdistance.getvalue())/float(self.intstep.getvalue()))):
            rx.append((rs+1)*pz*float(self.intstep.getvalue()))
            ry.append((rs+1)*pz/self.elip.d1*self.elip.d2*float(self.intstep.getvalue()))
        
        ang = math.radians(-self.elip.angle)

        #need the angular issue...
        eqang = np.arctan2(-gridY,gridX)
        eqang +=ang
        angstr = min(float(self.intarcstart.getvalue()),float(self.intarcstart.getvalue())+float(self.intarcextent.getvalue()))
        angend = max(float(self.intarcstart.getvalue()),float(self.intarcstart.getvalue())+float(self.intarcextent.getvalue()))        
        
        angstr = math.radians(angstr)
        angend = math.radians(angend)
        print (angstr,angend)
        isal = np.where(eqang>angstr,1,0)
        isau = np.where(eqang<angend,1,0)
        isang = isal*isau

        #plt.imshow(isang)
        #plt.show()

        rmeandict={}
        rstddict={}
        for d in self.profdata.getvalue():
            datinds=self.mapdata.labels.index(d)+2
            rmean=[]
            rstd=[]
        
            #iterate on ellipses...
            for i in range(len(rx)-1):
                eqll = (gridX*np.cos(ang)+gridY*np.sin(ang))**2/(rx[i]**2)+(gridX*np.sin(ang)-gridY*np.cos(ang))**2/(ry[i]**2)
                equl = (gridX*np.cos(ang)+gridY*np.sin(ang))**2/(rx[i+1]**2)+(gridX*np.sin(ang)-gridY*np.cos(ang))**2/(ry[i+1]**2)
            
                isll = np.where(eqll>1,1,0)
                isul = np.where(equl<1,1,0)
                isreg = isll*isul
    
                isreg = isreg*isang
                #print (np.count_nonzero(isreg.ravel()),len(isreg.ravel()))    
                #plt.imshow(isreg)
                #plt.show()
                
            
                #need to loop this on data sets...
                gd=self.mapdata.data.get(datinds)[dindices[1]:dindices[3],dindices[0]:dindices[2]]
                gd=gd[::-1,:]
                #nval=np.count_nonzero(isreg.ravel())
                mean=np.nanmean(np.where(np.isclose(isreg,0),np.nan,isreg*gd))
                std=np.nanstd(np.where(np.isclose(isreg,0),np.nan,isreg*gd))
                rmean.append(mean)
                rstd.append(std)
        
            rmean=np.array(rmean)
            rstd =np.array(rstd)
            
            rmeandict[d]=rmean
            rstddict[d]=rstd
            
        #whew...
        if not self.ps.maindisp.linegraph2present:
            self.ps.maindisp.linegraph2present=1
            self.ps.maindisp.newlineplot2=Pmw.MegaToplevel(self.ps.maindisp.master)
            self.ps.maindisp.newlineplot2.title('Elliptical Plot View')
            self.ps.maindisp.newlineplot2.userdeletefunc(func=self.ps.maindisp.killlineplot2)           
            h=self.ps.maindisp.newlineplot2.interior()
            self.ps.maindisp.graphx2=MyGraph.MyGraph(h,whsize=(4.5,4),side=tkinter.LEFT,padx=2,graphpos=[[.15,.1],[.9,.9]])

        else:
            #clear old
            self.ps.maindisp.newlineplot2.title('Elliptical Plot View')
            self.ps.maindisp.graphx2.cleargraphs()
      
        for d in self.profdata.getvalue():
            self.ps.maindisp.graphx2.plot(tuple(rx[:-1]),tuple(rmeandict[d]),text=d+'XV',color='green')        
            self.ps.maindisp.graphx2.plot(tuple(rx[:-1]),tuple(rmeandict[d]+0.5*rstddict[d]),text=d+'XVp',color='red')  
            self.ps.maindisp.graphx2.plot(tuple(rx[:-1]),tuple(rmeandict[d]-0.5*rstddict[d]),text=d+'XVm',color='red')  
            
        
        self.ps.maindisp.graphx2.draw()
        self.ps.maindisp.newlineplot2.show()        
        
        
    def updateData(self):
        #redraw first:
        self.ps.domapimage()
        ym=self.ma.shape[1]
        xc = float(self.elpxcentpos.getvalue())
        yc = float(self.elpycentpos.getvalue())
        xp,yp = self.ps.maindisp.datainvcoords(xc,yc,index=False)
        z,xi,yi = self.ps.maindisp.datalookup(xp,yp,offs=False)
        self.elip.xc=xi
        self.elip.yc=ym-yi
        self.elip.angle = float(self.elpangle.getvalue())
        self.elip.d1 = float(self.elpd1.getvalue())
        self.elip.d2 = float(self.elpd2.getvalue())
        
    def updateElipProf(self):
        #draw
        ym=self.ma.shape[1]
        ocs=[self.elip.xc-1,self.elip.yc-1,self.elip.xc+1,self.elip.yc+1]
        self.ps.maindisp.imframe.create_oval(self.convertToImage(ocs,ym),width=1,outline='black',fill='white')
        self.ps.maindisp.imframe.create_line(self.convertToImage(self.elip.calcMajorLine(),ym),fill='white')
        self.ps.maindisp.imframe.create_line(self.convertToImage(self.elip.calcMinorLine(),ym),fill='white')        
        
    def updateIntSlice(self):
        
        ym=self.ma.shape[1]
        rfe=float(self.intdistance.getvalue())
        rfar=[0.25*rfe,0.50*rfe,0.75*rfe,rfe]
        for rf in rfar:
            ocs=self.elip.calcElipArc(self.intarcstart.getvalue(),self.intarcextent.getvalue(),rf=rf)
            self.ps.maindisp.imframe.create_line(self.convertToImage(ocs,ym),width=2,fill='white')
        
        
    def makeContourFromMask(self,mask):
        mask=mask.astype(np.uint8)
        contours = cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)[0]
        mc = max(contours, key=cv.contourArea)
        return mc        
    
    def convertToImage(self,tup,ym):
        #print (tup)
        new=[]
        ti=0
        for tvs in tup:
            #print (ti,tvs)
            if ti%2==1: 
                ti+=1
                continue
            x,y = self.ps.maindisp.datainvcoords(tup[ti],ym-tup[ti+1],index=True)
            new.append(x)
            new.append(y)
            ti+=1
        #print (tuple(new))
        return tuple(new)
    
    def convertToCoords(self,tup,ym):
        new=[]
        ti=0
        for tvs in tup:
            #print (ti,tvs)
            if ti%2==1: 
                ti+=1
                continue
            xi,yi = self.ps.maindisp.datainvcoords(tup[ti],ym-tup[ti+1],index=True)
            z,x,y = self.ps.maindisp.datalookup(xi,yi)
            new.append(self.ps.maindisp.xsc[x])
            new.append(self.ps.maindisp.ysc[y])
            ti+=1
        #print (tuple(new))
        return tuple(new)       
        
    def getelpcentpos(self):
        self.ps.maindisp.main.show()
        self.ps.maindisp.PMlock.acquire()
        self.ps.maindisp.startPMgetpos()
        self.putelpcentpos()

    def putelpcentpos(self):
        if self.ps.maindisp.PMlock.locked():
            self.ps.root.after(250,self.putelpcentpos)
        else:
            self.elpxcentpos.setvalue(self.ps.maindisp.markerexport[0])
            self.elpycentpos.setvalue(self.ps.maindisp.markerexport[1])    
            
            
            
            
            