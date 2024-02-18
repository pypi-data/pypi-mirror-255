# NMF by alternative non-negative least squares using projected gradients
# Author: Chih-Jen Lin, National Taiwan University
# Python/numpy translation: Anthony Di Franco
# Translate to Numeric: Sam Webb

import numpy as np
from numpy import array
from sys import stdout
from time import time

def minimizer(A,x,dm):
    dx = np.reshape(A.shape[1],dm.shape[1])
    return np.ravel(np.square(np.dot(A,dx)-dm))


def sdot(x,y):
    #print x.shape
    #print y.shape
    #a=dot(x,y)
    #print a.shape
    return np.dot(x,y)

def norm(x):
    x=array(x)
    if len(x.shape)==2: return np.max(np.linalg.svd(x))
    else: return np.sqrt(np.dot(x,np.transpose(x)))


def fnorm(x):
    x=array(x)
    return np.sqrt(np.sum(np.diagonal(sdot(np.transpose(x),x))))

def all(x):
    for i in x:
        if not i: return 0
    return 1

def nmf(V,Winit,Hinit,tol=0.001,timelimit=60,maxiter=100,optout=0,verbose=0):
# (W,H) = nmf(V,Winit,Hinit,tol,timelimit,maxiter)
# W,H: output solution
# Winit,Hinit: initial solution
# tol: tolerance for a relative stopping condition
# timelimit, maxiter: limit of time and iterations
    W = Winit
    H = Hinit
    initt = time()
    HT=np.transpose(H)
    WT=np.transpose(W)

    gradW = sdot(W, sdot(H, HT)) - sdot(V, HT)
    gradH = sdot(sdot(WT, W), H) - sdot(WT, V)
    initgrad = fnorm(np.concatenate((gradW,np.transpose(gradH))))   #(r_[gradW, transpose(gradH)])
    if verbose: print('Init gradient norm ',initgrad) 
    tolW = np.max(0.001,tol)*initgrad
    tolH = tolW

    for iter in range(1,maxiter):
        # stopping condition
        gWc=np.where(np.logical_or(gradW<0,W>0),gradW,0)
        gHc=np.where(np.logical_or(gradH<0,H>0),gradH,0)
        #gHc=gHc*gradH
        #gWc=gWc*gradW
        projnorm = fnorm(np.concatenate((gWc,np.transpose(gHc))))               #r_[gradW[logical_or(gradW<0, W>0)],gradH[logical_or(gradH<0, H>0)]])
        if projnorm < tol*initgrad or time() - initt > timelimit: break
  
        (W, gradW, iterW) = nlssubprob(np.transpose(V),np.transpose(H),np.transpose(W),tolW,1000)
        W = np.transpose(W)
        gradW = np.transpose(gradW)
  
        if iterW==1: tolW = 0.1 * tolW

        if not optout:
            (H,gradH,iterH) = nlssubprob(V,W,H,tolH,1000)
            if iterH==1: tolH = 0.1 * tolH

        if iter % 10 == 0: stdout.write('.')

    if verbose: print('Iter = ',iter,' Final proj-grad norm ',projnorm)
    return (W,H,projnorm)

def nlssubprob(V,W,Hinit,tol,maxiter):
#H, grad: output solution and gradient
#iter: #iterations used
#V, W: constant matrices
#Hinit: initial solution
#tol: stopping tolerance
#maxiter: limit of iterations

    H = Hinit
    WtV = sdot(np.transpose(W), V)
    WtW = sdot(np.transpose(W), W) 

    alpha = 1
    beta = 0.1
    for iter in range(1,maxiter):  
        grad = sdot(WtW, H) - WtV
        gHc=np.where(np.logical_or(grad<0,H>0),grad,0)
        projgrad = fnorm(gHc)
        if projgrad < tol: break

        # search step size 
        for inner_iter in range(1,20):
            Hn = H - alpha*grad
            Hn = np.where(Hn > 0, Hn, 0)
            d = Hn-H
            gradd = np.sum(grad * d)
            dQd = np.sum(sdot(WtW,d) * d)
            try:
                suff_decr = 0.99*gradd + 0.5*dQd < 0
            except:
                stdout.write('!')
                suff_decr=0
            if inner_iter == 1:
                decr_alpha = not suff_decr
                Hp = H
            if decr_alpha: 
                if suff_decr:
                    H = Hn
                    break
                else:
                    alpha = alpha * beta
            else:
                if not suff_decr or all(Hp == Hn):
                    H = Hp
                    break
                else:
                    alpha = alpha/beta
                    Hp = Hn

        if iter == maxiter:
            print('Max iter in nlssubprob')
    return (H, grad, iter)


#some test
if __name__ == '__main__':    

    a=array([-8,-29,-45,-4,-16,-24])
    print(norm(a))

    w1 = array([[1,2,3],[4,5,6]])
    h1 = array([[1,2],[3,4],[5,6]])
    w2 = array([[1,1,3],[1,1,1]])
    h2 = array([[1,2],[3,4],[5,6]])

    v = sdot(w1,h1)

    #(wo,ho) = nmf(v, w2, h2, tol=0.0001, maxiter=100)
    #print wo
    #print ho


    print('\nSoln:')
    #Obs=Std*c
    v=array([.23,.50,1.33,1.1,1])
    std1=[.37,1.02,1.58,1.16,1.03]
    std2=[.27,.86,1.72,1.33,1.08]    
    std3=[.16,.32,.84,2.76,1.18]
    std4=[.10,.15,.26,1.73,1.11]

    std1=[.22,.62,1.46,1.08,1.05]
    std2=[.18,.45,1.43,1.29,1.1]    
    std3=[.12,.22,.49,3.3,1.2]
    std4=[.08,.12,.19,.99,1.19]



    std=array([std1,std2,std3,std4])
    g=array([.25,.25,.25,.25])
    g=np.resize(g,(1,4))
    v=np.resize(v,(1,5))
    print(sdot(g,std))
    print(v.shape,g.shape,std.shape)
    (c,s,e)=nmf(v,g,std,tol=0.001,maxiter=100)
    print(c)
    print(s)