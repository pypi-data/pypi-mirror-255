# -*- coding: utf-8 -*-
"""
Created on Fri May  5 11:22:12 2023

@author: stewards
"""

import tkinter

import Display
import numpy as np
from PIL import Image
from PIL import ImageTk
from PIL import ImageChops
import Pmw


import globalfuncs
import ImCmap
import PmwTtkButtonBox




#######################################
## Stich Group Class
#######################################        
        
class stitchChannelGroup:
    def __init__(self,master,labels,index,shift=True,slide=None,extend=False):
        
        self.index=index
        g1=Pmw.Group(master,tag_text='Channel '+str(index),tag_background='#d4d0c8',ring_background='#d4d0c8',hull_background='#d4d0c8')
        g1.interior().configure(background='#d4d0c8')
        if extend:
            mode=tkinter.EXTENDED
        else:
            mode=tkinter.SINGLE
        self.stitchch=Pmw.ScrolledListBox(g1.interior(),labelpos='n',label_text='Select Channel',items=labels,listbox_selectmode=mode,
                                              listbox_exportselection=tkinter.FALSE,selectioncommand=tkinter.DISABLED,listbox_height=5,
                                           hull_background='#d4d0c8',label_background='#d4d0c8')
        self.stitchch.pack(side=tkinter.LEFT,padx=4,pady=5,fill='both')
        if shift is True:
            self.vertch=Pmw.Counter(g1.interior(),labelpos='n',label_text='Vertical Shift',datatype='numeric',entryfield_value=0,entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
            self.horzch=Pmw.Counter(g1.interior(),labelpos='n',label_text='Horizontal Shift',datatype='numeric',entryfield_value=0,entry_width=10,hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
            self.vertch.pack(side=tkinter.LEFT,padx=4,pady=5)
            self.horzch.pack(side=tkinter.LEFT,padx=4,pady=5)
        if shift is False:
            #colormaps
            self.colmap=Pmw.ComboBox(g1.interior(),
                            scrolledlist_items=ImCmap.maplist,dropdown=1,
                            labelpos='w',label_text='Colormaps',history=0,listheight=300,
                            selectioncommand=None,hull_background='#d4d0c8',label_background='#d4d0c8')
            if index==1: self.colmap.selectitem('Greys',setentry=1)    
            else: self.colmap.selectitem('Stdgamma',setentry=1) 
            self.colmap.pack(side=tkinter.LEFT,fill='x')
        print ('Slide',index,slide)
        if slide is not None:
            l = 'Contrib.'
            sv=50
            if shift is None:
                l= 'Thresh.'
                sv=0
            self.fadeCFvar=tkinter.Scale(g1.interior(),label=l,background='#d4d0c8',width=20,length=100,from_=0,to=100,orient=tkinter.VERTICAL,resolution=1,command=slide)
            self.fadeCFvar.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=10)
            self.fadeCFvar.set(sv)
        g1.pack(side=tkinter.TOP,padx=5,pady=5,expand='yes',fill='both')

class MultiFader:

    def __init__(self,imgwin,mapdata,dataFileBuffer,activeFileBuffer,dispayParams, filedir):
        
        self.imgwin=imgwin
        self.mapdata=mapdata
        self.dataFileBuffer=dataFileBuffer
        self.activeFileBuffer=activeFileBuffer
        self.dispayParams=dispayParams
        self.filedir = filedir
        self.multiFader=None
        self.mfimageexists=0
        

        self.multiFadedialog=Pmw.Dialog(self.imgwin,title="Multi Fader",buttons=('OK','Cancel'),defaultbutton='Cancel',
                                            command=self.doneMultiFade)
        h=self.multiFadedialog.interior()
        h.configure(background='#d4d0c8')
        self.mfadegroup=[]
        self.mfadeMaster=Pmw.ScrolledFrame(h,hscrollmode='dynamic',vscrollmode='static',usehullsize=1,hull_width=520,hull_height=500,hull_background='#d4d0c8')
        self.mfadeMaster.pack(side=tkinter.TOP,padx=1,pady=1,expand='yes',fill='both')
        self.mfadeMaster.component("frame").configure(background='#d4d0c8')
        self.mfadeMaster.component("clipper").configure(background='#d4d0c8')
        mfm=self.mfadeMaster.interior()
        self.mfadegroup.append(stitchChannelGroup(mfm,self.mapdata.labels,1,shift=False,slide=True))
        self.mfadegroup.append(stitchChannelGroup(mfm,self.mapdata.labels,2,shift=False,slide=True)) #self.domFadePreview))
        #preview button
        b=PmwTtkButtonBox.PmwTtkButtonBox(h,hull_background='#d4d0c8')
        b.add('Preview',command=self.domFadePreview,style='GREEN.TButton',width=10)
        b.add('Save',command=self.domFadeSave,style='SBLUE.TButton',width=10)
        b.add('Add',command=self.domFadeAdd,style='ORANGE.TButton',width=10)
        b.pack(side=tkinter.LEFT,padx=5,pady=5)
        self.multiFadedialog.show()

    def killmfimwin(self):
        self.multiFadedialog.withdraw()
        self.mfimageexists = 0
        self.mfimwin.destroy()

    def doneMultiFade(self, result):
        # cleanup
        self.multiFadedialog.withdraw()
        if self.multiFader is not None:
            self.killmfimwin()
        self.multiFader = None

    def domFadeAdd(self):
        n=len(self.mfadegroup)+1
        self.mfadegroup.append(stitchChannelGroup(self.mfadeMaster.interior(),self.mapdata.labels,n,shift=False,slide=True)) #self.domFadePreview))

    def domFadeSave(self):
        self.domFadePreview()
        #get file name
        fn=globalfuncs.trimdirext(self.dataFileBuffer[self.activeFileBuffer]['fname'])+'_'+str('MFADER')+'.tiff'
        fn=globalfuncs.ask_save_file(fn,self.filedir.get())
        if fn=='':
            print('Save cancelled')
            globalfuncs.setstatus(self.dispayParams.status,'Save cancelled')
            return
        globalfuncs.setstatus(self.dispayParams.status,"Saving HR image display...")
        self.multiFader.saveHDimage(fn)
        globalfuncs.setstatus(self.dispayParams.status, "Saving complete.")

    def domFadePreview(self,*args):
        for i in self.mfadegroup:
            if i.stitchch.getvalue()==():
                print('Choose data channels to fade: Channel '+str(i.index)+' is undefined.')
                globalfuncs.setstatus(self.dispayParams.status,'Choose data channels to fade: Channel '+str(i.index)+' is undefined.')
                return

        if self.multiFader is None:
            self.multiFader = Display.Display(self.imgwin, self.dispayParams.toggleVAR, self.dispayParams.viewFUNC, self.dispayParams.scaleVAR,
                                      self.dispayParams.scaleTextVAR, self.dispayParams.flipVAR, main=0,show=False, sf=self.dispayParams.scaleFact)
        self.multiFader.saveobj = []
        self.multiFader.zmxyi = self.dispayParams.zmxyi

        imgN=[]        
        for i in self.mfadegroup:
            i.dataindex = self.mapdata.labels.index(i.stitchch.getvalue()[0])+2
            cfdata=self.mapdata.data.get(i.dataindex)
            # if self.maindisp.zmxyi[0:4] != [0, 0, -1, -1]:
            #     cfdata = cfdata[::-1, :]
            #     cfdata = cfdata[self.maindisp.zmxyi[1]:self.maindisp.zmxyi[3], self.maindisp.zmxyi[0]:self.maindisp.zmxyi[2]]
            #     cfdata = cfdata[::-1, :]
            cfdata = np.transpose(cfdata[::-1,:])
            img = self.multiFader.placeData(cfdata, np.transpose(self.mapdata.mapindex[::-1, :]), self.dispayParams.status,
                                             xax=self.mapdata.xvals, yax=self.mapdata.yvals, domask=0, mask=[],
                                             datlab='CrossFade', returnonly=True,
                                             forceColor=i.colmap.getvalue()[0])
            img=img.convert('RGB')
            img_array = np.asarray(img)
            imgN.append(img_array)
        for imi in range(len(imgN)-1):
            #if imi==0:
            #    pilim=ImageChops.blend(imgN[imi],imgN[imi+1],alpha=self.mfadegroup[imi+1].fadeCFvar.get()/100.)
            #else:
            #    pilim = ImageChops.blend(pilim, imgN[imi + 1], alpha=self.mfadegroup[imi + 1].fadeCFvar.get() / 100.)
            alpha=1-self.mfadegroup[imi+1].fadeCFvar.get()/100.
            cc = -self.mfadegroup[0].fadeCFvar.get() #/100.            

            if imi==0:
                aa = np.array(imgN[imi]*alpha,dtype=np.uint8)
                bb = np.array(imgN[imi+1]*(1-alpha),dtype=np.uint8)
                pilim = ImageChops.add(Image.fromarray(aa), Image.fromarray(bb),offset=cc)
            else:
                aa = np.array(np.asarray(pilim)*alpha,dtype=np.uint8)
                bb = np.array(imgN[imi + 1]*(1-alpha),dtype=np.uint8)
                pilim = ImageChops.add(Image.fromarray(aa), Image.fromarray(bb),offset=cc)



        (w, h) = pilim.size
        (scalex, scaley) = self.multiFader.pixscale
        pilim=pilim.resize((int(w*scalex),int(h*scaley)))
        self.multiFader.savobj=pilim
        self.mfimage=ImageTk.PhotoImage(pilim)
        #create window if needed
        if not self.mfimageexists:
            self.mfimwin=Pmw.MegaToplevel(self.imgwin)
            self.mfimwin.title('MultiFade Display')
            self.mfimwin.userdeletefunc(func=self.killmfimwin)
            hf=self.mfimwin.interior()
            self.mfimframe=tkinter.Canvas(hf,bg='black',borderwidth=2, height=250, width=250, cursor='crosshair')
            self.mfimframe.pack(side=tkinter.LEFT,fill=tkinter.X)
            self.mfimageexists=1
            self.mfitems=[]
        #clear
        if self.mfitems !=[] : self.mfimframe.delete(self.mfitems.pop())
        #rescale canvas
        self.mfimframe.config(height=int(h*scaley),width=int(w*scalex))
        self.mfitems.append(self.mfimframe.create_image((int(w*scalex+scalex))/2,(int(h*scaley+scaley))/2,anchor='center', image=self.mfimage))


class CrossFader:
    
    def __init__(self,imgwin,mapdata,dataFileBuffer,activeFileBuffer,dispayParams, filedir):
        
        self.imgwin=imgwin
        self.mapdata=mapdata
        self.dataFileBuffer=dataFileBuffer
        self.activeFileBuffer=activeFileBuffer
        self.dispayParams=dispayParams
        self.filedir = filedir
        self.crossFader=None
        self.cfimageexists=0
        
        self.crossFadeDialog=Pmw.Dialog(self.imgwin,title="Cross Fader",buttons=('OK','Cancel'),defaultbutton='Cancel',
                                            command=self.doneCrossFade)
        h=self.crossFadeDialog.interior()
        h.configure(background='#d4d0c8')            
        self.fadegroup=[]        
        self.fadeIndexMax=2
        self.fadeMaster = tkinter.Frame(h)
        self.fadeMaster.configure(background='#d4d0c8')
        self.fadeMaster.pack(side=tkinter.TOP,padx=1,pady=1,expand='yes',fill='both')
        self.fadegroup.append(stitchChannelGroup(self.fadeMaster,self.mapdata.labels,1,shift=False))
        self.fadegroup.append(stitchChannelGroup(self.fadeMaster,self.mapdata.labels,2,shift=False))  
        #slider
        self.fadeCFvar=tkinter.IntVar()
        self.fadeCFvar.set(50)
        self.fadeCFvar=tkinter.Scale(h,label='Fader',background='#d4d0c8',variable=self.fadeCFvar,width=20,length=150,from_=0,to=100,orient=tkinter.HORIZONTAL,resolution=1,command=self.doFadePreview)
        self.fadeCFvar.pack(side=tkinter.TOP,fill='both',expand=1,padx=5,pady=10)          
        #preview button
        b=PmwTtkButtonBox.PmwTtkButtonBox(h,hull_background='#d4d0c8')
        b.add('Preview',command=self.doFadePreview,style='GREEN.TButton',width=10)
        b.add('Save',command=self.doFadeSave,style='SBLUE.TButton',width=10)
        b.pack(side=tkinter.LEFT,padx=5,pady=5)
        self.crossFadeDialog.show()     

    def doFadeSave(self):
        self.doFadePreview()
        #get file name
        fn=globalfuncs.trimdirext(self.dataFileBuffer[self.activeFileBuffer]['fname'])+'_'+str('CFADER')+'.tiff'
        fn=globalfuncs.ask_save_file(fn,self.filedir.get())
        if fn=='':
            print('Save cancelled')
            globalfuncs.setstatus(self.dispayParams.status,'Save cancelled')
            return
        globalfuncs.setstatus(self.dispayParams.status,"Saving HR image display...")
        self.crossFader.saveHDimage(fn)
        globalfuncs.setstatus(self.dispayParams.status, "Saving complete.")

    def doFadePreview(self,*args):        
        for i in self.fadegroup:
            if i.stitchch.getvalue()==():
                print('Choose data channels to fade: Channel '+str(i.index)+' is undefined.')
                globalfuncs.setstatus(self.dispayParams.status,'Choose data channels to fade: Channel '+str(i.index)+' is undefined.')
                return             
        preview=[]
        for i in self.fadegroup:
            i.dataindex = self.mapdata.labels.index(i.stitchch.getvalue()[0])+2
            cfdata=self.mapdata.data.get(i.dataindex)
            # if self.maindisp.zmxyi[0:4] != [0, 0, -1, -1]:
            #     cfdata = cfdata[::-1, :]
            #     cfdata = cfdata[self.maindisp.zmxyi[1]:self.maindisp.zmxyi[3], self.maindisp.zmxyi[0]:self.maindisp.zmxyi[2]]
            #     cfdata = cfdata[::-1, :]
            preview.append(np.transpose(cfdata[::-1,:]))
        #create image
  
        if self.crossFader is None:
            self.crossFader=Display.Display(self.imgwin,self.dispayParams.toggleVAR, self.dispayParams.viewFUNC, self.dispayParams.scaleVAR,
                                      self.dispayParams.scaleTextVAR,self.dispayParams.flipVAR,main=0,show=False,sf=self.dispayParams.scaleFact)
        self.crossFader.saveobj=[]
        self.crossFader.zmxyi = self.dispayParams.zmxyi
        #print self.fadegroup[0].colmap.getvalue()[0],self.fadegroup[1].colmap.getvalue()[0]
        imgA=self.crossFader.placeData(preview[0],np.transpose(self.mapdata.mapindex[::-1,:]),self.dispayParams.status,xax=self.mapdata.xvals,yax=self.mapdata.yvals,domask=0,mask=[],datlab='CrossFade',returnonly=True,forceColor=self.fadegroup[0].colmap.getvalue()[0])
        imgB=self.crossFader.placeData(preview[1],np.transpose(self.mapdata.mapindex[::-1,:]),self.dispayParams.status,xax=self.mapdata.xvals,yax=self.mapdata.yvals,domask=0,mask=[],datlab='CrossFade',returnonly=True,forceColor=self.fadegroup[1].colmap.getvalue()[0])
        imgA=imgA.convert('RGB')
        imgB=imgB.convert('RGB')
        
        pilim=Image.blend(imgA,imgB,alpha=1-(self.fadeCFvar.get()/100.))
        #self.crossFader.placePPMimage(newImg,forceData=True)
        
        (w,h)=pilim.size
        (scalex,scaley)=self.crossFader.pixscale
        
        pilim=pilim.resize((int(w*scalex),int(h*scaley)))
        self.crossFader.savobj=pilim
        self.cfimage=ImageTk.PhotoImage(pilim)
        #create window if needed
        if not self.cfimageexists:
            self.cfimwin=Pmw.MegaToplevel(self.imgwin)
            self.cfimwin.title('CrossFade Display')
            self.cfimwin.userdeletefunc(func=self.killcfimwin)
            hf=self.cfimwin.interior()    
            self.cfimframe=tkinter.Canvas(hf,bg='black',borderwidth=2, height=250, width=250, cursor='crosshair')
            self.cfimframe.pack(side=tkinter.LEFT,fill=tkinter.X)  
            self.cfimageexists=1
            self.cfitems=[]
        #clear
        if self.cfitems !=[] : self.cfimframe.delete(self.cfitems.pop())
        #rescale canvas
        self.cfimframe.config(height=int(h*scaley),width=int(w*scalex))
        self.cfitems.append(self.cfimframe.create_image((int(w*scalex+scalex))/2,(int(h*scaley+scaley))/2,anchor='center', image=self.cfimage))
    
    def killcfimwin(self):
        self.crossFadeDialog.withdraw()
        self.cfimageexists=0
        self.cfimwin.destroy()        
        

    def doneCrossFade(self,result):
        #cleanup
        self.crossFadeDialog.withdraw()
        if self.crossFader is not None: 
            self.killcfimwin()
        self.crossFader=None   
