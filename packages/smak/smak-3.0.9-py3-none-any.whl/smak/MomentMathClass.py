import math
import cv2
import numpy as np
from scipy.stats import mstats as mStats
from scipy.stats import stats as Stats



#class for moment analysis math 

def median(t):
    t=np.sort(t)
    z=len(t)
    if z%2:
        return t[z//2]
    else:
        return (t[(z//2)-1]+t[z//2])/2.0

class MomentClass:
    def __init__(self,x,y,i,mask=None,all=1):
        self.x=x
        self.y=y
        self.i=i
        self.mask=mask
        self.moms={}
        if self.mask is not None: self.i=i*mask
        if all==1: self.calculateall()
        if all==2: self.calcbase()
        if all==3: self.calcshort()
        
    def calcshort(self):

        for i in range(2):
            for j in range(2):
                if i+j>4: continue
                self.calcmoment(i,j,force=1)

        self.A=self.moms[(0,0)]
        self.medx=self.moms[(1,0)]/self.moms[(0,0)]
        self.medy=self.moms[(0,1)]/self.moms[(0,0)]        

    def calculateall(self):
        for i in range(5):
            for j in range(5):
                if i+j>4: continue
                self.calcmoment(i,j,force=1)

        #normalize first moments
        self.A=self.moms[(0,0)]
        self.medx=self.moms[(1,0)]/self.moms[(0,0)]
        self.medy=self.moms[(0,1)]/self.moms[(0,0)]
        #calculate variances
        self.xxvar=(self.moms[(2,0)]-self.medx*self.moms[(1,0)])/self.moms[(0,0)]
        self.yyvar=(self.moms[(0,2)]-self.medy*self.moms[(0,1)])/self.moms[(0,0)]
        self.xyvar=(self.moms[(1,1)]-self.medx*self.moms[(0,1)])/self.moms[(0,0)]
        #calculate Skews
        self.xskew=(self.moms[(3,0)]-3*self.medx*self.moms[(2,0)]+2*self.medx**2*self.moms[(1,0)])/(self.moms[(0,0)]*self.xxvar**(1.5))
        self.yskew=(self.moms[(0,3)]-3*self.medy*self.moms[(0,2)]+2*self.medy**2*self.moms[(0,1)])/(self.moms[(0,0)]*self.yyvar**(1.5))
        #calculate Kurtosis
        self.xkurt=(self.moms[(4,0)]-4*self.medx*self.moms[(3,0)]+6*self.medx**2*self.moms[(2,0)]-3*self.medx**3*self.moms[(1,0)])/(self.moms[(0,0)]*self.xxvar**2)-3.0
        self.ykurt=(self.moms[(0,4)]-4*self.medy*self.moms[(0,3)]+6*self.medy**2*self.moms[(0,2)]-3*self.medy**3*self.moms[(0,1)])/(self.moms[(0,0)]*self.yyvar**2)-3.0

        self.calcbase()

    def calcbase(self):
        #calculate min/max/average/stddev
        if self.mask is None:
            #print('no mask')
            self.sum=np.sum(np.ravel(self.i))
            self.min=np.min(np.ravel(self.i))
            self.max=np.max(np.ravel(self.i))
            self.avg=np.sum(np.ravel(self.i))/len(np.ravel(self.i))
            self.stddev=np.std(np.ravel(self.i))
            self.median=np.median(np.ravel(self.i))
            self.mode=Stats.mode(np.ravel(self.i),keepdims=True)
        else:
            #print('mask')
            mi=[]
            ri=np.ravel(self.i)
            mk=np.ravel(self.mask)
            
            slow=False
            
            if slow:
                for j in range(len(ri)):
                    if mk[j]==1:mi.append(ri[j])
                mi=np.array(mi)
            else:
                mi = np.ma.MaskedArray(ri,mask=np.where(mk>0,False,True))
            
            
            self.sum=np.ma.sum(mi)
            self.min=np.ma.min(mi)
            self.max=np.max(mi)
            self.avg=np.sum(mi)/np.ma.count(mi)
            self.stddev=np.ma.std(mi)            
            self.median=np.ma.median(mi)
            self.mode=mStats.mode(mi)
            self.i=np.ma.take(mi.data,np.ma.where(mi.mask==False)).data

    def calcmoment(self,mx,my,force=0):
        if not force:
            if (mx,my) in list(self.moms.keys()): return
        #calculate
        xp=self.x**mx
        yp=self.y**my
        #Mij = sumx sumy x^i y^j i(x,y)
        new=xp*yp*self.i
        moment=sum(sum(new))
        self.moms[(mx,my)]=moment

class EllipseClass:
    def __init__(self,mask):
        self.mask=mask
        self.elp = None
        if len(mask)<5:
            return
        
        self.elp=cv2.fitEllipse(mask)
        (xc,yc),(d1,d2),angle = self.elp
        
        rmajor = max(d1,d2)
        rminor = min(d1,d2)
        
        self.rmajor=rmajor
        self.rminor=rminor
        self.d1=rmajor
        self.d2=rminor
        self.xc=xc
        self.yc=yc
        self.r1=d1
        self.r2=d2
        
        self.asprat = rmajor/rminor
        self.perim = cv2.arcLength(mask,True)
        
        if angle > 90:
            angle = angle - 90
        else:
            angle = angle + 90
        self.angle=angle
        
    def calcMajorLine(self):
        lx = self.xc - math.cos(math.radians(self.angle+0))*self.d1/2.
        rx = self.xc + math.cos(math.radians(self.angle+0))*self.d1/2.
        ly = self.yc - math.sin(math.radians(self.angle+0))*self.d1/2.
        ry = self.yc + math.sin(math.radians(self.angle+0))*self.d1/2.
        self.mjr={}
        self.mjr['lx']=lx
        self.mjr['ly']=ly
        self.mjr['rx']=rx
        self.mjr['ry']=ry
        #print (self.mjr)
        return (lx,ly,rx,ry)
    
    def calcMinorLine(self):
        lx = self.xc - math.cos(math.radians(self.angle+90))*self.d2/2.
        rx = self.xc + math.cos(math.radians(self.angle+90))*self.d2/2.
        ly = self.yc - math.sin(math.radians(self.angle+90))*self.d2/2.
        ry = self.yc + math.sin(math.radians(self.angle+90))*self.d2/2.
        self.mnr={}
        self.mnr['lx']=lx
        self.mnr['ly']=ly
        self.mnr['rx']=rx
        self.mnr['ry']=ry
        #print (self.mnr)
        return (lx,ly,rx,ry)
    
    def calcBoundingBox(self):
        self.calcMajorLine()
        self.calcMinorLine()
        
        x0=self.mjr['lx']+(self.mnr['lx']-self.xc)#
        y0=self.mjr['ly']+(self.mnr['ly']-self.yc)#
        x1=self.mjr['rx']-(self.mnr['rx']-self.xc)
        y1=self.mjr['ry']-(self.mnr['ry']-self.yc)
        x2=self.mjr['rx']+(self.mnr['rx']-self.xc)
        y2=self.mjr['ry']+(self.mnr['ry']-self.yc)
        x3=self.mjr['lx']+(self.mnr['rx']-self.xc)
        y3=self.mjr['ly']+(self.mnr['ry']-self.yc)        
        print (x0,y0,x1,y1,x2,y2,x3,y3)
        return (x0,y0,x1,y1,x2,y2,x3,y3,x0,y0)
    
    def calcElipArc(self,thst,thend,rf):
        thst=math.radians(float(thst))
        thend=thst+math.radians(float(thend))
        thdel = (thend-thst)/100.
        ang = math.radians(self.angle)
        thar = np.arange(thst,thend,thdel)
        x,y = np.array([self.xc+self.d1/2*rf*np.cos(thar)*np.cos(ang)-self.d2/2*rf*np.sin(thar)*np.sin(ang),
                        self.yc+self.d1/2*rf*np.cos(thar)*np.sin(ang)+self.d2/2*rf*np.sin(thar)*np.cos(ang)])

        rpts = []
        for i in range(len(thar)):
            rpts.append(x[i])
            rpts.append(y[i])
        rpts=tuple(rpts)
        #print (rpts)
        return rpts

    