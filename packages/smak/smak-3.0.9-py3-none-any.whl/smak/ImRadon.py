#standard
import math
import os
import string
import types


#third party
from PIL import Image
import numpy as np


try:
    ImageCommand = Image.frombytes
except:
    ImageCommand = Image.fromstring

def iscomplexobj(x):
    return np.asarray(x).dtype.char in ['F', 'D']

# Returns a byte-scaled image
def bytescale(data, cmin=None, cmax=None, high=255, low=0):
    data=np.array(data)
    if data.dtype.char is np.uint8: #UnsignedInt8:
        return data
    high = high - low
    if cmin is None:
        cmin = min(np.ravel(data))
    if cmax is None:
        cmax = max(np.ravel(data))
    scale = high *1.0 / (cmax-cmin or 1)
    bytedata = ((data*1.0-cmin)*scale + 0.4999).astype(np.uint8) #UnsignedInt8)
    low=np.array(low,dtype=np.uint8)
    return bytedata + low

def imread(name,flatten=0):
    """Read an image file from a filename.

    Optional arguments:

     - flatten (0): if true, the image is flattened by calling
convert('F') on
     the resulting image object.  This flattens the color layers into a
single
     grayscale layer.
    """

    im = Image.open(name)
    return fromimage(im,flatten=flatten)


def imsave(name, arr):
    """Save an array to an image file.
    """
    im = toimage(arr)
    im.save(name)
    return

def fromimage(im, flatten=0):
    """Takes a PIL image and returns a copy of the image in a numpy container.
    If the image is RGB returns a 3-dimensional array:  arr[:,:,n] is each channel

    Optional arguments:

    - flatten (0): if true, the image is flattened by calling convert('F') on
    the image object before extracting the numerical data.  This flattens the
    color layers into a single grayscale layer.  Note that the supplied image
    object is NOT modified.
    """
    assert Image.isImageType(im), "Not a PIL image."
    if flatten:
        im = im.convert('F')
    mode = im.mode
    adjust = 0
    if mode == '1':
        im = im.convert(mode='L')
        mode = 'L'
        adjust = 1
    str = im.tobytes()
    type = np.uint8 #UnsignedInt8
    if mode == 'F':
        type = np.float32  #Float32
    elif mode == 'I':
        type = np.int32 #Int32
    elif mode == 'I;16':
        type = np.int16 #Int16
    arr = np.frombuffer(str,dtype=type)
    shape = list(im.size)
    shape.reverse()
    if mode == 'P':
        arr.shape = shape
        if im.palette.rawmode != 'RGB':
            print ("Warning: Image has invalid palette.")
            return arr
        pal = np.frombuffer(im.palette.data,dtype=type)
        N = len(pal)
        pal.shape = (int(N/3.0),3)
        return arr, pal
    if mode in ['RGB','YCbCr']:
        shape += [3]
    elif mode in ['CMYK','RGBA']:
        shape += [4]
    arr.shape = shape
    if adjust:
        arr = (arr != 0)
    return arr

_errstr = "Mode is unknown or incompatible with input array shape."
def toimage(arr,high=127,low=0,cmin=None,cmax=None,pal=None,
            mode=None,channel_axis=None,skip=0):
    """Takes a numpy array and returns a PIL image.  The mode of the
    PIL image depends on the array shape, the pal keyword, and the mode
    keyword.

    For 2-D arrays, if pal is a valid (N,3) byte-array giving the RGB values
    (from 0 to 255) then mode='P', otherwise mode='L', unless mode is given
    as 'F' or 'I' in which case a float and/or integer array is made

    For 3-D arrays, the channel_axis argument tells which dimension of the
      array holds the channel data.
    For 3-D arrays if one of the dimensions is 3, the mode is 'RGB'
      by default or 'YCbCr' if selected.

    The numpy array must be either 2 dimensional or 3 dimensional.
    """
    data = np.asarray(arr)
    if iscomplexobj(data):
        raise ValueError ("Cannot convert a complex-valued array.")
    shape = list(data.shape)
    valid = len(shape)==2 or ((len(shape)==3) and ((3 in shape) or (4 in shape)))
    assert valid, "Not a suitable array shape for any mode."
    if len(shape) == 2:
        shape = (shape[1],shape[0]) # columns show up first
        if mode == 'F':
            data32 = data.astype(float)
            image = ImageCommand(mode,shape,data32.tostring())
            return image
        if mode in [None, 'L', 'P']:
            if not skip: bytedata = bytescale(data,high=high,low=low,cmin=cmin,cmax=cmax)
            else: bytedata=data
            image = ImageCommand('L',shape,bytedata.tostring())
            if pal is not None:
                image.putpalette(np.asarray(pal,dtype=np.uint8).tostring())
                # Becomes a mode='P' automagically.
            elif mode == 'P':  # default gray-scale
                pal = np.arange(0,256,1,dtype=np.uint8)[:,np.newaxis] * np.ones((3,),dtype=np.uint8)[np.newaxis,:]
                image.putpalette(np.asarray(pal,dtype=np.uint8).tostring())
            return image
        if mode == '1':  # high input gives threshold for 1
            bytedata = (data > high)
            image = ImageCommand('1',shape,bytedata.tostring())
            return image
        if cmin is None:
            cmin = min(np.ravel(data))
        if cmax is None:
            cmax = max(np.ravel(data))
        data = (data*1.0 - cmin)*(high-low)/(cmax-cmin) + low
        
        if mode == 'I':
            data32 = data.astype(np.int32)
            image = ImageCommand(mode,shape,data32.tostring())
        else:
            raise ValueError (_errstr)
        return image

    # if here then 3-d array with a 3 or a 4 in the shape length.
    # Check for 3 in datacube shape --- 'RGB' or 'YCbCr'
    if channel_axis is None:
        if (3 in shape):
            ca = np.nonzero(np.asarray(shape) == 3)[0][0]
        else:
            ca = np.nonzero(np.asarray(shape) == 4)
            if len(ca):
                ca = ca[0]
            else:
                raise ValueError ("Could not find channel dimension.")
    else:
        ca = channel_axis

    print (ca,shape,channel_axis)
    numch = shape[ca]
    if numch not in [3,4]:
        raise ValueError ("Channel axis dimension is not valid.")

    bytedata = bytescale(data,high=high,low=low,cmin=cmin,cmax=cmax)
    if ca == 2:
        strdata = bytedata.tostring()
        shape = (shape[1],shape[0])
    elif ca == 1:
        strdata = np.transpose(bytedata,(0,2,1)).tostring()
        shape = (shape[2],shape[0])
    elif ca == 0:
        strdata = np.transpose(bytedata,(1,2,0)).tostring()
        shape = (shape[2],shape[1])
    if mode is None:
        if numch == 3: mode = 'RGB'
        else: mode = 'RGBA'

    if mode not in ['RGB','RGBA','YCbCr','CMYK']:
        raise ValueError (_errstr)

    if mode in ['RGB', 'YCbCr']:
        assert numch == 3, "Invalid array shape for mode."
    if mode in ['RGBA', 'CMYK']:
        assert numch == 4, "Invalid array shape for mode."

    # Here we know data and mode is coorect
    image = ImageCommand(mode, shape, strdata)#.astype(np.uint8))
    return image

