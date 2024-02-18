
import math
import string 
import numpy as np
import ImRadon
import FFTtomo
import time
#from Scientific.Functions.LeastSquares import *
#from Scientific.Functions.LeastSquares import leastSquaresFit
##from scipy.optimize import leastsq as leastSquaresFit
from scipy.optimize import curve_fit

#fit sinogram function
def sine_wave(x,a):
    #a[0]=rotation center
    #a[1]=amplitude
    #a[2]=phase
    x=np.array(list(map(float,x)))
    a=list(map(float,a))
    f=a[0]+a[1]*math.sin(x+a[2])
    pder=np.np.zeros((len(x),3),np.Float)
    pder[:,0]=np.ones(len(x),np.Float)
    pder[:,1]=np.transpose(math.sin(x+a[2]))
    pder[:,2]=np.transpose(a[1]*math.cos(x+a[2]))
    return f,pder

def sine_wave_cf(a,x):
    f=a[0]+a[1]*math.sin(x+a[2])
    return f
def sine_wave_cfnew(x,p0,p1,p2):
    return sine_wave_cf([p0,p1,p2],x)

def do_cf_dataalign(x,y):
    ret=[]
    for i in range(len(x)):
        ret.append((x[i],y[i]))
    return ret

def sinogram(input,angles,acc_values=0,air_values=10,cogret=0,auto_center=0,center=0,fluo=0):
    #ncols=len(input[:,0])
    #nrows=len(input[0,:])
    (ncols,nrows)=np.shape(input)
    #remove column if even number
    if ncols%2==0: ncols=ncols-1
    #remove acc values
    output=input[acc_values:ncols-acc_values-1,:]
    output=output.astype(np.Float)
    ncols=np.shape(output)[0]

    cog=np.np.zeros(nrows,np.Float)
    linear=np.arange(ncols,typecode=np.Float) / (ncols-1)
    no_air=np.np.zeros(ncols)+0.0001
    lin2=np.arange(ncols,typecode=np.Float)+1.0
    weight=np.ones(nrows,typecode=np.Float32)
    for i in range(nrows):
        if air_values>0:
            air_left=sum(output[0:air_values-1,i])/air_values
            air_right=sum(output[ncols-air_values:ncols-1,i])/air_values
            air=air_left+linear*(air_right-air_left)
        else:
            air=no_air
        if not fluo:
            for jj in range(ncols):
                if air[jj]>1e-5:
                    t=output[jj,i]/air[jj]
                    if t==0:
                        output[jj,i]=0
                    else:
                        try: output[jj,i]=-math.log(t)  #CHECK HERE output(0,i) = -alog(output(*,i)/air > 1.e-5)
                        except: output[jj,i]=0.0001
                else: output[jj,i]=0.0001
        if sum(output[:,i]):
            cog[i]=sum(output[:,i]*lin2)/sum(output[:,i])
        else: cog[i]=0
    odds=np.arange(1,nrows,2)#where(np.arange(nrows)%2,1,0)
    evens=np.arange(0,nrows,2)#where(np.arange(nrows)%2,0,1)
    x=angles*math.pi/180
    x=np.array(x)
    #estimate of inital rotation parameters
    a=[(ncols-1)/2.,(max(cog) - min(cog))/2., 0.]
    ##fitdat=do_cf_dataalign(np.take(x,odds),np.take(cog,odds))
    ##(a,err)=leastSquaresFit(sine_wave_cf,a,fitdat)
    result,cov=curve_fit(sine_wave_cfnew,np.take(x,odds),np.take(cog,odds),p0=a)
    #cog_fit=1 #CURVEFIT cog_fit = curvefit(x(odds), cog(odds), weight(odds), a, sigmaa, function_name='sine_wave')
    cog_odd=result[0]-1##a[0]-1
    print('Fitted COG for odd rows = '+str(cog_odd)+' +/- '+str('error'))
    ##fitdat=do_cf_dataalign(np.take(x,evens),np.take(cog,evens))
    ##(a,err)=leastSquaresFit(sine_wave_cf,a,fitdat)
    result,cov=curve_fit(sine_wave_cfnew,np.take(x,evens),np.take(cog,evens),p0=a)
    #cog_fit=1 #CURVEFIT curvefit(x(evens), cog(evens), weight(evens), a, sigmaa, function_name='sine_wave')
    cog_even=result[0]-1##a[0]-1
    print('Fitted COG for even rows = '+str(cog_even)+' +/- '+str('error'))
    #could fix odd/even backlash here -- forget it for now.
    ##fitdat=do_cf_dataalign(x,cog)
    ##(a,err)=leastSquaresFit(sine_wave_cf,a,fitdat)
    result,cov=curve_fit(sine_wave_cfnew,x,cog,p0=a)    
    #cog_fit=1 #CURVEFIT curvefit(x, cog, weight, a, sigmaa, function_name='sine_wave')
    cog_mean=result[0]-0o1##a[0]-1
    error_before=cog_mean-(ncols-1)/2.

    shift_amount=0
    print('Fitted COG = '+str(cog_mean)+' +/- '+str('error'))
    print('Error before correction (offset from center of image) = '+str(error_before))
    do_shift=0
    if auto_center: do_shift=1
    if center!=0: do_shift=1
    if do_shift:
        if auto_center: center=cog_mean
        shift_amount=round(center-(ncols-1)/2.)
        npad=int(2*abs(shift_amount))
        if air_values>0:
            pad_values=air_values
        else:
            pad_values=1
        if shift_amount<0:
            pad_left=np.zeros((npad,nrows),np.Float)
            temp=sum(output[0:npad,:])/pad_values
            for i in range(npad):
                pad_left[i,:]=temp
            newout=np.zeros((ncols+npad,nrows),np.Float)
            newout[0:npad,:]=pad_left
            newout[npad:ncols+npad,:]=output
            output=newout
            ncols=np.shape(output)[0]
        else:
            pad_right=np.zeros((npad,nrows),np.Float)
            temp=sum(output[ncols-npad:ncols-1,:])/pad_values
            for i in range(npad):
                pad_right[i,:]=temp
            newout=np.zeros((ncols+npad,nrows),np.Float)
            newout[0:ncols:]=output
            newout[ncols:ncols+npad,:]=pad_right
            output=newout
            ncols=np.shape(output)[0]
        lin2=np.arange(ncols,typecode=np.Float)+1.0
        for i in range(nrows):
            if sum(output[:,i]):
                cog[i]=sum(output[:,i]*lin2)/sum(output[:,i])
            else: cog[i]=0
        ##fitdat=do_cf_dataalign(x,cog)   
        ##(a,err)=leastSquaresFit(sine_wave_cf,a,fitdat)
        result,cov=curve_fit(sine_wave_cfnew,x,cog,p0=a) 
        #cog_fit=1 #CURVEFIT curvefit(x, cog, weight, a, sigmaa, function_name='sine_wave')
        cog_mean=result[0]-1#a[0]-1
        error_after=cog_mean-(ncols-1)/2.
        print('Fitted COG after correction= '+str(cog_mean)+' +/- '+str('error'))
        print('Error after correction (offset from center of image) = '+str(error_after))
    #cog=[cog,cog_fit]
    print('Used average of '+str(air_values)+' pixels for air')
    print('Skipped '+str(acc_values)+' acceleration pixels')
    print('Center corrected '+str(shift_amount)+' pixels')
    print('Absolute center = '+str(center)+' pixels')

    if cogret:
        return output,cog
    else:
        return output

