import numpy as np
import spline

def congrid(a, newdims, method='linear', centre=0, minusone=0):
    '''Arbitrary resampling of source array to new dimension sizes.
    Currently only supports maintaining the same number of dimensions.
    To use 1-D arrays, first promote them to shape (x,1).
    
    Uses the same parameters and creates the same co-ordinate lookup points
    as IDL''s congrid routine, which apparently originally came from a VAX/VMS
    routine of the same name.

    method:
    neighbour - closest value from original data
    nearest and linear - uses n x 1-D interpolations using
                         scipy.interpolate.interp1d
    (see Numerical Recipes for validity of use of n 1-D interpolations)
    spline - uses ndimage.map_coordinates

    centre:
    True - interpolation points are at the centres of the bins
    False - points are at the front edge of the bin

    minusone:
    For example- inarray.shape = (i,j) & new dimensions = (x,y)
    False - inarray is resampled by factors of (i/x) * (j/y)
    True - inarray is resampled by(i-1)/(x-1) * (j-1)/(y-1)
    This prevents extrapolation one element beyond bounds of input array.
    '''
    if not a.dtype.char in [np.Float64, np.Float32]:
        a = a.astype(np.Float)

    m1 = int(minusone)
    ofs = int(centre) * 0.5
    old = a.shape 
    ndims = len( a.shape )
    if len( newdims ) != ndims:
        print ("[congrid] dimensions error. \n This routine currently only support \n rebinning to the same number of dimensions.")
        return None
    newdims = np.array( newdims, dtype=np.Float)
    dimlist = []

    if method == 'neighbour':
        for i in range( ndims ):
            base = np.indices(newdims)[i]
            dimlist.append( (old[i] - m1) / (newdims[i] - m1) \
                            * (base + ofs) - ofs )
        cd = np.array( dimlist ).round().astype(np.Int)
        newa = a[list( cd )]
        return newa

    elif method in ['nearest','linear']:
        # calculate new dims
        for i in range( ndims ):
            base = np.arange( newdims[i] )
            dimlist.append( (old[i] - m1) / (newdims[i] - m1)* (base + ofs) - ofs )
        # specify old dims
        olddims = [np.arange(i, typecode = np.Float) for i in list( a.shape )]

        # first interpolation - for ndims = any
##        mint = scipy.interpolate.interp1d( olddims[-1], a, kind=method )
##        newa = mint( dimlist[-1] )
##        interp=spline.Spline(olddims[-1],a)
##        newa=interp(dimlist[-1])
        newa=multispline(dimlist[-1],olddims[-1],a)

        trorder = [ndims - 1] + range( ndims - 1 )
        for i in range( ndims - 2, -1, -1 ):
            newa = np.transpose(newa,trorder )

##            interp=spline.Spline(olddims[i],newa)
##            newa=interp(dimlist[i])    
            newa=multispline(dimlist[i],olddims[i],newa)

##            mint = scipy.interpolate.interp1d( olddims[i], newa, kind=method )
##            newa = mint( dimlist[i] )

        if ndims > 1:
            # need one more transpose to return to original dimensions
            newa = np.transpose(newa, trorder )

        return newa
##    elif method in ['spline']:
##        oslices = [ slice(0,j) for j in old ]
##        oldcoords = np.ogrid[oslices]
##        nslices = [ slice(0,j) for j in list(newdims) ]
##        newcoords = np.mgrid[nslices]
##
##        newcoords_dims = range(np.rank(newcoords))
##        #make first index last
##        newcoords_dims.append(newcoords_dims.pop(0))
##        newcoords_tr = newcoords.transpose(newcoords_dims)
##        # makes a view that affects newcoords
##
##        newcoords_tr += ofs
##
##        deltas = (np.asarray(old) - m1) / (newdims - m1)
##        newcoords_tr *= deltas
##
##        newcoords_tr -= ofs
##
##        newa = scipy.ndimage.map_coordinates(a, newcoords)
##        return newa
    else:
        print ("Congrid error: Unrecognized interpolation type.\n", \
              "Currently only \'neighbour\', \'nearest\',\'linear\',", \
              "and \'spline\' are supported.")
        return None

def multispline(new,old,a):
    #1-D
    if len(a.shape)==1:
        interp=spline.Spline(old,a)
        newa=interp(new)  
    else: #presume 2-D
        #spline along rows
        newa=np.zeros((a.shape[0],len(new)),np.Float)
        for i in range(a.shape[0]):
            interp=spline.Spline(old,a[i,:])
            nn=interp(new)
            newa[i,:]=nn
##            print a.shape,len(new),len(old),len(nn),newa.shape
    return newa