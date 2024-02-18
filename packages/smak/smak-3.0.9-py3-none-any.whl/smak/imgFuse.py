# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 09:01:56 2020

@author: samwebb
"""

import pywt
import math
import numpy as np
from skimage.transform import resize

def fuseCoeff(cooef1, cooef2, method):

    if (method == 'mean'):
        cooef = (cooef1 + cooef2) / 2
        #cooef = cooef1
    elif (method == 'min'):
        cooef = np.minimum(cooef1,cooef2)
    elif (method == 'max'):
        cooef = np.maximum(cooef1,cooef2)
    else:
        cooef = []

    return cooef
    
#FUSION_METHOD = 'mean' # Can be 'min' || 'max || anything you choose according theory
def doFuse(I1,I2,FUSION_METHOD):

    inputshape = I1.shape
    next2 = max(math.ceil(math.log(inputshape[0],2)),math.ceil(math.log(inputshape[1],2)))

    print(inputshape,next2)

    def1 = int(math.pow(2,next2)-inputshape[0])
    def2 = int(math.pow(2,next2)-inputshape[1])
    I1=np.pad(I1,((0,def1),(0,def2)), mode='constant')
    I2=np.pad(I2,((0,def1),(0,def2)), mode='constant')

    ## Fusion algo
    # First: Do wavelet transform on each image
    wavelet = 'db1'
    #cooef1 = pywt.wavedec2(I1[:,:], wavelet)
    #cooef2 = pywt.wavedec2(I2[:,:], wavelet)
    
    level = pywt.swt_max_level(I1.shape[1])

#    cooef1 = pywt.wavedec2(I1[:,:], wavelet)
#    cooef2 = pywt.wavedec2(I2[:,:], wavelet)
    cooef1 = pywt.swt2(I1[:,:], wavelet, level=level)
    cooef2 = pywt.swt2(I2[:,:], wavelet, level=level)

    # Second: for each level in both image do the fusion according to the desire option
    fusedCooef = []
    for i in range(len(cooef1)):
    
        # The first values in each decomposition is the apprximation values of the top level

             
            c0 = fuseCoeff(cooef1[i][0],cooef2[i][0],'mean')
    
    
            # For the rest of the levels we have tupels with 3 coeeficents
            c1 = fuseCoeff(cooef1[i][1][0],cooef2[i][1][0],FUSION_METHOD)
            c2 = fuseCoeff(cooef1[i][1][1], cooef2[i][1][1], FUSION_METHOD)
            c3 = fuseCoeff(cooef1[i][1][2], cooef2[i][1][2], FUSION_METHOD)

            fusedCooef.append((c0,(c1,c2,c3)))
    
    # Third: After we fused the cooefficent we nned to transfor back to get the image
#    fusedImage = pywt.waverec2(fusedCooef, wavelet)
    fusedImage = pywt.iswt2(fusedCooef, wavelet)#(fusedCooef, wavelet)    
    #print fusedCooef == cooef1
    # Forth: normmalize values to be in uint8
    #fusedImage = np.multiply(np.divide(fusedImage - np.min(fusedImage),(np.max(fusedImage) - np.min(fusedImage))),255)
    #fusedImage = fusedImage.astype(np.uint8)
    if fusedImage.shape != inputshape:
        refI = fusedImage[0:inputshape[0],0:inputshape[1]]       
#        refI = resize(fusedImage,inputshape)
        return refI
    return fusedImage
# Fith: Show image
#cv2.imshow("win",fusedImage)