

# Keywords: Spectral Angle Mapping (SAM), matrix factorization, convexity

# "In this paper, we focus on a type of constraint that restricts the
# representation to convex combinations of latent components."

# "Convexity constraints result in latent components that show interesting
# properties: First, the basis vectors are included in the data set and often
# reside on actual data points. Second, convexity constrained basis vectors
# usually correspond to the most extreme data points rather than to the most
# average ones."

# "Both these properties typically cause the basis elements to be readily
# interpretable even to non-experts."

# In the case of STXM analysis of zinc whites, the convexity restraint leads
# to endmembers that are representative of the most dissimilar particles.

# "For example, in geoscience it is also referred to as Endmember Detection
# and is used in the analysis of spectral images."

# Other endmember selection algorithms are O(n^2), whereas this SiVM is O(n)

# "We formulate the problem as a constrained matrix factorization problem
# aiming at minimizing the Frobenius norm between a data matrix and its
# approximation."

# "we then show that for convexity constrained factorizations minimizing the
# Frobenius norm is equivalent to maximizing the volume of a simplex whose
# vertices correspond to basis vectors."

# "Any increase of the volume of the k-simplex encoded in W will reduce the
# overall residual of the reconstruction. But why should maximizing the
# simplex volume be advanta- geous over minimizing the Frobenius norm? The
# answer is computational efficiency."

import sklearn
import sklearn.decomposition
import sklearn.manifold
import sklearn.cluster
import sklearn.tree
import numpy as np
import scipy
from scipy import ndimage as scnd
import struct
import time
import io

from PIL import Image
#import tifffile as tiff
from os import listdir

NMF = sklearn.decomposition.NMF

class Base:
    Comment = 'This is an empty place holder'
    Method_input = 'None'
    Method_output = 'None'
    Name = 'Empty:No Name'
    Method_endmemberout = 0

    class dummy:
        pass