#smoothing functions
def filterconvolve(data,filter,z=0):
    t=data*filter
    s=sum(np.ravel(t))
    if z:
        return abs(s)
    else:
        return s

def smooth_image(input,width):
    (ncols,nrows)=np.shape(input)    
    filter=np.ones((width,width),np.Float)/(width*width)
    hw=int(width/2)
    for i in range(hw,ncols-hw):
        for j in range(hw,nrows-hw):
            input[i,j]=filterconvolve[input[i-hw:i+hw+1,j-hw:j+hw+1],filter]
    return input    

def datasmooth(x,numpts):
    if numpts==0:
        return x
    numpts=int(numpts/2)
    x=np.array(x,typecode=np.Float)
    i=0
    smoo=[]
    while i<len(x):
        if i<numpts:
            sr=list(range(0,i+numpts+1,1))
        elif i>len(x)-numpts-1:
            sr=list(range(i-numpts,len(x),1))
        else:
            sr=list(range(i-numpts,i+numpts+1,1))
        temp=0
        for ind in sr:
            temp=temp+x[ind]
        smoo.append(temp/len(sr))
        i=i+1
    return np.array(smoo,typecode=np.Float)

#remove artifacts...
def remove_tomo_artifacts(image,image2=None,width=9,threshold=None,zingers=0,double_correlation=0,rings=0,diffraction=0):
    output=image
    (ncols,nrows)=np.shape(image)

    #zingers
    if zingers:
        if threshold==None: threshold=1.2
        ratio=image/smooth_image(image,width)
        #JOY Q
        zinger=np.where(ratio>threshold,1,0)
        for i in range(ncols):
            for j in range(nrows):
                if zinger[i,j]!=0:
                    try: output[i,j]=(output[i-2,j]+output[i+2,j])/2.
                    except: print('zinger error')
        print('Found '+str(sum(sum(zinger)))+' zingers in image')

    if double_correlation:
        pass

    if rings:
        ave=sum(image,1)/nrows
        diff=ave-datasmooth(ave,width)
        for i in range(nrows):
            output[:,i]=output[:,i]-diff

    if diffraction:
        if threshold==None: threshold=0.8
        for i in range(ncols):
            col=output[i,:]
            ratio=col/datasmooth(col,width)
            for j in range(len(ratio)-1):
                if ratio[j]<threshold:
                    try: col[j]=(col[j-2]+col[j+2])/2.
                    except: print('diff error')
            output[i,:]=col

    return output

