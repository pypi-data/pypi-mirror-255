
import math
import string
import ImRadon
#import FFT
from numpy import fft as FFT
import numpy as np
from PIL import Image
#JOY Q
import GridTomoWrap
import congrid

def recon_gridFFT(arr,fil,theta=None):
    if theta is None:
        theta = np.arange(arr.shape[1])
    #angles = (pi/180)*theta
    angles=theta
    ang=len(angles)
    det=np.shape(arr)[0]
    geom=0
    center=det/2
    C=6
    sampl=1.2
    MPS=1.0
    R=1.0
    X0=0
    Y0=0
    ltbl=512
    imsiz=0
    S1=arr.copy()
    S2=arr.copy()
    (rt,imsiz)=GridTomoWrap.init_vals(ang,det,geom,angles,center,C,sampl,R,MPS,X0,Y0,ltbl,fil,imsiz)
    print('doneA',rt,imsiz)
    (rt,I1,I2)=GridTomoWrap.do_gridrecon(ang,det,imsiz,S1,S2)
    print('doneB',I1.shape,I2.shape)
    #resize
    new=congrid.congrid(I2,[det,det])
    new=arr
##    r=ImRadon.toimage(I2,cmin=0)
##    r=r.resize((det,det),Image.ANTIALIAS)
##    new=ImRadon.fromimage(r)
##    #normalize?
##    sum1=sum(arr)
##    mom1=sum(sum1)/len(sum1)
##    n1=mom1/sum(sum(new))
##    new=new*n1
    #flip?
    new=np.transpose(new[:,::-1])
    return new


def recon_FFT(arr,theta=None):
    if theta is None:
        theta = np.arange(arr.shape[1])
    th = (math.pi/180)*theta

    (nrow,nang)=np.shape(arr)
    im=np.zeros((nrow,nrow),np.Float)
    imc=np.zeros((nrow,nrow),np.Float)

    #assemble FFTs    
    for a in range(len(theta)):
        f=FFT.fft(arr[:,a])
        fr=f.real
        fc=f.imag
        if a:
            #rotate
            r=theta[a]-theta[a-1]
            im = ImRadon.imrotate(im,-r)
            imc = ImRadon.imrotate(imc,-r)
            im=np.array(im,typecode=np.Float)
            imc=np.array(im,typecode=np.Float)
        im[0,1:nrow-1]=im[0,1:nrow-1]+fr[1:nrow-1]
        imc[0,1:nrow-1]=imc[0,1:nrow-1]+fc[1:nrow-1]
    #rotate back
    r=theta[-1]-theta[0]
    im=ImRadon.imrotate(im,-r)
    imc=ImRadon.imrotate(imc,-r)

    #assemble complex matrix
    imall=np.zeros((nrow,nrow),np.Complex)
    for i in range(nrow):
        for j in range(nrow):
            imall[i,j]=complex(im[i,j],imc[i,j])
    #do inv FFT
    ans=FFT.ifft2(im)
            
    return ans
        











#test code
if __name__ == '__main__':   
    a=zeros((50,50),Float)
    for i in range(2,5):
        for j in range(20,25):
            a[i,j]=100. 
    b=ImRadon.radon(a)
    print(b.shape)
    c=recon_FFT(b)
    cr=c.real
    ci=c.imag
    #imshow(b)
    #c=inv_radon(b)
    ImRadon.imshow(cr)
    print(np.max(np.max(cr)))