class SiVM(Base):  # SiVM class; methods to preprocessed data and perform SiVM

    Method_input = 'D'
    Method_output = 'W'
    Name = 'Calc_W: SiVM'

    def __init__(self, X, num_bases=4, metric='euclidean', silent=True,
                 norm=['', [0, 0], [False, 0]], minimum=[False, [0, 0]],
                 gaussian=True, sigma=2.2):  # Mostly preprocessing setting
        self.silent = silent
        self._init = 'fastmap'
        self.Parameters = self.dummy()  # Refer to dummy function to initialize
        self.Parameters.num_bases = {'Name': 'Bases', 'type': 'int',
                                     'value': num_bases}
        self.Parameters.metric = {'Name': 'metric', 'type': 'list',
                                  'value': metric, 'list':
                                      list(sklearn.metrics.
                                           pairwise.distance_metrics().keys())}
        self.Parameters.norm = norm  # How to normalize?
        self.Parameters.minimum = minimum  # Subtract a minimum?
        self.Parameters.gaussian = gaussian  # Do gaussian filtering?
        self.Parameters.sigma = sigma  # Sigma of Gaussian filter?
        self.ppball = Base.dummy()
        self.ppball.ots = []
        self.ppball.data = [X]  # Contains data array

    def execute(self):
        pp = self.Parameters
        print(('SiVM for {} archetypes and {} matrix'.
              format(pp.num_bases['value'], pp.metric['value'])))
        self.metric = pp.metric['value']
        W = []
        H_labels = []
        W_indices = []
        self.ppball.ots.append('W')
        self.ppball.ots.append('W_indices')
        self.ppball.ots.append('H_labels')

        for d in self.ppball.data:  # d is the data
            self._num_bases = pp.num_bases['value']  # 4 by default
            if type(d) is np.ndarray:  # Regular data cube: one set
                self.data = np.abs(d.reshape(
                        d.shape[0], np.prod(d.shape[1:3])))
                self.IndexSample=np.arange(d.shape[1])
            self.IndexSampleSave = self.IndexSample.copy()
            self.preprocess(pp)  # Perform the preprocessing

            self.update_w()
            W.append(self.W)
            W_indices.append(self.select)
            H_labels.append(['Archetype '+str(i) for i in
                             range(pp.num_bases['value'])])

        self.ppball.W = W
        self.ppball.W_indices = W_indices
        self.ppball.H_labels = H_labels

    def preprocess(self, pp):

        self.datasave = self.data.copy()
        self.dataN = self.data.copy()
        self.SNR = ['']*self.data.shape[1]
        print("ppst",self.data.shape)

        if pp.minimum[0]:  # if True then subtract a minimum
            self.data = self.data - np.mean(self.data[
                    pp.minimum[1][0]:pp.minimum[1][1], :], axis=0)
        print("ppmin",self.data.shape)

        if pp.norm[0] in ['sum','peak']:
            for i in range(self.data.shape[1]):
                if pp.gaussian:  # Gaussian filter the data and calculate SNR
                    self.data[:, i] = scnd.gaussian_filter(
                            self.data[:, i], pp.sigma)
                    self.dataN[:, i] = self.dataN[:, i] - self.data[:, i]
                    self.SNR[i] = np.mean(self.data[:, i])/np.std(self.dataN[:, i])
                else:  # Only use the filtered data as a dummy variable
                    GaussianFiltered = scnd.gaussian_filter(
                            self.data[:, i], pp.sigma)
                    self.dataN[:, i] = self.dataN[:, i] - GaussianFiltered
                    self.SNR[i] = np.mean(GaussianFiltered)/np.std(
                            self.dataN[:, i])
            self.SNR = np.array(self.SNR)
        print("gauss",self.data.shape)
        
        if pp.norm[0] == 'peak':
            if pp.norm[2][0]:  # if True then select spectra based on SNR
                self.data = self.data[  # Select based on treshold sum
                        :, np.where(self.SNR > pp.norm[2][1])[0]]
                self.IndexSample = self.IndexSample[np.where(
                        self.SNR > pp.norm[2][1])[0]]
            self.means = np.mean(self.data[
                    pp.norm[1][0]:pp.norm[1][1], :], axis=0)
            self.data = self.data/self.means
        elif pp.norm[0] == 'sum':
            if pp.norm[2][0]:  # if True then select spectra based on SNR
                self.data = self.data[  # Select based on treshold sum
                        :, np.where(self.SNR > pp.norm[2][1])[0]]
                self.IndexSample = self.IndexSample[np.where(
                        self.SNR > pp.norm[2][1])[0]]
            self.sums = np.sum(self.data, axis=0)
            self.data = self.data/self.sums
        elif pp.norm[0] == 'mean':
            if pp.norm[2][0]:  # if True then select spectra based on SNR
                means = np.mean(self.data[
                        pp.norm[1][0]:pp.norm[1][1], :], axis=0)
                thresh=pp.norm[2][1]*np.mean(means)
                print('means/thresh',means.shape,thresh)
                self.data = self.data[  # Select based on treshold sum
                        :, np.where(means > thresh)[0]]
                self.IndexSample = self.IndexSample[np.where(
                        means > thresh)[0]]
                print('pren',self.data.shape)
            self.means = np.mean(self.data[
                    pp.norm[1][0]:pp.norm[1][1], :], axis=0)    
            self.data = self.data/self.means
            
        print("norm",self.data.shape)

    def _distfunc(self, data, vec):
        dist = sklearn.metrics.pairwise.distance_metrics()[
                self.metric](data.T, vec.T)[:, 0]
        return dist

    def _distance(self, idx):  # idx stands for index
        """compute distances of a specific data \
        point to all other samples"""

        if scipy.sparse.issparse(self.data):
            step = self.data.shape[1]
        else:
            step = 50000

        d = np.zeros((self.data.shape[1]))
        if idx == -1:
            # set vec to origin if idx=-1
            vec = np.zeros((self.data.shape[0], 1))
            if scipy.sparse.issparse(self.data):
                vec = scipy.sparse.csc_matrix(vec)
        else:
            vec = self.data[:, idx:idx+1]

        if not self.silent:
            print(('compute distance to node ' + str(idx)))

        # slice data into smaller chunks
        for idx_start in range(0, self.data.shape[1], step):
            if idx_start + step > self.data.shape[1]:
                idx_end = self.data.shape[1]
            else:
                idx_end = idx_start + step