#FILTER TYPES

def filter_none(x,d):
    y=np.zeros(len(x),np.Float)
    y[int(len(y)/2)]=1
    return y

def filter_ramlak(x,d):
    q=x
##    for i in range(len(q)-1):
##        if x[i]==0: q[i]=0.01
    y=(math.sin(math.pi*x/2))**2
    z=math.pi**2*x**2*d
    for i in range(len(q)):
        if z[i]==0:
            y[i]=1/(4.*d)
        else:
            y[i]=-y[i]/z[i]
    return (y)
##    y=x
##    for i in range(len(x)):
##        if x[i]==0: y[i]==1
##        elif x[i]%2==0: y[i]=0
##        else: y[i]=-4/(pi**2*x[i]**2)
##    return y

def filter_shepp_logan(x,d):
    d=math.pi**2*d*(1-4*x**2)
    for i in range(len(d)):
        if abs(d[i])<1e-6: d[i]=0.001
    return (2/d)

def filter_lp_cosine(x,d):
    return 0.5*(filter_ramlak(x-0.5,d)+filter_ramlak(x+0.5,d))

def filter_gen_hamming(x,d,alpha=0.5):
    return alpha*filter_ramlak(x,d)+((1-alpha)/2)*(filter_ramlak(x-1,d)+filter_ramlak(x+1,d))

#filter routine