def imrotate(arr,angle,interp='bilinear',mode=None):
    """Rotate an image counter-clockwise by angle degrees.

    Interpolation methods can be:
        'nearest' :  for nearest neighbor
        'bilinear' : for bilinear
        'cubic' or 'bicubic' : for bicubic
    """
    arr = np.asarray(arr)
    func = {'nearest':0,'bilinear':2,'bicubic':3,'cubic':3}
    im = toimage(arr,mode=mode)
    im = im.rotate(angle,resample=func[interp])
    return fromimage(im)



def imshow(arr):
    """Simple showing of an image through an external viewer.
    """
    im = toimage(arr)
    if (len(arr.shape) == 3) and (arr.shape[2] == 4):
        try:
            im.save('/tmp/scipy_imshow.png')
            if os.system("(xv /tmp/scipy_imshow.png; rm -f/tmp/scipy_imshow.png)&"):
                raise RuntimeError
            return
        except:
            print ("Warning: Alpha channel may not be handled correctly.")

    im.show()
    return

def radon(arr,theta=None):
    if theta is None:
        theta = np.arange(180)
    s = np.zeros((arr.shape[1],len(theta)), float)
    k = 0
    for th in theta:
        im = imrotate(arr,-th)
        s[:,k] = sum(im,axis=0)
        k += 1
    return s   

def inv_radon(arr,theta=None):
    if theta is None:
        theta = np.arange(arr.shape[1])
    th = (math.pi/180)*theta

    #set up the image
    m = arr.shape[1]
    n = arr.shape[0]-1
    inv = np.zeros( (n, n), float)

    #set up x and y matices
    midindex = (n+1)/2
    xy = np.indices((n,n))+1
    #JOY Q
    xy = array(xy,typecode=np.int32)
    xpr = xy[1]-(n+1)/2
    ypr = xy[0]-(n+1)/2

    for l in range(len(theta)):
        filtrindex = array(xpr*math.sin(th[l])-ypr*math.cos(th[l])+midindex)
        fi=np.ravel(filtrindex)
        fi = list(map(round,fi))
        fi = list(map(int,fi))
        filtrindex=np.reshape(fi,np.shape(filtrindex))
        inva=np.np.zeros((n,n),float)
        spota=np.where((filtrindex > 0) & (filtrindex <= n),1,0)
        ##newfiltindex=where((filtrindex > 0) & (filtrindex <= n),filtrindex,0)
        ##fir=ravel(filtrindex)
        ##spotar=ravel(spota)
        ##newfiltindex=take(fir,spotar*np.arange(len(spotar)))
        for i in range(n):
            for j in range(n):
                if spota[i,j]:
                    inva[i,j]=arr[filtrindex[i,j],l]
                    
        ##ni=ravel(newfiltindex)
        ##ni=np.array(map(int,ni))
        ##newfiltindex=reshape(ni,shape(newfiltindex))
        ##inva[spota]=arr[newfiltindex[:],l]              ###
        inv=inv+inva
    return inv/m

#test code
if __name__ == '__main__':   
    a=np.zeros((50,50),float)
    for i in range(12,15):
        for j in range(20,25):
            a[i,j]=100. 
    b=radon(a)
    print((b.shape))
    imshow(b)
    c=inv_radon(b)
    imshow(c)