#                print(idx_start,idx_end,d.shape,self.data.shape)
            d[idx_start:idx_end] = self._distfunc(
                self.data[:, idx_start:idx_end], vec)
            if not self.silent:
                print(('completed:' +
                      str(idx_end/(self.data.shape[1]/100.0)) + "%"))
        return d

    def init_sivm(self):
        self.select = []
        self.selectdist = []
        if self._init == 'fastmap':
            # Fastmap like initialization
            # set the starting index for fastmap initialization
            cur_p = 0

            # after 3 iterations the first "real" index is found
            for i in range(3):
                d = self._distance(cur_p)
                cur_p = np.argmax(d)

            # store maximal found distance, later used for "a" (->update_w)
            self._maxd = np.max(d)
            self.select.append(cur_p)
            self.selectdist.append(np.max(d))

        elif self._init == 'origin':
            # set first vertex to origin
            cur_p = -1
            d = self._distance(cur_p)
            self._maxd = np.max(d)
            self.select.append(cur_p)
            self.selectdist.append(np.max(d))

    def update_w(self):
        """ compute new W """
        EPS = 10**-8
        self.init_sivm()

        # initialize some of the recursively updated distance measures ....
        d_square = np.zeros((self.data.shape[1]))
        d_sum = np.zeros((self.data.shape[1]))
        d_i_times_d_j = np.zeros((self.data.shape[1]))
        distiter = np.zeros((self.data.shape[1]))
        a = np.log(self._maxd)
#        a_inc = a.copy()

        for l in range(1, self._num_bases):
            d = self._distance(self.select[l-1])

            # take the log of d (sually more stable that d)
            d = np.log(d + EPS)

            d_i_times_d_j += d * d_sum
            d_sum += d
            d_square += d**2
            distiter = d_i_times_d_j + a*d_sum - (l/2.0) * d_square

            # detect the next best data point
            self.select.append(np.argmax(distiter))
            self.selectdist.append(np.max(distiter))

            if not self.silent:
                print(('cur_nodes: ' + str(self.select)))
                print(('cur_dist: ' + str(self.selectdist)))

        # sort indices, otherwise h5py won't work
        self.W = self.data[:, np.sort(self.select)]

        # "unsort" it again to keep the correct order
        self.W = self.W[:, np.argsort(np.argsort(self.select))]
        print(('cur_nodes: ' + str(self.select)))
        print(('cur_dist: ' + str(self.selectdist)))
        print(('indices: '+ str(self.IndexSample[self.select])))

# Default SNR treshold 10 for STXM
# 041: 2-4, res
# 012: 1-4, res
# 143: 1-4, res
# 102: 1-4
# 013: 2-5, res
# 021: 2-4(5), res!

class calculateNNLS:
    def __init__(self,S,FileNames,NumEnergies):
        self.FileNames=FileNames
        self.NumEnergies=NumEnergies
        self.S=S
        
    def eval(self,num,Array):  #num=number of components to fit
           
        # Produces NNLS model for each spectrum from archetypes, saves corresp. maps #
        H = self.S.ppball.W[0][:,0:num].T  # Write the archetypes to array H
        H[np.where(H < 0)] = 0  # Set all negative archetype values to zero
        model = NMF(n_components=H.shape[0], init='random',
                    random_state=0, max_iter=500)  # Create an NMF model instance
        model.n_components_ = model.n_components
        model.components_ = H
        
        W = ['']*len(self.FileNames)  # W contains weights matrix for NNLS acc. to scipy
#        W_ = list(W) #.copy()  # W_ contains weights matrix for NNLS acc. to NMF method
        SSD = list(W) #.copy()
