import os
import sys
import tkinter

#third party
import numpy as np
from PIL import Image, ImageTk
import Pmw


#local
import Display
import globalfuncs
import ImRadon
from MasterClass import MasterClass
import PmwTtkMenuBar



class TriColorWindowParams:
    def __init__(self, savetcdisplayasjpg, viewtricolormap, savetricolormap, maindisp, CMYKOn, tcrangedict, status, dodt, deadtimevalue, DTICRchanval, root, xyflip, tcrefresh, tclegendexist, showscalebar, showscalebarText, tcmarkerupdate):
        self.savetcdisplayasjpg = savetcdisplayasjpg
        self.viewtricolormap = viewtricolormap
        self.savetricolormap = savetricolormap
        self.maindisp = maindisp
        self.CMYKOn = CMYKOn
        self.tcrangedict = tcrangedict
        self.status = status
        self.dodt = dodt
        self.deadtimevalue = deadtimevalue
        self.DTICRchanval = DTICRchanval
        self.root = root
        self.xyflip = xyflip
        self.tcrefresh = tcrefresh
        self.tclegendexist = tclegendexist
        self.showscalebar = showscalebar
        self.showscalebarText = showscalebarText
        self.tcmarkerupdate = tcmarkerupdate



class TriColorWindow(MasterClass):

    def _create(self):
        #make window
        self.win=Pmw.MegaToplevel(self.imgwin)
        self.win.title('TriColor Plot Control')
        self.win.userdeletefunc(func=self.killtcplot)
        h=self.win.interior()    
        #Menu bar
        menubar=PmwTtkMenuBar.PmwTtkMenuBar(h)
        if os.sys.platform=='win32': menubar.component('hull').configure(bg='#d4d0c8')
        #file menu
        menubar.addmenu('File','')
        menubar.addmenuitem('File','command',label='Save TriColor Display',command=self.ps.savetcdisplayasjpg)
        menubar.addmenu('Limits','')
        menubar.addmenuitem('Limits','command',label='Restore Defaults',command=self.tcrestore)
        menubar.addmenu('Legend','')
        menubar.addmenuitem('Legend','command',label='View Legend',command=self.ps.viewtricolormap)
        menubar.addmenuitem('Legend','command',label='Save Legend',command=self.ps.savetricolormap)
        menubar.addmenuitem('Legend','separator')
        menubar.addmenuitem('Legend','checkbutton',label='Convert Palette to CMYK',command=self.dotcdisplay,variable=self.ps.CMYKOn)        
        menubar.pack(side=tkinter.TOP,fill=tkinter.X)
        #main window
        if sys.platform=='darwin': hwv=500
        else: hwv=400
        wmf=Pmw.ScrolledFrame(h,hscrollmode='dynamic',vscrollmode='static',usehullsize=1,hull_width=hwv,hull_height=400,hull_background='#d4d0c8')
        wmf.pack(side=tkinter.LEFT,fill='both')
        mf=wmf.interior()
        wmf.component("frame").configure(background='#d4d0c8')
        wmf.component("clipper").configure(background='#d4d0c8')
        lf=tkinter.Frame(mf,background='#d4d0c8')
        lf.pack(side=tkinter.LEFT,fill='both')
        #SCA and RGB selection
        f=tkinter.Frame(lf,background='#d4d0c8')
        #Header
        lab=tkinter.Label(f,text="Channel, Low Limits, High Limits",anchor=tkinter.W,background='#d4d0c8')
        lab.pack(side=tkinter.LEFT,fill='both')
        f.pack(side=tkinter.TOP,fill='both',pady=1)
        ents=[]
        self.entlook={}
        for c in self.mapdata.labels:
            index=self.mapdata.labels.index(c) + 2
            if c in self.ps.tcrangedict:
                loval=self.ps.tcrangedict[c][0]
                hival=self.ps.tcrangedict[c][1]
            else:
                loval="0"
                hival=self.gettczoomMax(index)
            #create a widget set for it
            f=tkinter.Frame(lf,background='#d4d0c8')
            f.pack(side=tkinter.TOP,fill='both',pady=10)
            eflow=Pmw.EntryField(f,labelpos='w',label_text=c,validate='real',entry_width=12,command=self.dotcdisplay,hull_background='#d4d0c8',label_background='#d4d0c8')
            eflow.pack(side=tkinter.LEFT)
            eflow.setentry(loval)
            ents.append(eflow)
            efhi=Pmw.EntryField(f,validate='real',entry_width=12,command=self.dotcdisplay,hull_background='#d4d0c8')
            efhi.pack(side=tkinter.LEFT)
            efhi.setentry(hival)#[:,:,index]))))
            #define dictionaries for reference
            self.entlook.update({c:[eflow,efhi]})
            self.ps.tcrangedict[c]=[loval,hival]
        Pmw.alignlabels(ents)
        #none frame
        f=tkinter.Frame(lf,background='#d4d0c8')
        lab=tkinter.Label(f,text="None",anchor=tkinter.W,background='#d4d0c8')
        lab.pack(side=tkinter.LEFT,fill='both')
        f.pack(side=tkinter.TOP,fill='both',pady=10)
        #Color select
        rf=tkinter.Frame(mf,background='#d4d0c8')
        rf.pack(side=tkinter.LEFT,fill='both')
        self.tcred=Pmw.RadioSelect(rf,buttontype='radiobutton',labelpos='n',orient=tkinter.VERTICAL,label_text='R',command=self.dotcdisplay,hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        self.tcgreen=Pmw.RadioSelect(rf,buttontype='radiobutton',labelpos='n',orient=tkinter.VERTICAL,label_text='G',command=self.dotcdisplay,hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        self.tcblue=Pmw.RadioSelect(rf,buttontype='radiobutton',labelpos='n',orient=tkinter.VERTICAL,label_text='B',command=self.dotcdisplay,hull_background='#d4d0c8',label_background='#d4d0c8',frame_background='#d4d0c8')
        for but in self.mapdata.labels:
            self.tcred.add(but,text=' ',value=but,background='#d4d0c8')
            self.tcgreen.add(but,text=' ',value=but,background='#d4d0c8')
            self.tcblue.add(but,text=' ',value=but,background='#d4d0c8')
        self.tcred.add('None',text=' ',value='None',background='#d4d0c8')
        self.tcgreen.add('None',text=' ',value='None',background='#d4d0c8')
        self.tcblue.add('None',text=' ',value='None',background='#d4d0c8')       
        self.tcred.pack(side=tkinter.LEFT,fill='y')
        self.tcgreen.pack(side=tkinter.LEFT,fill='y')
        self.tcblue.pack(side=tkinter.LEFT,fill='y')
        self.tcred.setvalue('None')
        self.tcgreen.setvalue('None')
        self.tcblue.setvalue('None')

        #exist variables
        self.tcimageexists=0

    def killtcplot(self):
        self.tricolorplotexist=0
        if self.tcimageexists:
            self.killtcimwin()
        self.kill()

    def killtcimwin(self):
        self.tcimageexists=0
        self.tcimwin.destroy()

    def tcrestore(self):
        for c in self.mapdata.labels:
            [eflow,efhi]=self.entlook[c]
            index=self.mapdata.labels.index(c)+2
            eflow.setentry('0')
            efhi.setentry(self.gettczoomMax(index))#[:,:,index]))))
            self.ps.tcrangedict[c]=['0', self.gettczoomMax(index)]
        self.dotcdisplay()

    def dotcdisplay(self, *args):
        if self.tcred.getvalue()==self.tcblue.getvalue()==self.tcgreen.getvalue()=='None':
            if self.tcimageexists:
                self.killtcimwin()
            return
        globalfuncs.setstatus(self.ps.status,"DISPLAYING...")

        if self.ps.maindisp.zmxyi[2]!=-1 and self.ps.maindisp.zmxyi[3]!=-1:     
            len_x, len_y=self.mapdata.data.get(0)[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]].shape[:2]
            #tdata=self.mapdata.data[::-1,:,:]
            #tdata=tdata[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2],:]
            #tdata=tdata[::-1,:,:]
        else:
            len_x, len_y=self.mapdata.data.shape[:2]
            #tdata=self.mapdata.data[:,:,:]
        tcdata=np.zeros((len_y,len_x,3),dtype=np.float32)
        #assemble red data
        if self.tcred.getvalue()!='None':
            redindex=self.mapdata.labels.index(self.tcred.getvalue())+2
            [eflow,efhi]=self.entlook[self.tcred.getvalue()]
            self.ps.tcrangedict[self.tcred.getvalue()]=[eflow.getvalue(),efhi.getvalue()]
            nodt=0
            if self.tcred.getvalue() in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodt=1
            if self.ps.dodt.get()==1 and not nodt:
                icr=self.mapdata.data.get(self.ps.DTICRchanval)
                dtcor=np.exp(float(self.ps.deadtimevalue.getvalue())*1e-6*icr)
                del icr
            else:
                dtcor=1.
            red=self.mapdata.data.get(redindex)*dtcor
            if self.ps.maindisp.zmxyi[2]!=-1 and self.ps.maindisp.zmxyi[3]!=-1:     
                red=red[::-1,:]
                red=red[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
                red=red[::-1,:]

            redmax=max(np.ravel(red))
            if redmax<1: redmax=1
            reddata,(scalex,scaley)=Display.preprocess(self.ps.root,np.transpose(red[::-1,:]),(None,None),float(efhi.getvalue())/redmax,float(eflow.getvalue())/redmax,convert=0,DEFAULT=1.0)
            if not self.ps.CMYKOn.get(): tcdata[:,:,0]=reddata
            else:
                tcdata[:,:,0]+=reddata/2
                tcdata[:,:,1]+=reddata/2
            del red
        #assemble green data
        if self.tcgreen.getvalue()!='None':
            greenindex=self.mapdata.labels.index(self.tcgreen.getvalue())+2
            [eflow,efhi]=self.entlook[self.tcgreen.getvalue()]
            self.ps.tcrangedict[self.tcgreen.getvalue()]=[eflow.getvalue(),efhi.getvalue()]
            nodt=0
            if self.tcgreen.getvalue() in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodt=1
            if self.ps.dodt.get()==1 and not nodt:
                icr=self.mapdata.data.get(self.ps.DTICRchanval)
                dtcor=np.exp(float(self.ps.deadtimevalue.getvalue())*1e-6*icr)
                del icr
            else:
                dtcor=1.
            green=self.mapdata.data.get(greenindex)*dtcor
            if self.ps.maindisp.zmxyi[2]!=-1 and self.ps.maindisp.zmxyi[3]!=-1:     
                green=green[::-1,:]
                green=green[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
                green=green[::-1,:]            
            greenmax=max(np.ravel(green))
            if greenmax<1: greenmax=1
            greendata,(scalex,scaley)=Display.preprocess(self.ps.root,np.transpose(green[::-1,:]),(None,None),float(efhi.getvalue())/greenmax,float(eflow.getvalue())/greenmax,convert=0,DEFAULT=1.0)
            if not self.ps.CMYKOn.get(): tcdata[:,:,1]=greendata
            else:
                tcdata[:,:,1]+=greendata/2
                tcdata[:,:,2]+=greendata/2
            del green
        #assemble blue data
        if self.tcblue.getvalue()!='None':
            blueindex=self.mapdata.labels.index(self.tcblue.getvalue())+2
            [eflow,efhi]=self.entlook[self.tcblue.getvalue()]
            self.ps.tcrangedict[self.tcblue.getvalue()]=[eflow.getvalue(),efhi.getvalue()]
            nodt=0
            if self.tcblue.getvalue() in ['ICR','I0','I1','I2','I0STRM','I1STRM','I2STRM']: nodt=1
            if self.ps.dodt.get()==1 and not nodt:
                icr=self.mapdata.data.get(self.ps.DTICRchanval)
                dtcor=np.exp(float(self.ps.deadtimevalue.getvalue())*1e-6*icr)
                del icr
            else:
                dtcor=1.
            blue=self.mapdata.data.get(blueindex)*dtcor
            if self.ps.maindisp.zmxyi[2]!=-1 and self.ps.maindisp.zmxyi[3]!=-1:     
                blue=blue[::-1,:]
                blue=blue[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
                blue=blue[::-1,:]
            bluemax=max(np.ravel(blue))
            if bluemax<1: bluemax=1
            bluedata,(scalex,scaley)=Display.preprocess(self.ps.root,np.transpose(blue[::-1,:]),(None,None),float(efhi.getvalue())/bluemax,float(eflow.getvalue())/bluemax,convert=0,DEFAULT=1.0)
            if not self.ps.CMYKOn.get(): tcdata[:,:,2]=bluedata
            else:
                tcdata[:,:,2]+=bluedata/2
                tcdata[:,:,0]+=bluedata/2
            del blue
        #match display order
        tcdata=tcdata[::self.ps.maindisp.xdir,::self.ps.maindisp.ydir]
        #convert to bin
        #print (max(np.ravel(tcdata[:,:,0])),max(np.ravel(tcdata[:,:,1])),max(np.ravel(tcdata[:,:,2])))
        ##UGLY! tcdata=skColor.hsv2rgb(tcdata)
        tcdata=tcdata.astype('b')
        #check for flip
        if self.ps.xyflip.get(): tcdata=np.transpose(tcdata)        
        if 1:
            pilim=ImRadon.toimage(np.transpose(tcdata),cmin=0,skip=1)
            self.tcppm=pilim
        else:
            #convert to ppm
            ppm=Display.array2ppm(tcdata)
            self.tcppm=ppm
            pilim=Image.open(Display.save_ppm(ppm))
        (w,h)=pilim.size

        pilim=pilim.resize((int(w*scalex),int(h*scaley)))
        self.tcimage=ImageTk.PhotoImage(pilim)
        #create window if needed
        if not self.tcimageexists:
            self.tcimwin=Pmw.MegaToplevel(self.imgwin)
            self.tcimwin.title('TriColor Image Display')
            self.tcimwin.userdeletefunc(func=self.killtcimwin)
            hf=self.tcimwin.interior()    
            self.tcimframe=tkinter.Canvas(hf,bg='black',borderwidth=2, height=250, width=250, cursor='crosshair')
            self.tcimframe.pack(side=tkinter.LEFT,fill=tkinter.X)

            #bindings for zoom...
            if sys.platform=='darwin':
                self.tcimframe.bind(sequence="<ButtonPress>",func=self.tcmacbutton)
                self.tcimframe.bind(sequence="<ButtonRelease>",func=self.tcmacbuttonrelease)                
            else:
                self.tcimframe.bind(sequence="<Control-ButtonPress>",func=self.tcaddzoompt)
                self.tcimframe.bind(sequence="<Control-ButtonRelease>",func=self.tcfinishzoom)
            #zoom menu
            self.tcpopmenu=tkinter.Menu(self.tcimframe,tearoff=0)
            self.tcpopmenu.add_command(label='Clear Zoom',command=self.tcclearzoom)              
            if sys.platform=='darwin':
                self.tcimframe.bind(sequence="<Button-2>", func=self.tcshowpopup)
            else:
                self.tcimframe.bind(sequence="<Button-3>", func=self.tcshowpopup)         
            self.tcitems=[]
            self.tcimageexists=1
        #clear        
        if self.tcitems !=[] : self.tcimframe.delete(self.tcitems.pop())
        #rescale canvas
        self.tcimframe.config(height=int(h*scaley),width=int(w*scalex))
        self.tcitems.append(self.tcimframe.create_image((int(w*scalex+scalex))/2,(int(h*scaley+scaley))/2,anchor='center', image=self.tcimage))
        if self.ps.tclegendexist==1:
            self.viewtricolormap()
        #marker updates
        for m in list(self.ps.maindisp.markerlist.keys()):
            if self.ps.maindisp.markerlist[m] is not None: self.ps.tcmarkerupdate(m)              
        #add scalebar if necessary
        if self.ps.showscalebar.get(): self.tcaddscalebartodisplay()
        if not self.ps.showscalebar.get(): self.tcremovescalebarfromdisplay()
        
        globalfuncs.setstatus(self.ps.status,"Ready")

    def gettczoomMax(self,index,dsum=False,opt=False,length=False):
        tdata=self.mapdata.data.get(index)
        if self.ps.maindisp.zmxyi[2] != -1 and self.ps.maindisp.zmxyi[3] != -1:
            tdata=tdata[::-1,:]
            tdata=tdata[self.ps.maindisp.zmxyi[1]:self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[0]:self.ps.maindisp.zmxyi[2]]
            tdata=tdata[::-1,:]
        if dsum:
            return str(sum(np.ravel(tdata)))
        if length:
            return str(len(np.ravel(tdata)))
        if not opt:
            return str(max(np.ravel(tdata)))
        else:
            return str(min(np.ravel(tdata)))
    
    def tcaddzoompt(self,event):
        global zdrag,zdrug
        zdrag=1
        zdrug=0
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        globalfuncs.setList(self.ps.maindisp.zmxyc,[x,y,x,y])
        (z,xi,yi)=self.ps.maindisp.datalookup(x,y)
        #JOY Q - wrong list length for zmxyi?
        self.ps.maindisp.zmxyi=[xi,yi,0,0,self.ps.maindisp.zmxyi[0],self.ps.maindisp.zmxyi[1]]
        #print x,y,self.zmx0,self.zmy0
        #create zoom line
        self.tczoomline=self.tcimframe.create_rectangle(tuple(self.ps.maindisp.zmxyc),width=2,outline='grey50')
        #create binding
        self.tcimframe.bind(sequence="<Motion>",func=self.tczoomdrag)

    def tcclearzoom(self):
        global zdrag,zdrug
        zdrag=0
        zdrug=0
        self.tczoomline=None
        globalfuncs.setList(self.ps.maindisp.zmxyi, [0,0,-1,-1,0,0])
        globalfuncs.setList(self.ps.maindisp.zmxyc, [0,0,0,0])
        #update display
        try:
            self.ps.maindisp.placePPMimage(self.ps.maindisp.raw)
            self.ps.tcrefresh()
        except:
            pass

 

    def tczoomdrag(self,event):
        global zdrag,zdrug
        zdrug=1
        canvas=event.widget
        x=canvas.canvasx(event.x)
        y=canvas.canvasx(event.y)
        self.ps.maindisp.zmxyc[2]=x
        self.ps.maindisp.zmxyc[3]=y
        (z,xi,yi)=self.ps.maindisp.datalookup(x,y)
        self.ps.maindisp.zmxyi[2]=xi
        self.ps.maindisp.zmxyi[3]=yi
        #update zoom line
        self.tcimframe.coords(self.tczoomline,tuple(self.ps.maindisp.zmxyc))
        
    def tcfinishzoom(self,event):
        global zdrag,zdrug
        if zdrag:
            self.tcimframe.unbind(sequence="<Motion>")
            #delete zoom line
            self.tcimframe.delete(self.tczoomline)
            if zdrug:
                #print self.zmxyc,self.zmxyi
                if self.ps.maindisp.zmxyi[0]>self.ps.maindisp.zmxyi[2]:self.ps.maindisp.zmxyi[0],self.ps.maindisp.zmxyi[2]=self.ps.maindisp.zmxyi[2],self.ps.maindisp.zmxyi[0]
                if self.ps.maindisp.zmxyi[1]>self.ps.maindisp.zmxyi[3]:self.ps.maindisp.zmxyi[1],self.ps.maindisp.zmxyi[3]=self.ps.maindisp.zmxyi[3],self.ps.maindisp.zmxyi[1]                
                #update display
                #print self.zmxyc,self.zmxyi
                self.ps.tcrefresh()
                self.ps.maindisp.placePPMimage(self.ps.maindisp.raw)
        zdrag=0
        zdrug=0

    def tcshowpopup(self,event):
        self.tcpopmenu.post(event.x_root,event.y_root)
        
    def tcaddscalebartodisplay(self):
        #calculate size
        w, h=self.tcimage.width(), self.tcimage.height()
        sbwp=w*.1
#        first=self.mapdata.xvals[0]#self.zmxyi[0]]
#        last=self.mapdata.xvals[-1]#self.zmxyi[2]]
        first=self.mapdata.xvals[self.ps.maindisp.zmxyi[0]]
        last=self.mapdata.xvals[self.ps.maindisp.zmxyi[2]]
        sbwm=abs(first-last)*.1*1000
        scl=sbwp/sbwm
        sbwr=globalfuncs.chop(sbwm,0.1)
        sbwp=sbwr*scl
        #print sbwp,sbwm
        self.tcsbid=self.tcimframe.create_rectangle(self.ps.maindisp.scalebarx,self.ps.maindisp.scalebary,self.ps.maindisp.scalebarx+sbwp,self.ps.maindisp.scalebary+10,fill='white')
        if self.ps.showscalebarText: self.tcsbtext=self.tcimframe.create_text(self.ps.maindisp.scalebarx+10+sbwp,self.ps.maindisp.scalebary+5,anchor=tkinter.W,fill='white',text=str(int(sbwr)))
    
    def tcremovescalebarfromdisplay(self):
        try:
            self.tcsbid.delete()
        except:
            pass
        try:
            self.tcsbtext.delete()
        except:
            pass

    def tcmacbutton(self,event):
        if event.num>1: return
        if event.state==4: self.tcaddzoompt(event)
        
    def tcmacbuttonrelease(self,event):
        if event.num>1: return
        if event.state==4+256: self.tcfinishzoom(event)
        