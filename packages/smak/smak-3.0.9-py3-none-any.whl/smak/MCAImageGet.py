#standard 
import math
import string
import time
import tkinter
import tkinter.simpledialog

#third party
import numpy as np
import Pmw

def dataSquares(n):
    list=[]
    for i in range(2,n):
        if math.fmod(n,i)==0.0:
            list.append([i,n/i])
    return list

def listfloat(x,y): return float(x)*y

####################################
## Main
####################################

class MCAdataRead:

    def __init__(self,datafn,dx,dy,xp,yp):
        t=time.clock()
        self.type='MCA'

        self.nxpts=xp
        self.nypts=yp
        self.channels=1
        self.labels=['OCR']
        self.comments=''
        self.xvals=list(map(listfloat,list(range(xp)),[dx]*xp))
        self.yvals=list(map(listfloat,list(range(yp)),[dy]*yp))
        self.energy=1
        dt=[]
        dtm=[]

        fid=open(datafn,'rU')

        for dpn in range(xp*yp):
            l=fid.readline()
            if l=='' or len(l)==0 or l[0]=='!' or l[0]=='#': continue
            dl=l.split()
            i=0
            ds=0
            for dp in dl:
                if i==0:
                    i=1
                    continue
                ds+=int(dp)
            dtm.append(ds)
            i+=1
        #make xy's
        xt=[]
        for i in range(yp):
            xt.extend(self.xvals)
        yt=[]
        for i in range(xp):
            yt.extend(self.yvals)
        yt.sort()
        #check points and assemble
        if len(dtm)<len(xt):
            #add zeros
            print('need to add...')
            while len(dtm)<len(xt):
                dtm.append(0)
        elif len(dtm)>len(xt):
            print('need to cut...')
            #cut out data
            dtm=dtm[:len(xt)]
        for i in range(len(dtm)):
            dt.append([xt[i],yt[i],dtm[i]])
        #array-ize data
        self.xvals=np.array(self.xvals)
        self.yvals=np.array(self.yvals)
        dt=np.array(dt)        
        self.data=np.reshape(dt,(self.nypts,self.nxpts,self.channels+2))
        print(time.clock()-t)

class importDataRead:

    def __init__(self,master,fn):
        self.master=master

        self.ImageFromMCA(fn)        
    
    def ImageFromMCA(self,fn):
        self.fn=fn
        #open and read file
        fid=open(fn,'rU')
#        self.lines=fid.readlines()
        self.lines=None
        read=1
        numpts=0
        while read:
            try:
                l=fid.readline()
                if l=='' or len(l)==0 or l[0]=='!' or l[0]=='#':
                    break
                numpts+=1
                #print read,numpts
            except:
                read=0
                break
        fid.close()
        #find valid data points
#        numpts=0
#        for l in self.lines:
#            if l=='' or len(l)==0 or l[0]=='#' or l[0]=='!':
#                continue
#            numpts+=1
        print('has ',numpts)
        #options for data size
        opts=dataSquares(numpts)
        optlist=[]
        self.optdict={}
        for o in opts:
            optlist.append(str(o[0])+' by '+str(o[1]))
            self.optdict[str(o[0])+' by '+str(o[1])]=o
        optlist.append('Custom')
        #make selection dialog
        self.sdialog=Pmw.SelectionDialog(self.master,title='Data Dimensions',buttons=('OK','Cancel'),scrolledlist_labelpos='n',label_text='Choose size of data (x,y)',
                                         scrolledlist_items=optlist,command=self.ImageFromMCAExec)
        self.sdialog.activate()

    def ImageFromMCAExec(self,result):
        sels=self.sdialog.getcurselection()
        if len(sels)!=1:
            return None
        self.sdialog.deactivate()
        if result=='Cancel':
            return None
        sels=sels[0]
        if sels=='Custom':
            xpts=tkinter.simpledialog.askinteger(title='Custom Data Size',prompt='Enter number of x data points: ')
            if xpts=='' or xpts==0: return None
            ypts=tkinter.simpledialog.askinteger(title='Custom Data Size',prompt='Enter number of y data points: ')
            if ypts=='' or ypts==0: return None
        else:
            xpts=self.optdict[sels][0]
            ypts=self.optdict[sels][1]
        #get step sizes
        dx=tkinter.simpledialog.askfloat(title='Data Step Size',prompt='Enter x data step size: ')
        if dx=='' or dx==0: return None
        dy=tkinter.simpledialog.askfloat(title='Data Step Size',prompt='Enter y data step size: ',initialvalue=dx)
        if dy=='' or dy==0: return None
        self.impdata=MCAdataRead(self.fn,dx,dy,xpts,ypts)
        