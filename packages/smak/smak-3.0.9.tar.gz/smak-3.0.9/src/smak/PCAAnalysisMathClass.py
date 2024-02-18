#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 23:16:53 2023

@author: samwebb
"""
#standard
import math
import packaging.version as VRS
import random
import time
import tkinter

#third party
import numpy as np
import numpy.linalg as LinearAlgebra
import sklearn
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import FastICA, MiniBatchDictionaryLearning, NMF, PCA
import sklearn.metrics.pairwise as sklPairs
import sklearn.manifold as skmanifold


#local imports
import varimax
import sivm


if VRS.Version(sklearn.__version__)>VRS.parse("0.13.0"):
    print ('sklearn version > 0.13.0')
    from sklearn.decomposition import FactorAnalysis
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    sklHasFactorAnalysis=True
else:
    sklHasFactorAnalysis=False
    
if VRS.Version(sklearn.__version__)>=VRS.parse("0.17.0"):
    print ('sklearn version > 0.17.0')
    from sklearn import cluster as skcluster
    from sklearn import mixture as skmixture
    #import hdbscan
    sklHasAdvancedCluster=True
else:
    sklHasAdvancedCluster=False
    

print("thru sklearn -PCAMath")


#######################################
## PCA classes and functions
#######################################



def amnesic(i):
    n1=20.
    n2=500.
    m=1000.
    if i<n1:
        L=0.
    elif i>=n1 and i<n2:
        L=2.*(i-n1)/(n2-n1)
    else:
        L=2.+(i-n2)/m
    w1=(i-1-L)/i
    w2=(1+L)/i
    return [w1,w2]

def norm(v):
    return math.sqrt(sum(v**2))


def sortme(dat,ind):
    #sort columns
    dat=np.transpose(dat)
    ans=[]
    for i in ind:
        ans.append(dat[i,:])
    return np.transpose(ans)

def normc(m):
    [mr,mc]=m.shape
    m=m.astype(np.float32)
    if mr==1:
        n=np.ones((1,mc),dtype=np.float32)
    else:
        n=math.sqrt(np.ones(m.shape,dtype=np.float32)/sum(m*m))*m
    return n

def remmean(dat):
    meanval=np.mean(np.transpose(dat))
    meanval=np.reshape(meanval,(meanval.shape[0],1))                    
    onem=np.ones((1,dat.shape[1]))
    #newV=dat-meanval*onem
    dat=dat-meanval*onem
    #dat=np.transpose(dat)
    return [dat,meanval]

def ccipca(X,*args):
    (datadim,samplenum)=X.shape
    print(datadim,samplenum)
    vectornum=datadim
    repeating=1
    initn=2
    if len(args)==0:
        if datadim>samplenum:
            #error
            print('PCA error: Number of samples is less than the dimension -- choose number of eigenvectors to compute')
            return [0,0,0]
        V=X[:,0:vectornum]
    elif len(args)==1:
        k=args[0]
        if k>datadim:
            k=datadim
        vectornum=k
        V=X[:,0:vectornum]
    elif len(args)==2:
        k=args[0]
        iteration=args[1]
        if k>datadim:
            k=datadim
        vectornum=k
        V=X[:,0:vectornum]            
        repeating=iteration
    elif len(args)>=3:
        k=args[0]
        iteration=args[1]
        oldV=args[2]
        access=args[3]
        if datadim !=oldV.shape[0]:
            print('PCA error: dimensionality problem!')
            return [0,0,0]
        vectornum=oldV.shape[1]
        V=oldV
        repeating=iteration
        initn=access
    Vnorm=math.sqrt(sum(V**2))
    for eigenidx in range(vectornum):
        n=initn
        for iter in range(repeating):
            for i in range(samplenum):
                [w1,w2]=amnesic(n)
                n=n+1
                t1=w1*V[:,eigenidx]
                t2=w2*np.transpose(V[:,eigenidx])
                t3=np.dot(t2,X[:,i])
                t3=np.dot(t3,X[:,i])
                V[:,eigenidx]=t1+t3/Vnorm[eigenidx]
                del t1
                del t2
                del t3
                Vnorm[eigenidx]=norm(V[:,eigenidx])
        normedV=V[:,eigenidx]/Vnorm[eigenidx]
        vt=np.reshape(normedV,(normedV.shape[0],1))
        t1=np.dot(normedV,X)
        del normedV
        t2=vt*t1
        del vt
        del t1
        X=X-t2
        del t2
        print(str(eigenidx+1)+' components of '+str(vectornum))
        #X=X-(reshape(normedV,(normedV.shape[0],1))*matrixmultiply(normedV,X))
    D=math.sqrt(sum(V**2))
    I=np.argsort(-D)
    VS=sortme(V,I)
    VS=normc(VS)
    DS=np.sort(-D)
    DS=-DS
    #D=np.diag(D) #diagonalize?
    return [VS,DS]


class PCADataStructure:
    def __init__(self,rawdata,PCAcompMAXNO,imgwin,pcaft=None,dx=None,dy=None,zmxyi=None,cl=None,ml=None):
        self.PCArawdata=rawdata
        self.PCAcompMAXNO=PCAcompMAXNO
        self.imgwin = imgwin
        self.pcaFileTypes=pcaft
        
        #sivm specific
        self.zmxyi=zmxyi  #self.maindisp.zmxyi
        self.dx=dx        #self.mapdata.data.get(0)[::-1,:]
        self.dy=dy        #aelf.mapdata.data.get(1)[::-1,:]
        self.ml=ml
        self.cl=cl
        
        #result structure
        self.PCAuevect=None
        self.PCAeval=None
        self.PCAprop=None
        self.PCAevect=None
        
        self.PCAKcluster=None

    def donewPCA(self,pcatype='sPCA',MCA=False):
        if pcatype != 'SiVM' and self.imgwin is None:
            self.PCAcompMAXNO=self.cl
        #reshape
        #datmat=np.transpose(self.PCArawdata)
        (datadim,samplenum)=np.transpose(self.PCArawdata).shape
        
        if pcatype == 'SiVM': self.PCAcompMAXNO = datadim
        
        #del self.PCArawdata
        #self.PCAdatatype='none'
        print('enter pca',pcatype)
        
        if pcatype=='CCIPCA':

            print('subing...')
            [self.PCArawdataT,samplemean]=remmean(np.transpose(self.PCArawdata))            
            
            print('enter ccipca')

            [V,D]=ccipca(self.PCArawdataT,self.PCAcompMAXNO)        
         
            evalmat=np.diag(D)
            evect=np.dot(V,evalmat)
            invvect=LinearAlgebra.inv(evect)#generalized_inverse(evect)
            weight=np.dot(invvect,self.PCArawdataT)
            
            print(V.shape,D.shape,weight.shape)
    
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(weight)#weight X
            self.PCAevect=evect #V

        if pcatype=='sPCA':
            pca=PCA(n_components=self.PCAcompMAXNO)
            X=np.transpose(pca.fit_transform((self.PCArawdata)))
            V=pca.components_
            D=pca.explained_variance_        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            if MCA:
                self.PCAevect=np.transpose(V)
                self.PCAuevect=np.transpose(V)
            else:
                self.PCAevect=V

        if pcatype=='FA':
            pca=FactorAnalysis(n_components=self.PCAcompMAXNO)
            X=np.transpose(pca.fit_transform((self.PCArawdata)))
            V=pca.components_
            D=pca.noise_variance_        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            self.PCAevect=V
            if MCA:
                self.PCAevect=np.transpose(V)
                self.PCAuevect=np.transpose(V)
            else:
                self.PCAevect=V
                
        if pcatype=='NMF':
            pca=NMF(n_components=self.PCAcompMAXNO)
            X=np.transpose(pca.fit_transform((self.PCArawdata)))
            V=pca.components_
            D=np.ones(samplenum)        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            if MCA:
                self.PCAevect=np.transpose(V)
                self.PCAuevect=np.transpose(V)
            else:
                self.PCAevect=V

        if pcatype=='Dictionary':
            if MCA:
                nc=self.PCAcompMAXNO
            else: 
                nc=self.PCAcompMAXNO-1
            pca=MiniBatchDictionaryLearning(n_components=nc,alpha=1.0,fit_algorithm="lars",transform_algorithm="lasso_cd")
            X=np.transpose(pca.fit_transform((self.PCArawdata)))
            V=pca.components_
            D=np.ones(samplenum)

            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            if MCA:
                self.PCAevect=np.transpose(V)
                self.PCAuevect=np.transpose(V)
            else:
                self.PCAevect=V

        if pcatype=='SiVM':
            print(self.PCArawdata.shape)

            if self.imgwin is not None:
                cl=tkinter.simpledialog.askinteger('SiVM','Number of Endmembers',parent=self.imgwin,initialvalue=self.PCAcompMAXNO)        
                if cl<2 or cl>self.PCAcompMAXNO*2: cl=self.PCAcompMAXNO*2

                ml=tkinter.simpledialog.askfloat('SiVM','Factoring Mean Fraction',parent=self.imgwin,initialvalue=1.0)        
                if ml<0: ml=0
            else:
                cl = self.cl
                ml = self.ml
            cl+=1            

            pca=sivm.SiVM(np.transpose(self.PCArawdata), cl, 'euclidean', silent=True,  # Create instance of SiVM
                norm=['mean', [0, 100], [True, ml]],
                minimum=[False, [0, 100]], gaussian=True, sigma=3)
            pca.execute()   
                       
            print ('sivm',self.PCAcompMAXNO)
            R=sivm.calculateNNLS(pca,[1],self.PCAcompMAXNO)
            fast=1
            if not fast:
                for m in range(2,cl):
                    X=R.eval(m,[np.transpose(self.PCArawdata)])
            else:
                #print ('ERRCHK2:',cl-1,self.PCArawdata.shape)
                X=R.eval(cl-1,[np.transpose(self.PCArawdata)])
            #X=np.transpose(pca.fit_transform((self.PCArawdata)))
            V=pca.ppball.W[0]   #pca.components_
            
            if self.pcaFileTypes=='Single File':
                emind=pca.IndexSample[pca.select]
                #dx=self.mapdata.data.get(0)[::-1,:]#[::-1,:,dataind]
                if self.zmxyi[0:4]!=[0,0,-1,-1]:    
                    self.dx=self.dx[self.zmxyi[1]:self.zmxyi[3],self.zmxyi[0]:self.zmxyi[2]]            
                #dy=self.mapdata.data.get(1)[::-1,:]#[::-1,:,dataind]
                if self.zmxyi[0:4]!=[0,0,-1,-1]:    
                    self.dy=self.dy[self.zmxyi[1]:self.zmxyi[3],self.zmxyi[0]:self.zmxyi[2]]            
                nx=np.ravel(self.dx)[emind]
                ny=np.ravel(self.dy)[emind]
                D=[nx,ny]
            else:
                D=[]
        
            #print V.shape,D.shape,X.shape        
        
            self.PCAuevect=np.transpose(V)
            self.PCAeval=D
    
            self.PCAprop=X#np.transpose(X)#weight X
            self.PCAevect=np.transpose(V)
            print(self.PCAprop.shape)


        if pcatype=='FastICA':
            pca=FastICA(n_components=self.PCAcompMAXNO)
            X=np.transpose(pca.fit_transform((self.PCArawdata)))
            V=pca.components_
            D=np.ones(samplenum)        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            if MCA:
                self.PCAevect=np.transpose(V)
                self.PCAuevect=np.transpose(V)
            else:
                self.PCAevect=V

        if pcatype=='LDA':
            
            self.PCA_cluster_classifier=None
            self.getChannelNameViaDialog()            
            
            pca=LinearDiscriminantAnalysis(n_components=int(max(self.PCA_cluster_classifier)+1))
            print("LDA input",self.PCArawdata.shape,self.PCA_cluster_classifier.shape,max(self.PCA_cluster_classifier))
            ##need y classifier here!
            X=np.transpose(pca.fit_transform(self.PCArawdata,self.PCA_cluster_classifier))
            V=pca.means_
            D=np.ones(samplenum)        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            if MCA:
                self.PCAevect=np.transpose(V)
                self.PCAuevect=np.transpose(V)
            else:
                self.PCAevect=V
                
        if pcatype=='Kmeans':
            
            if self.imgwin is not None:
                cl=tkinter.simpledialog.askinteger('K Mean Clustering','Number of clusters',parent=self.imgwin,initialvalue=self.PCAcompMAXNO)        
                if cl<2: cl=self.PCAcompMAXNO
            else:
                cl = self.PCAcompMAXNO
                
            pca=MiniBatchKMeans(n_clusters=cl, tol=1e-3, batch_size=20,max_iter=50)
            X=np.transpose(pca.fit_transform((self.PCArawdata)))
            V=pca.cluster_centers_
            D=np.ones(samplenum)        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            self.PCAevect=V

            self.PCAKcluster=pca.labels_ 

##['','','','Ward','Birch','DBSCAN','AggCluster']:

        if pcatype=='AggCluster':

            if self.imgwin is not None:
                cl=tkinter.simpledialog.askinteger('Agglomerative Clustering','Number of clusters',parent=self.imgwin,initialvalue=self.PCAcompMAXNO)   
            else:
                cl = self.PCAcompMAXNO
            #if cl<2 or cl>self.PCAcompMAXNO: cl=self.PCAcompMAXNO            
            if cl<2: cl=2           
            pca=skcluster.AgglomerativeClustering(n_clusters=cl,linkage='average')
            X=np.transpose(pca.fit_predict((self.PCArawdata)))
            V=pca.labels_ 
            D=np.ones(samplenum)        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            self.PCAevect=V

            self.PCAKcluster=pca.labels_ 

        if pcatype=='Ward':

            if self.imgwin is not None:
                cl=tkinter.simpledialog.askinteger('Ward Agglomerative Clustering','Number of clusters',parent=self.imgwin,initialvalue=self.PCAcompMAXNO)        
            else:
                cl=self.PCAcompMAXNO
            #if cl<2 or cl>self.PCAcompMAXNO: cl=self.PCAcompMAXNO            
            if cl<2: cl=2           
            pca=skcluster.AgglomerativeClustering(n_clusters=cl,linkage='ward')
            X=np.transpose(pca.fit_predict((self.PCArawdata)))
            V=pca.labels_ 
            D=np.ones(samplenum)        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            self.PCAevect=V

            self.PCAKcluster=pca.labels_ 

        if pcatype=='Birch':

            if self.imgwin is not None:
                cl=tkinter.simpledialog.askinteger('Birch Clustering','Number of clusters',parent=self.imgwin,initialvalue=self.PCAcompMAXNO)        
            else:
                cl = self.PCAcompMAXNO
            #if cl<2 or cl>self.PCAcompMAXNO: cl=self.PCAcompMAXNO            
            if cl<2: cl=2          
            pca=skcluster.Birch(n_clusters=cl)
            X=np.transpose(pca.fit_predict((self.PCArawdata)))
            V=pca.subcluster_centers_ 
            D=np.ones(samplenum)        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            self.PCAevect=V

            self.PCAKcluster=pca.labels_ 

        if pcatype=='Spectral':

            if self.imgwin is not None:
                cl=tkinter.simpledialog.askinteger('Spectral Clustering','Number of clusters',parent=self.imgwin,initialvalue=self.PCAcompMAXNO)        
            else:
                cl = self.PCAcompMAXNO
            #if cl<2 or cl>self.PCAcompMAXNO: cl=self.PCAcompMAXNO            
            if cl<2: cl=2         
            pca=skcluster.SpectralClustering(n_clusters=cl)
            X=np.transpose(pca.fit_predict((self.PCArawdata)))
            V=pca.affinity_matrix_
            D=np.ones(samplenum)        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            self.PCAevect=V

            self.PCAKcluster=pca.labels_ 

        if pcatype=='Gaussian':

            if self.imgwin is not None:
                cl=tkinter.simpledialog.askinteger('Gaussian Mixtures','Number of mixtures',parent=self.imgwin,initialvalue=self.PCAcompMAXNO)        
            else:
                cl = self.PCAcompMAXNO
                #if cl<2 or cl>self.PCAcompMAXNO: cl=self.PCAcompMAXNO            
            if cl<2: cl=2
            pca=skmixture.GaussianMixture(n_components=cl)
            X=np.transpose(pca.fit(self.PCArawdata))
            V=pca.covariances_
            D=np.ones(samplenum)        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            self.PCAevect=V

            self.PCAKcluster=pca.predict(self.PCArawdata)

        if pcatype=='AffProp':
            
            if self.imgwin is not None:
                cl=tkinter.simpledialog.askfloat('Affinity Clustering','Damping Factor',parent=self.imgwin,initialvalue=0.8)        
            else:
                cl = self.ml
                
            if cl<0.5: cl=0.5
            if cl>1: cl=0.99
            print('damping',cl)
            pca=skcluster.AffinityPropagation(damping=cl)
            X=np.transpose(pca.fit_predict((self.PCArawdata)))
            V=pca.cluster_centers_
            D=np.ones(samplenum)        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            self.PCAevect=V

            self.PCAKcluster=pca.labels_ 

        # if pcatype=='DBSCAN':
            
        #     #pca=skcluster.DBSCAN(min_samples=15)
        #     pca=hdbscan.HDBSCAN(min_cluster_size=10)
        #     X=np.transpose(pca.fit_predict(self.PCArawdata))
        #     V=np.ones(samplenum)#pca.components_
        #     D=np.ones(samplenum)        
        
        #     print(V.shape,D.shape,X.shape)        
        
        #     self.PCAuevect=V
        #     self.PCAeval=D
    
        #     self.PCAprop=np.transpose(X)#weight X
        #     self.PCAevect=V

        #     self.PCAKcluster=pca.labels_ 
            

        if pcatype=='MeanSh':
            
            pca=skcluster.MeanShift()
            X=np.transpose(pca.fit_predict((self.PCArawdata)))
            V=pca.cluster_centers_
            D=np.ones(samplenum)        
        
            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            self.PCAevect=V

            self.PCAKcluster=pca.labels_ 

        if pcatype=='Iso':
            
            pca=skmanifold.Isomap(n_components=2)
            X=np.transpose(pca.fit_transform((self.PCArawdata)))
            V=np.ones((2,self.PCArawdata.shape[0]))
            D=np.ones(samplenum)

            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            if MCA:
                self.PCAevect=np.transpose(V)
                self.PCAuevect=np.transpose(V)
            else:
                self.PCAevect=V

        if pcatype=='MDS':
            
            pca=skmanifold.MDS(n_components=2)
            X=np.transpose(pca.fit_transform((self.PCArawdata)))
            V=np.ones((2,self.PCArawdata.shape[0]))
            D=np.ones(samplenum)

            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            if MCA:
                self.PCAevect=np.transpose(V)
                self.PCAuevect=np.transpose(V)
            else:
                self.PCAevect=V

        if pcatype=='tSNE':
            
            pca=skmanifold.TSNE(n_components=2)
            X=np.transpose(pca.fit_transform((self.PCArawdata)))
            V=np.ones((2,self.PCArawdata.shape[0]))
            D=np.ones(samplenum)

            print(V.shape,D.shape,X.shape)        
        
            self.PCAuevect=V
            self.PCAeval=D
    
            self.PCAprop=np.transpose(X)#weight X
            if MCA:
                self.PCAevect=np.transpose(V)
                self.PCAuevect=np.transpose(V)
            else:
                self.PCAevect=V

            
        print('done')
