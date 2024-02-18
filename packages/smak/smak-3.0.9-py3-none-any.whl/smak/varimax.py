
#Varimax matrix rotation
#Coded in Python by Sam Webb in 2003 
#Adapted from MATLAB code modified by Tevor Park in 2002 from original code by J.O. Ramsay
#
import math

import numpy as np


def angle(z):
    a=z.real
    b=z.imag
    return math.arctan2(b,a)

def var(z):
    s=np.std(z)
    return s**2

def vcomplex(a,b):
    return a+b*1j

def varimax(amat,target_basis=0):

    MAX_ITER=50
    EPSILON=1e-10
    
    amatd=amat.shape
    #make sure the problem is 2D
    if len(amatd)!=2:
        raise ValueError('AMAT must be 2-dimensional')
    n=amatd[0]
    k=amatd[1]
    rotm=math.identity(k)*1.0
    #if math.singular
    if k==1:
        return
    #error check target_basis
    if target_basis!=0:
        if len(target_basis.shape)!=2:
            raise ValueError('TARGET_BASIS must be 2-dimensional')
        if math.alltrue(target_basis.shape==(n,n)):
            amat=np.linalg.solve(target_basis,amat)
        else:
            raise ValueError('TARGET_BASIS must be a basis for the column space')
    else:
        target_basis=math.identity(n)*1.0

    #on to the guts
    varnow=sum(var(amat**2))
    not_converged=1
    iter=0
    while not_converged and iter<MAX_ITER:
        for j in range(0,k-1):
            for l in range(j+1,k):
                #find optimal planar rotation angle for column j,l
                #break expression into parts
                c1=vcomplex(amat[:,j],amat[:,l])
                c1=n*sum(c1**4)
                c2=vcomplex(amat[:,j],amat[:,l])
                c2=sum(c2**2)
                phi_max=angle(c1-c2**2)/4
                sub_rot=np.array([[math.cos(phi_max),-math.sin(phi_max)],[math.sin(phi_max),math.cos(phi_max)]])
                atemp=math.take(amat,(j,l),1)
                rtemp=math.take(rotm,(j,l),1)
                atemp=math.matrixmultiply(atemp,sub_rot)
                rtemp=math.matrixmultiply(rtemp,sub_rot)
                math.put(amat,list(range(j,n*k,k)),atemp[:,0])
                math.put(amat,list(range(l,n*k,k)),atemp[:,1])
                math.put(rotm,list(range(j,k*k,k)),rtemp[:,0])
                math.put(rotm,list(range(l,k*k,k)),rtemp[:,1])
        varold=varnow
        varnow=sum(var(amat**2))
        if varnow==0:
            return
        not_converged=((varnow-varold)/varnow > EPSILON)
        iter=iter+1
    if iter>=MAX_ITER:
        print('WARNING: Maximum number of iterations exceeded in varimax rotation')
    opt_amat=math.matrixmultiply(target_basis,amat)
    print("Total varimax iterations: "+str(iter))
    return rotm,opt_amat

