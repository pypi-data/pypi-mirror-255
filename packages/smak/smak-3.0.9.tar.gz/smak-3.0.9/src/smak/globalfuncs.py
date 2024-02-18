# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 18:28:37 2023

@author: stewards
"""
#standard
from functools import reduce
import os
import sys
import math

#third party
import tkinter
from tkinter import ttk
import numpy as np
import cv2 as cv

global LASTDIR
LASTDIR = 1
global MINSIZE
global DEFAULT_HEIGHT
DEFAULT_HEIGHT = 255
MINSIZE = 300



def getModePath():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        running_mode = 'Frozen/executable'
    else:
        try:
            app_full_path = os.path.realpath(__file__)
            application_path = os.path.dirname(app_full_path)
            running_mode = "Non-interactive (e.g. 'python myapp.py')"
        except NameError:
            application_path = os.getcwd()
            running_mode = 'Interactive'    
    return running_mode, application_path

##############################
##  legacy functions
##############################


def writeblankline(fid,n):
    for i in range(n):
        fid.write('* BLANK LINE\n')

def trimdirext(f):
    return os.path.splitext(os.path.basename(f))[0]
    #firstind=rfind(f,os.sep)+1
    #lastind=rfind(f,'.')
    #cf=f[firstind:lastind]
    #print cf,os.path.splitext(os.path.split(cf)[1])[0]
    #return cf

#entry replace
def entry_replace(ent, val):
    ent.delete(0,len(ent.get()))
    ent.insert(0,val)
    ent.checkentry()

def entry_replace_d(ent, val,dig):
    ent.delete(0,len(ent.get()))
    val=str(val)
    decind=val.rfind('.')
    eind=val.rfind("e")
    if eind==-1:
        val=val[:decind+dig]
    else:
        val=val[:4]+val[eind:len(val)]
    ent.insert(0,val)
    ent.checkentry()

def valueclip_d(val,dig):
    val=str(val)
    decind=val.rfind('.')
    eind=val.rfind("e")
    if eind==-1:
        val=val[:decind+dig]
    else:
        val=val[:4]+val[eind:len(val)]
    return val

#functions for updating status bars
def setstatus(n,format):
    n.config(text=format)
    n.update_idletasks()
    
def setstatus_d(n,val,dig):
    val=str(val)
    decind=val.rfind('.')
    eind=val.rfind("e")
    if eind==-1:
        val=val[:decind+dig]
    else:
        val=val[:4]+val[eind:len(val)]
    n.config(text=val)
    n.update_idletasks()

def clearstatus(n):
    n.config(text=" ")
    n.update_idletasks()
    
#Load filename into an entry
def fileget(master,ent,dir='',check=1,replace=True):
    global LASTDIR
    fty=[("data files","*.dat"),("HDF5 data files","*.hdf5"),("NXS data files","*.nxs"),("H5 data files","*.h5"),("SUPER files","*.*G"),("all files","*")]
    if LASTDIR==1:
        fty=[fty[1],fty[3],fty[2],fty[0],fty[4],fty[5]]
    if LASTDIR==2:
        fty=[fty[2],fty[1],fty[0],fty[3],fty[4],fty[5]]
    if LASTDIR==3:
        fty=[fty[5],fty[0],fty[1],fty[2],fty[3],fty[4]]
    fn=ask_for_file(fty,dir)
    if fn!='':
        sdir=fn.rfind(os.sep)
        fp=fn.split('.')
        exten=fp[-1]
        if exten.lower()=='dat': LASTDIR=0
        elif exten[0].upper()=='H': LASTDIR=1
        elif exten[0].upper()=='N': LASTDIR=2
        else: LASTDIR=3
    if replace: 
        entry_replace(ent,fn)
    master.focus_set()
    return fn

def ask_for_file(defaults,dir,check=1,multi=False):
    f = ''
    if not os.path.exists(dir): dir=''
    if not multi: func=tkinter.filedialog.askopenfilename
    else: func=tkinter.filedialog.askopenfilenames
    if dir=='':
        f = func(filetypes=defaults)
    else:
        f = func(filetypes=defaults,initialdir=dir)        
    return f

def ask_save_file(fn,dir,ext=None):
    f=''
    if dir=='':
        if ext is not None:
            f = tkinter.filedialog.asksaveasfilename(initialfile=fn,filetypes=ext)
        else:
            f = tkinter.filedialog.asksaveasfilename(initialfile=fn)
    else:
        if ext is not None:
            f = tkinter.filedialog.asksaveasfilename(initialfile=fn,initialdir=dir,filetypes=ext)
        else:
            f = tkinter.filedialog.asksaveasfilename(initialfile=fn,initialdir=dir)
    return f

#######################################
## Array index
######################################

def indexme(a,val):
    b=np.sort(a)
    if sum(a==b)==len(a):
        i=np.searchsorted(a,val)
    else:
        i=np.searchsorted(b,val)
        i=len(a)-i
    return i

def point_inside_circle(x,y,circle):
    #circle is [(centerx,centery),radius]
    dist=math.sqrt((x-circle[0][0])**2+(y-circle[0][1])**2)
    if dist<=circle[1]:
        return True
    else:
        return False
# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.
def point_inside_polygon(x,y,poly):
    n = len(poly)
    inside = 0
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside


def polygon_centroid(vertexes):
     _x_list = [vertex [0] for vertex in vertexes]
     _y_list = [vertex [1] for vertex in vertexes]
     _len = len(vertexes)
     _x = sum(_x_list) / _len
     _y = sum(_y_list) / _len
     return(_x, _y)


def perform_affine_transform(points,afftranmat):
    #make matrix -- afftranmat = [x trans, y trans, scale, rotation]
    output=[]
    angle = math.radians(afftranmat[3])
    scale = afftranmat[2]
    tm = np.array([[math.cos(angle)*scale, -math.sin(angle), afftranmat[0]],
                   [math.sin(angle), math.cos(angle)*scale, afftranmat[1]],
                   [0,0,1]])
    for pair in points:
        input = np.array([[pair[0]],[pair[1]],[1]])
        res=np.dot(tm,input)
        res=np.ravel(res)
        output.append((res[0],res[1]))
    return output

def lineareqn(pars,point):
    return pars[0]*point+pars[1]
def linearFit(point,p0,p1):
    return lineareqn([p0,p1],point)

def gausseqn(pars,point):
    #return pars[0]*exp(-(point-pars[1])**2/(2*pars[2]**2))
    return pars[0]*np.exp(-(point-pars[1])**2/(2*pars[2]**2))+pars[3]
def gaussFit(point,p0,p1,p2,p3):
    return gausseqn([p0,p1,p2,p3],point)

def gausseqnline(pars,point):
    #return pars[0]*exp(-(point-pars[1])**2/(2*pars[2]**2))
    return pars[0]*np.exp(-(point-pars[1])**2/(2*pars[2]**2))+pars[3]*point+pars[4]
def gausslineFit(point,p0,p1,p2,p3,p4):
    return gausseqnline([p0,p1,p2,p3,p4],point)


def save_ppm(ppm, fname=None):
    import tempfile
#    if fname is None:
#        fname = tempfile.mktemp('.ppm')
    td=tempfile.gettempdir()
    fname=td+'\\SMAK.ppm'
    f = open(fname, 'w')
    f.write(ppm)
    f.close()
    return fname

def array2ppm(image):
    # scaling
    if len(image.shape) == 2:
        # B&W:
        image = np.transpose(image)
        return "P5\n#PPM version of array\n%d %d\n255\n%s" % \
               (image.shape[1], image.shape[0], np.ravel(image).tobytes())
    else:
        # color
        image = np.transpose(image, (1, 0, 2))
        return "P6\n%d %d\n255\n%s" % \
               (image.shape[1], image.shape[0], np.ravel(image).tobytes())
               

###########################
## Sig Figs
###########################

def frange(start, end=None, inc=None):
    #"A range function, that does accept float increments end point INCLUSIVE..."
    flag=1
    if end is None:
        end = start + 0.0
        start = 0.0
        flag=0
    if inc is None:
        inc = 1.0
    L = []
    while 1:
        next = start + len(L) * inc
        if inc > 0 and next >= end:
            break
        elif inc < 0 and next <= end:
            break
        L.append(next)
    if flag and abs((L[len(L)-1]-end))>1e-8: L.append(end)
    return L

def chop(x,n=0):
    if n%1:
        d=int(10*n)
        return round(x,d-1-int(math.floor(math.log10(abs(x)))))
    else:
        return round(x,n)
    
def getSNR(x,type=0):
    x=np.sort(x)
    pct=int(len(x)/10)
    hp=int(len(x)/2)
    if not type:
        peak=np.mean(x[len(x)-pct:])
        std=np.std(x[0:hp])
    else:
        peak=np.mean(x[0:pct])
        std=np.std(x[hp:])
#    print peak,std,sqrt(peak)
    if type:
        if std!=0:
            return float(peak/std)
        else:
            return 1.
    else:
        if peak!=0:
            return math.sqrt(peak)
        else:
            return 1.

def fixlabelname(str):
    #take underscores out and replace with a "."
    str=str.replace('_','.')
    str=str.replace('#','.')
    return str

def powernext(n):
    for i in range(8):
        n|=n>>2**i
    n+=1
    return n

            
def filterconvolve(data,filter,z=0):
    filter=np.array(filter,dtype=np.float32)
    data=np.array(data,dtype=np.float32)
    usecv=1
    if usecv:
        inp=data#cv.fromarray(data)#,allowND=True)
        out=data#cv.fromarray(data)#,allowND=True)
        out = cv.filter2D(inp, -1, filter)
        out = np.asarray(out)
        return out
    else:    
        #assume filter is odd and square...

        s=filter.shape[0]
        sh=int(int(s)/2)
        (xlen,ylen)=data.shape
        newdata=np.zeros((xlen,ylen),dtype=np.float32)
        #expand original data...
        xdata=padforconvolve(data,sh)
        for i in range(xlen):
            for j in range(ylen):
                newdata[i,j]=subfilterconvolve(xdata[i:i+2*sh+1,j:j+2*sh+1],filter,z=z)
        return newdata

def subfilterconvolve(data,filter,z=0):
    #print data.shape,filter.shape
    t=data*filter
    s=np.sum(np.ravel(t))
    if z:
        return abs(s)
    else:
        return s

def padforconvolve(data,sh):
    (xlen,ylen)=data.shape
    nxl=xlen+2*sh
    nyl=ylen+2*sh
    newdata=np.zeros((nxl,nyl),dtype=np.float32)
    for i in range(nxl):
        if i>=sh and i<=xlen-1:
            newl=makenewpadline(data[i-sh,:],nyl,sh)  
        elif i<sh:
            newl=makenewpadline(data[0,:],nyl,sh)  
        else:
            newl=makenewpadline(data[xlen-1,:],nyl,sh)
        newdata[i,:]=newl
    return newdata

def makenewpadline(data,newy,sh):
    newl=np.zeros(newy,dtype=np.float32)
    ylen=len(data)
    for j in range(newy):
        if j<sh:
            newl[j]=data[0]
        elif j>ylen-1:
            newl[j]=data[ylen-1]
        else:
            newl[j]=data[j-sh]
    return newl


def setList(list1, list2):
        if len(list1) == len(list2):
            for i in range(len(list2)):
                list1[i] = list2[i]
        else:
            print("Lists not same length")

def find_nearest(array,value):
    idx=(np.abs(array-value)).argmin()
    return idx

def powerrange(n):
    rv=[0]
    if n==0: return rv
    nv=1
    while nv<=n:
        rv.append(nv)
        nv=nv*2
    return rv
        

def factors(n):    
    return reduce(list.__add__, 
                ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0))







