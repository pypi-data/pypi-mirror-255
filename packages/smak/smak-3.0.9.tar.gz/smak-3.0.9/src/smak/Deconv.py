import math
import string 
from numpy import fft as FFT
import numpy as np
import scipy.signal as sig

def eps():
    eps=1
    while (eps/2. + 1.) > 1.:
        eps = eps / 2.
    return eps


def circshift(a,v):
    #print a.shape,v
    r=abs(v[0])
    c=abs(v[1])
    r=int(r)
    c=int(c)
    rind=list(range(a.shape[0]))
    for i in range(r):
        rind.append(rind.pop(0))
    a=np.take(a,rind,axis=0)
    cind=list(range(a.shape[1]))
    for i in range(c):
        cind.append(cind.pop(0))
    a=np.take(a,cind,axis=1)
    return a   

def psf2otf(psf,outsize):
    psfsize=np.array(psf.shape)
    padsize=outsize-psfsize
    newpsf=np.zeros(outsize,dtype=np.float32)
    newpsf[0:psfsize[0],0:psfsize[1]]=psf
    psf=circshift(newpsf,-np.floor(psfsize/2))
    otf=FFT.fft2(psf)

    return otf    

def deconvwnr(I,PSF,filter=0,NSR=0):
    filter=int(filter)
    #init      
    ncorr=NSR
    icorr=[]
    sizeI=np.array(I.shape)
    I=np.array(I,dtype=np.float32)
    if filter:
        #apply window:
        hw=np.hanning(filter*2+1)
        ##bwr=MLab.kaiser(sizeI[0],1)
        ##bwc=MLab.kaiser(sizeI[1],1)
        bwr=np.ones(sizeI[0],dtype=np.float32)
        bwr[0:filter]=hw[0:filter]
        bwr[len(bwr)-filter-1:]=hw[filter:]
        bwc=np.ones(sizeI[1],dtype=np.float32)
        bwc[0:filter]=hw[0:filter]
        bwc[len(bwc)-filter-1:]=hw[filter:]        
        for i in range(int(sizeI[0])):
            I[i,:]=I[i,:]*bwc##.real
        for j in range(int(sizeI[1])):
            I[:,j]=I[:,j]*bwr##.real
    sizePSF=np.array(PSF.shape)
    numNSdim=[]
    for i in list(range(len(sizePSF))):
        if sizePSF[i]!=1:numNSdim.append(i)

    otf=psf2otf(PSF,sizeI)
    K=ncorr
    #skip step
    Denom=abs(otf)**2+K
    Nomin=np.conjugate(otf)*FFT.fft2(I)

    #check
    whats_tiny=max(np.ravel(abs(Nomin)))*math.sqrt(eps())
    whers_tiny=np.where(abs(Denom)<whats_tiny,1,0)
    ts=whers_tiny*Denom
    try:
        tsr=ts.real
    except:
        tsr=ts
    sign_tiny=np.where(tsr<0,-1,1)
    signed=sign_tiny*whats_tiny
    Denom=np.where(abs(Denom)<whats_tiny,0,1)*Denom+signed

    JFT=Nomin/Denom
    J=FFT.ifft2(JFT)
    try:
        J=J.real
    except:
        pass
    return J


def gauss_lin(x,mu,sig):
    return np.exp(-np.power(x-mu,2.)/(2*np.power(sig,2.)))

def dualg(x,mu,sig):
    return gauss_lin(x,mu,sig) + gauss_lin(x,-mu,sig)
    
def fannular(p2,xd,rs):
    siz=(p2-1)/2
    std=rs

    [yy,xx] = np.indices((p2,p2),dtype=np.float32)
    h = np.zeros((p2,p2),dtype=np.float32)
    yy=yy-siz
    xx=xx-siz
    
    for i in range(p2):
        for j in range(p2):
            r=math.sqrt(xx[i,j]*xx[i,j]+yy[i,j]*yy[i,j])
            h[i,j]=dualg(r,xd/2.,std)
    hm=np.max(np.max(h))
    print (hm)
    hs=np.where(h<eps()*hm,0,1)
    h=h*hs

    sumh = sum(sum(h))
    if sumh != 0:
        h  = h/sumh;
    return h
    

def fspecial(p2,p3):

    siz=(p2-1)/2
    std=p3

    [y,x] = np.indices((p2,p2),dtype=np.float32)
    y=y-siz
    x=x-siz
    arg=-(x*x + y*y)/(2*std*std)

    h=np.exp(arg)
    hm=np.max(np.max(h))
    print (hm)
    hs=np.where(h<eps()*hm,0,1)
    h=h*hs

    sumh = sum(sum(h))
    if sumh != 0:
        h  = h/sumh;
    return h

#test code
if __name__ == '__main__':   
    import ImRadon
    a=np.ones((500,500),dtype=np.float32)
    for i in range(70,85):
        for j in range(120,135):
            a[i,j]=100.
    psf=fspecial(500,40)
    psf2=fannular(31,15,1.5)
    
    nr = (1-20.0/100.0) * float(31)
    nr = int(round(nr/2))
    print ("nr",nr)
    if nr!=0:
        psf=np.zeros(psf2.shape)
        psf[nr:-nr,:]=psf2[nr:-nr,:]
    else:
        psf=psf2    
    
    ImRadon.imshow(psf)

    #blur
    blur=a.copy()
    
    blur = sig.convolve2d(a,psf,mode='same')
#    for i in range(blur.shape[0]):
#        blur[i,:]=np.convolve(blur[i,:],psf[2,:],mode=1)
#    for j in range(blur.shape[1]):
#        blur[:,j]=np.convolve(blur[:,j],psf[2,:],mode=1)
    rec=deconvwnr(blur,psf)
    ImRadon.imshow(blur)
    ImRadon.imshow(rec)
    