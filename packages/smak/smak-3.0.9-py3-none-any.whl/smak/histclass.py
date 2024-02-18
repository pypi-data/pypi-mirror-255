import math
import numpy as np

class Histogram:
    def __init__(self,dlist,bins=25,nmin=None,nmax=None,log=False, wts=None):
        self.log = log
        if nmax is None: self.max=math.maximum.reduce(dlist)
        else: self.max=nmax
        if nmin is None: self.min=math.minimum.reduce(dlist)
        else: self.min=nmin
        if not log:
            self.min=float(self.min)
            self.max=float(self.max)
            self.bin_width=(self.max-self.min)/bins
            self.nbins=bins
            self.hist=np.zeros((self.nbins,2),dtype=np.float32)
            self.hist[:,0]=self.min+self.bin_width*(np.arange(self.nbins)+0.5)
        else:
            self.min=float(self.min)
            self.max=float(self.max)
            if self.min==0.0:
                self.min=1.0
            self.min=math.log10(self.min)
            self.max=math.log10(self.max)
            self.bin_width=(self.max-self.min)/bins
            self.nbins=bins
            self.hist=np.zeros((self.nbins,2),dtype=np.float32)
            self.hist[:,0]=self.min+self.bin_width*(np.arange(self.nbins))
            dlist = list(map(float,dlist))
            dlist = list(map(abs,dlist))
            dlist = list(map(math.log10,dlist))
        self.makehist(dlist,wts)

    def __len__(self):
        return self.hist.shape[0]

    def __getitem__(self, index):
        return self.hist[index]

    def __getslice__(self, first, last):
        return self.hist[first:last]
    
    def makehist(self,data,wts):
        self._addData(data,wts)
        #n=int((len(data)+999)/1000)
        #for i in range(n):
        #    self._addData(data[1000*i:1000*(i+1)],wts[1000*i:1000(i+1)])

    def _addData(self,data,wts=None):
        #data=array(data,dtype=np.float32)
        #data=np.repeat(data,np.logical_and(np.less_equal(data,self.max),np.greater_equal(data,self.min)))

        #data=np.floor((data-self.min)/self.bin_width).astype(np.int32)
        #nbins=self.hist.shape[0]
        #histo=np.add.reduce(np.equal(np.arange(nbins)[:,np.newaxis],data),-1)
        #histo[-1]=histo[-1]+np.add.reduce(np.equal(nbins,data))
        
        histo,edges = np.histogram(data,bins=self.nbins,range=(self.min,self.max),weights=wts)
        
        
        self.hist[:,1]=self.hist[:,1]+histo

    def normalize(self,norm=1.):
        self.hist[:,1]=norm*self.hist[:,1]/np.add.reduce(self.hist[:,1])

    def normalizeArea(self,norm=1.):
        self.normalize(norm/self.bin_width)





if __name__ == '__main__':
    import random
    list=[]
    for i in range(500):
        list.append(random.normalvariate(0,1))

    h=Histogram(list,nmin=-5,nmax=5)
    print(h.hist)     
    
    
