
#standard
import math
import os.path
import string
import tkinter


#third party
import matplotlib as mplot
import matplotlib.backends.backend_tkagg as mplottk
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import matplotlib.transforms as TX
from matplotlib.transforms import Bbox
import numpy as np
import pylab


mplot.rcParams['figure.facecolor']='black'
mplot.rcParams['axes.labelcolor']='0.80'
mplot.rcParams['axes.edgecolor']='0.80'
mplot.rcParams['xtick.color']='0.80'
mplot.rcParams['ytick.color']='0.80'
mplot.rcParams['grid.color']='0.50'
mplot.rcParams['legend.fontsize']='small'
#mplot.rcParams['legend.frameon']='False'

################################
##     Graph Classes
################################

class MyGraph:
    def __init__(self,master,tool=0,event=0,callback=None,callback2=None,motioncallback=None,callpick=None,xlabel='',ylabel='',backcolor="black",grid=0,side=tkinter.TOP,padx=0,pady=0,expand=1,fill='both',facecolor=None,whsize=None,graphpos=[[0.1,0.1],[0.90,0.90]]):
        self.event=event
        self.tool=tool
        self.callback=callback
        self.callback2=callback2
        self.callpick=callpick
        self.motioncallback=motioncallback
        self.xlabel=xlabel
        self.ylabel=ylabel
        self.grid=grid
        self.backcolor=backcolor
        self.axesDict={}
        self.graphframe=tkinter.Frame(master)
        self.legend=None
        self.title=None
        self.titletext=''
        self.graphpos=graphpos
        self.graphframe.pack(side=side,expand=expand,fill=fill,padx=padx,pady=pady)

        self.figure=Figure(figsize=whsize)  #graph
        self.canvas = mplottk.FigureCanvasTkAgg(self.figure,master=self.graphframe)
        if event:
            self.markereventDown = self.canvas.mpl_connect('button_press_event', self.mouseDown)
            self.markereventUp = self.canvas.mpl_connect('button_release_event', self.mouseUp)
        if self.motioncallback!=None: self.motionevent= self.canvas.mpl_connect('motion_notify_event', self.motioncallback)
        self.setupaxes()
        self.secondaxes=None
        self.graphMarker=None
        self.graphMarkerpos=None
        self.markereventMove=None
        self.graphcontents=[]
        self.legendcontents=[]
        self.graphDict={}
        self.graphcontentlabels=[]
        self.druged = 0
        if facecolor!=None:
            mplot.rcParams['figure.facecolor']=facecolor

        self.canvas.get_tk_widget().pack(side=tkinter.TOP,expand=1,fill='both')
        if tool:
            self.graphtool = mplottk.NavigationToolbar2Tk(self.canvas,self.graphframe)
            self.graphtool.update()
        self.canvas.draw()

    def changeBackColor(self,shade):
        x=self.graphaxes.get_xaxis()
        y=self.graphaxes.get_yaxis()        
        if shade=='white':
            self.graphaxes.set_axis_bgcolor('white')            
            self.graphaxes.set_facecolor='0.75'
            self.graphaxes.set_edgecolor='0.75'


##            for c in x.get_children():
##                try:
##                    c.set_color('0.2')
##                except:
##                    pass
##            for c in y.get_children():
##                try:
##                    c.set_color('0.2')
##                except:
##                    pass
        else:
            self.graphaxes.set_axis_bgcolor('black')
            self.graphaxes.set_facecolor='black'
            self.graphaxes.set_edgecolor='black'

            