def tomo_filter(image,filter_size=0,d=1,filter_name='SHEPP_LOGAN'):
    dims=np.shape(image)
    if not filter_size: filter_size=int(dims[0]/4.)
    nfilter=2*filter_size+1
    x=np.arange(nfilter,typecode=np.Float)-filter_size
    if string.upper(filter_name)=='GEN_HAMMING': filter=filter_gen_hamming(x,d)
    elif string.upper(filter_name)=='LP_COSINE': filter=filter_lp_cosine(x,d)
    elif string.upper(filter_name)=='RAMLAK': filter=filter_ramlak(x,d)
    elif string.upper(filter_name)=='NONE': filter=filter_none(x,d)
    else: filter=filter_shepp_logan(x,d)
    (ncols,nrows)=np.shape(image)
    s=image
    temp=np.zeros(ncols+2*nfilter,np.Float)
    for i in range(nrows):
        #pad with data from first and last columns
        temp[0:nfilter-1]=image[0,i]
        temp[nfilter+ncols-1:ncols+2*nfilter-1]=image[ncols-1,i]
        temp[nfilter:nfilter+ncols]=image[:,i]
        temp=np.convolve(temp,filter,mode=1)
        s[:,i]=temp[nfilter:nfilter+ncols]
    return s

##def dist(x,y):
##    a=np.zeros((x,y),np.Float)
##    for i in range(x):
##        for j in range(y):
##            i2=min([i,x-i])
##            j2=min([j,y-j])
##            a[i,j]=sqrt(i2**2+j2**2)
##    return a
##
##def shift(a,x,y):
##    x=int(x)
##    y=int(y)
##    for i in range(x):
##        pass
##    for j in range(y):
##        pass

#backprojection reconstruction
def backproject(sinogram,angles,bilinear=0,cubic=0):
    b=ImRadon.inv_radon(sinogram,theta=angles)
    return b

def fftrecon(sinogram,angles,name='SHEPP_LOGAN'):
    if string.upper(name)=='GEN_HAMMING': fn='hamm'
    elif string.upper(name)=='LP_COSINE': fn='hann'
    elif string.upper(name)=='RAMLAK': fn='ramp'
    elif string.upper(name)=='NONE': fn='ramp'
    else:fn='shepp'
    b=FFTtomo.recon_gridFFT(sinogram,fn,theta=angles)
    return b

def do_recon(arr,angles,method='BP',acc_values=0,air_values=10,auto_center=1,center=0,fluo=0,rings=0,ring_width=9,filter_name='SHEPP_LOGAN',filter_width=0,filter_d=1):
    #do data pre-processing
    t1=time.time()
    s=sinogram(arr,angles,acc_values=acc_values,air_values=air_values,auto_center=auto_center,center=center,fluo=fluo)
    t2=time.time()
    if rings: s=remove_tomo_artifacts(s,rings=rings,width=ring_width)
    t3=time.time()
    if method=='BP':
        im=tomo_filter(s,filter_name=filter_name,filter_size=filter_width,d=filter_d)
        t4=time.time()
        r=backproject(im,angles)
        t5=time.time()
    if method=='FT':
        r=fftrecon(s,angles,name=filter_name)
        t5=time.time()
    #normalize
    sum1=sum(arr)
    mom1=sum(sum1)/len(sum1)
    n1=mom1/sum(sum(r))
    print(mom1,sum(sum(r)),n1)
    r=r*n1
    print('Time to calculate sinogram: '+str(t2-t1))
    print('Time to remove artifacts: '+str(t3-t2))
    if method=='BP':
        print('Time to apply filter: '+str(t4-t3))
        print('Time to do backprojection reconstruction: '+str(t5-t4))
        if string.upper(filter_name) in ['LP_COSINE','GEN_HAMMING','RAMLAK']: r=-r
    if method=='FT':
        print('Time to do FFT reconstruction: '+str(t5-t3))
    return r        
        
if __name__ == '__main__':    
    ang=np.arange(0,180,0.25)
    a=np.ones((200,200),np.Float)
    for i in range(32,35):
        for j in range(40,55):
            a[i,j]=100. 
    b=ImRadon.radon(a,theta=ang)
    #ImRadon.imshow(b)
    c=do_recon(b,ang,fluo=0)
    ImRadon.imshow(c)