#        SSD_ = list(W)#.copy()
        Xg = list(W) #.copy()
        
        for j in range(len(self.FileNames)):  # Loop calculates NNLS models and saves maps
            #print ('ERRCHK3:',j,Array[j].shape,self.NumEnergies,np.prod(Array[j].shape[1:3]))
            X = Array[j].reshape(self.NumEnergies, np.prod(Array[j].shape[1:3])).T
        
            if self.S.Parameters.minimum[0]:  # if True then subtract a minimum
                X = (X.T -
                     np.mean(X[:, self.S.Parameters.minimum[1][0]:
                             self.S.Parameters.minimum[1][1]], axis=1)).T
        
            X = np.abs(X)  # No negatives for NNLS, helps in determining noise levels
        
#            W_[j] = model.transform(X)
#            Xm_ = np.matmul(W_[j], H)  # Spectra modelled with archetype fit
        
            W[j] = np.zeros([X.shape[0], H.shape[0]])
            Xm = np.zeros([X.shape[0], self.NumEnergies])  # Spectra modelled w/ archet. fit
            Xg[j] = Xm.copy()
            print(W[j].shape,X.shape,H.shape)
            for i in range(X.shape[0]):  # Fill in scipy NNLS weight mat. per spectrum
                W[j][i, :] = scipy.optimize.nnls(H.T, X[i, :])[0]  # Calc NNLS model
                Xg[j][i, :] = scnd.gaussian_filter(X[i, :], self.S.Parameters.sigma)
        
            Xm = np.matmul(W[j], H)  # Spectr modelled with archetype fit
        
            Xsum = np.sum(X, axis=1)
            Xsum = Xsum[Xsum < np.median(Xsum)]
            XsumH = np.histogram(Xsum, 20)
            AirI = np.where(Xsum < XsumH[1][list(
                    XsumH[0]).index(np.max(XsumH[0])) + 1])[0]  # Sel. below air tresh.
            AirSpectra = X[AirI, :]  # Select them from data
            AirF = Xg[j][AirI, :]  # Select them from filtered data
            AirM = Xm[AirI, :]  # Select them from SiVM-NNLS modelled data
        
            alpha = np.mean(np.sum((AirSpectra - AirM)**2, axis=1)/np.sum(
                    (AirSpectra - AirF)**2, axis=1))  # For explanation of alpha see: *
        
            SSD[j] = (np.sum((X - Xm)**2, axis=1) - alpha*np.sum(
                    (X - Xg[j])**2, axis=1))/np.sum((X - Xg[j])**2, axis=1)
#            SSD_[j] = (np.sum((X - Xm_)**2, axis=1) - alpha*np.sum(
#                    (X - Xg[j])**2, axis=1))/np.sum((X - Xg[j])**2, axis=1)
                
            Norm = max([np.sort(W[j][:, i], axis=0)[
                    int(-round(np.sqrt(len(W[j][:, i]))/5))]
                    for i in range(H.shape[0])])  # Makes archetype maps proportional
        
#            Norm_ = max([np.sort(W_[j][:, i], axis=0)[
#                    int(-round(np.sqrt(len(W[j][:, i]))/5))]
#                    for i in range(H.shape[0])])  # Makes archetype maps proportional
                
            NormResiduals = max([np.sort(SSD[j])[int(-round(np.sqrt(
                len(SSD[j]))/5))] for j in range(len(self.FileNames))])
#        NormResiduals_ = max([np.sort(SSD_[j])[int(-round(np.sqrt(
#                len(SSD_[j]))/5))] for j in range(len(FileNames))])

        
        print(num,NormResiduals)
        return W[0]
        
# * Estimates the alpha factor here for normalized residual estimation.

# Alpha is equal to the expected ratio between (the residual sum of squares of
# a pure noise spectrum relative to an NNLS archetype fit) and (the residual
# sum of squares of a pure noise spectrum relative to that spectrum after
# Gaussian filtering). It can be used to calculate the contributions to the
# residual sum of squares of a spectra relative to an endmember fit in terms of
# noise and deviation is spectral shape. This can then allow to normalize the
# residuals to optical density without excessively overestimating the spectral
# deviation of pure or high noise spectra. Alpha = 1.73, Sigma_alpha = 0.18