##            for c in x.get_children():
##                try:
##                    c.set_color('0.8')
##                except:
##                    pass
##            for c in y.get_children():
##                try:
##                    c.set_color('0.8')
##                except:
##                    pass
                
    def setupaxes(self):
        self.graphaxes=self.figure.add_subplot(111,label='main')
        self.axesDict['main']=self.graphaxes
        self.graphaxes.set_facecolor(self.backcolor)  #set_axis_bgcolor(self.backcolor)
        self.graphaxes.set_xlabel(self.xlabel)
        self.graphaxes.set_ylabel(self.ylabel)
        # if self.grid:
        #     self.graphaxes.grid(c='on',which='major',axis='both')
        # else:
        #     self.graphaxes.grid(c='off')
        self.graphaxes.set_position(Bbox(np.array(self.graphpos)))
        if self.callpick!=None:
            self.figure.canvas.mpl_connect('pick_event',self.callpick)

    def cleargraphs(self,redraw=0):
        self.graphaxes.clear()
        self.graphcontents=[]
        self.legendcontents=[]
        self.graphcontentlabels=[]
        for k in list(self.axesDict.keys()):
            if k!='main':
                self.figure.delaxes(self.axesDict[k])
        self.axesDict={}
        self.graphDict={}
        #self.setupaxes()
        self.uselegend(0)
        if self.title!=None:
            self.title.set_visible(False)
            self.title=None
            self.titletext=''
        #add marker if needed
        if redraw:
            if self.graphMarkerpos!=None: self.graphMarker=self.graphaxes.axvline(x=self.graphMarkerpos,color='white')
        else:
            self.graphMarker=None
            self.graphMarkerpos=None

    def setMain(self):
        self.figure.sca(self.graphaxes)

    def setLabels(self,x,y,color=None):
        self.xlabel=x
        self.ylabel=y
        if color==None:
            self.graphaxes.set_xlabel(self.xlabel)
            self.graphaxes.set_ylabel(self.ylabel)
        else:
            self.graphaxes.set_xlabel(self.xlabel,color=color)
            self.graphaxes.set_ylabel(self.ylabel,color=color)
            
    def setTitle(self,title,color='0.85',yht=0.95):
        if self.title==None:
            self.title=self.figure.suptitle(title,color=color,y=yht)
            self.titletext=title

    def uselegend(self,opt,loc=None):
        if self.legend!=None:
            self.legend.set_visible(False)
            self.legend=None
        if opt: #use it
            if loc==None: loc="upper right"
            self.legend=self.figure.legend(self.legendcontents,self.graphcontentlabels,loc=loc)
        else:
            pass

    def bar(self,xd,yd,color='green',edge='green',text='graph',log=None,width=None,align='center',picker=False):
        if width==None:
            width=abs(xd[0]-xd[1])/2.0
        if log==None:
            lv=False
        else: lv=True
        l=self.graphaxes.bar(xd,yd,width=width,color=color,edgecolor=edge,picker= picker,label=text,align=align,log=lv)
        self.graphcontents.append(l)
        p=mpatches.Patch(color=color,label=text)
        self.legendcontents.append(p)
        self.graphDict[text]=l[0]

    def boxplot(self,xd,xnames=None,notch=0,sym='b+',vert=1,whis=1.5,positions=None,widths=None,boxcolor=None,whiskers=None):
        l=self.graphaxes.boxplot(xd,notch=notch,sym=sym,vert=vert,whis=whis,positions=positions,widths=widths)
        self.graphcontents.append(l)
        self.graphDict['box']=l
        if xnames!=None:
            self.graphaxes.set_xticklabels(xnames)
        if boxcolor!=None:
            pylab.setp(l['boxes'], color=boxcolor)
        if whiskers!=None:
            pylab.setp(l['whiskers'], color=boxcolor)
        
    def savegraph(self,filename):
        p,ext=os.path.splitext(filename)
        if ext not in ['.jpg','.png','.eps','.pdf','.raw','.ps']:
            filename=p+'.png'
        self.figure.savefig(filename)

    def hexplot(self,xd,yd,color='green',symbol=None,size=10,text='graph',linewidth=1.0,picker=False,axes=None,tight=None,uselegend=1,log=None):
        binlog2=(0,1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768)
        if color=='green': cmaptype=mplot.pyplot.cm.get_cmap('nipy_spectral')
        else: cmaptype=mplot.pyplot.cm.get_cmap('bone_r')
        if axes=='newover':
            ty=self.graphaxes.get_ylim()
            gd=ty[1]-ty[0]
            dd=max(yd)-min(yd)
            scale=gd/dd
            offs=ty[0]-scale*min(yd)
            print(ty[0],ty[1])
            print(min(yd),max(yd))
            print(scale,offs)
            nyd=yd*scale+offs
            if log==None:
                l=self.graphaxes.hexbin(xd,nyd,bins=binlog2,cmap=cmaptype)
            else:
                l=self.graphaxes.hexbin(xd,nyd,bins='log',cmap=cmaptype)
            print("plotted in main",axes)
        elif axes==None or axes not in list(self.axesDict.keys()):
            if log==None:
                l=self.graphaxes.hexbin(xd,yd,bins=binlog2,cmap=cmaptype)
            else:
                l=self.graphaxes.hexbin(xd,yd,bins='log',cmap=cmaptype)
            self.graphaxes.autoscale(tight=tight)
            print("plotted in main",axes)
            ##print self.graphaxes.transData
        else:
            if log==None:
                l=self.axesDict[axes].hexbin(xd,yd,bins=binlog2,cmap=cmaptype)
            else:
                l=self.axesDict[axes].hexbin(xd,yd,bins='log',cmap=cmaptype)            
            self.axesDict[axes].autoscale(tight=tight)
            print("plotted in ",axes)
            ##print self.axesDict[axes].get_ybound()
        self.graphcontents.append(l)
        if uselegend: 
            self.graphcontentlabels.append(text)
            p=mpatches.Patch(color=color,label=text)
            self.legendcontents.append(p)
        self.graphDict[text]=l 

    def plot(self,xd,yd,color='green',symbol=None,size=10,text='graph',linewidth=1.0,picker=False,axes=None,tight=None,uselegend=1,log=None):
        ##print "plot:",axes
        if axes=='newover':
            ty=self.graphaxes.get_ylim()
            gd=ty[1]-ty[0]
            dd=max(yd)-min(yd)
            scale=gd/dd
            offs=ty[0]-scale*min(yd)
            print(ty[0],ty[1])
            print(min(yd),max(yd))
            print(scale,offs)
            nyd=yd*scale+offs
            if log==None:
                l=self.graphaxes.plot(xd,nyd,color=color,picker=picker, label=text,marker=symbol,markersize=size,lw=linewidth)
            else:
                l=self.graphaxes.semilogy(xd,nyd,color=color,picker=picker, label=text,marker=symbol,markersize=size,lw=linewidth)
            print("plotted in main",axes)
        elif axes==None or axes not in list(self.axesDict.keys()):
            if log==None:
                l=self.graphaxes.plot(xd,yd,color=color,picker=picker, label=text,marker=symbol,markersize=size,lw=linewidth)
            else:
                l=self.graphaxes.semilogy(xd,yd,color=color,picker=picker, label=text,marker=symbol,markersize=size,lw=linewidth)
            self.graphaxes.autoscale(tight=tight)
            print("plotted in main",axes)
            ##print self.graphaxes.transData
        else:
            if log==None:
                l=self.axesDict[axes].plot(xd,yd,color=color,picker=picker, label=text,marker=symbol,markersize=size,lw=linewidth)
            else:
                l=self.axesDict[axes].semilogy(xd,yd,color=color,picker=picker, label=text,marker=symbol,markersize=size,lw=linewidth)            
            self.axesDict[axes].autoscale(tight=tight)
            print("plotted in ",axes)
            ##print self.axesDict[axes].get_ybound()
        self.graphcontents.append(l)
        if uselegend: 
            self.graphcontentlabels.append(text)
            p=mpatches.Patch(color=color,label=text)
            self.legendcontents.append(p)
        self.graphDict[text]=l[0]

    def scatterplot(self,xd,yd,color='green',symbol=None,size=10,text='graph',linewidth=1.0,picker=False,axes=None,tight=None,uselegend=1,log=None):
        ##print "plot:",axes
        if axes=='newover':
            ty=self.graphaxes.get_ylim()
            gd=ty[1]-ty[0]
            dd=max(yd)-min(yd)
            scale=gd/dd
            offs=ty[0]-scale*min(yd)
            print(ty[0],ty[1])
            print(min(yd),max(yd))
            print(scale,offs)
            nyd=yd*scale+offs
            if log==None:
                l=self.graphaxes.scatter(xd,nyd,color=color,picker=picker, label=text,marker=symbol,lw=linewidth)
            else:
                l=self.graphaxes.semilogy(xd,nyd,color=color,picker=picker, label=text,marker=symbol,lw=linewidth)
            print("plotted in main",axes)
        elif axes==None or axes not in list(self.axesDict.keys()):
            if log==None:
                l=self.graphaxes.scatter(xd,yd,color=color,picker=picker, label=text,marker=symbol,lw=linewidth)
            else:
                l=self.graphaxes.semilogy(xd,yd,color=color,picker=picker, label=text,marker=symbol,lw=linewidth)
            self.graphaxes.autoscale(tight=tight)
            print("plotted in main",axes)
            ##print self.graphaxes.transData
        else:
            if log==None:
                l=self.axesDict[axes].scatter(xd,yd,color=color,picker=picker, label=text,marker=symbol,lw=linewidth)
            else:
                l=self.axesDict[axes].semilogy(xd,yd,color=color,picker=picker, label=text,marker=symbol,lw=linewidth)            
            self.axesDict[axes].autoscale(tight=tight)
            print("plotted in ",axes)
            ##print self.axesDict[axes].get_ybound()
        self.graphcontents.append(l)
        if uselegend: 
            self.graphcontentlabels.append(text)
            p=mpatches.Patch(color=color,label=text)
            self.legendcontents.append(p)
        #self.graphDict[text]=l[0]

    def addAxes(self,name):
        new=self.figure.add_subplot(111,label=name,frameon=False)
        new.set_axis_bgcolor(self.backcolor)
        self.axesDict[name]=new
        new.set_position(Bbox(np.array(self.graphpos)))
        new.set_xticks([])
        new.set_yticks([])
        ##print "created ",name
        
    def twinAxes(self,name):
        new = self.graphaxes.twinx()
        self.axesDict[name]=new
        new.set_position(Bbox(np.array(self.graphpos)))
        #new.set_xticks([])
        #new.set_yticks([])
        
    def removeplot(self,plot):
        if plot in self.graphDict:
            #self.graphaxes.remove(self.graphDict[plot])
            self.graphDict[plot].remove()
            self.graphDict.pop(plot)

    def get_xdata(self,plot):
        if plot in self.graphDict:
            #line=self.graphaxes.get_lines()[plot]
            return self.graphDict[plot].get_xdata()

    def get_ydata(self,plot):
        if plot in self.graphDict:
            #line=self.graphaxes.get_lines()[plot]
            return self.graphDict[plot].get_ydata()

    def get_color(self,plot):
        if plot in self.graphDict:
            #line=self.graphaxes.get_lines()[plot]
            return self.graphDict[plot].get_color()
        
    def draw(self):
        self.canvas.draw()

    def mouseMotion(self,event):
        self.druged=1

    def addMarker(self,x,y=None,color='white',secondcolor='white',linelist=None,draw=True,second=False):
        if self.graphMarker!=None:
            #print self.graphMarker
            try:
                self.graphaxes.lines.remove(self.graphMarker[0])
                if self.graphMarker[1]!=None: self.graphaxes.lines.remove(self.graphMarker[1])                
            except:
                print("no marker to remove error")
        self.graphMarkerpos=[x,y]
        if linelist==None:
            if not second:
                self.graphMarker=[self.graphaxes.axvline(x=x,color=color),None]
            else:
                self.graphMarker=[self.graphaxes.axvline(x=x,color=color),self.graphaxes.axvline(x=y,color=secondcolor)]
        else:
            if not second:
                self.graphaxes.axvline(x=x,color=color)
            else:
                self.graphaxes.axvline(x=x,color=color)
                self.graphaxes.axvline(x=y,color=secondcolor)
        if draw: self.canvas.draw()

    def mouseUp(self,event):
        if self.markereventMove==None: return
        if not self.druged:
            if event.button==1 or event.button==3: self.addMarker(event.xdata)
##            if self.graphMarker!=None:
##                #print self.graphMarker
##                self.graphaxes.lines.remove(self.graphMarker)
##            self.graphMarkerpos=event.xdata
##            self.graphMarker=self.graphaxes.axvline(x=event.xdata,color='white')
##            self.canvas.draw()
            #print event.button
            if self.callback!=None and event.button==1: self.callback(event.xdata,event.ydata)
            if self.callback2!=None and event.button>1: self.callback2(event.xdata,event.ydata)
        self.canvas.mpl_disconnect(self.markereventMove)
        self.markereventMove=None
        
    def mouseDown(self,event):
        self.druged = 0
        self.markereventMove = self.canvas.mpl_connect('motion_notify_event', self.mouseMotion)
