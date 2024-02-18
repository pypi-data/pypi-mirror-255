#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 13:04:40 2023

@author: samwebb
"""

# import the necessary packages
import numpy as np
import imutils
import cv2
import math

def convert(image):
    maxv=np.max(np.ravel(image))
    im = np.array(image/maxv*255,dtype=np.uint8)
    print (np.max(im))
    return im

def make_color(image):
    im = convert(image)
    return cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)

def data_color(image):
    destshape = list(image.shape)
    destshape.append(3)
    im = np.zeros(destshape, dtype=np.float32)
    for i in range(3):
        im[:,:,i]=image
    return im

def align_images(image, template, maxFeatures=500, keepPercent=0.2,
	debug=False, ptsOverride=None, color=True,
    method=None, matchKnn=False):
	# convert both the input image and template to grayscale
    if method is None:
        method = 'ORB'
    
    if color:
        imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)        
    else:
        imageGray = convert(image)
        templateGray = convert(template)

    if ptsOverride is None:

        if color:
            imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)        
        else:
            imageGray = convert(image)
            templateGray = convert(template)
    
    	# use ORB to detect keypoints and extract (binary) local
    	# invariant features
        if method=='ORB':
            orb = cv2.ORB_create(maxFeatures)
            fmethod = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
        elif method=='AKAZE':
            orb = cv2.AKAZE_create()
            fmethod = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
        elif method=='SIFT':
            orb = cv2.SIFT_create()
            fmethod = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_SL2
        else:
            method='ORB'
            orb = cv2.ORB_create(maxFeatures)
        (kpsA, descsA) = orb.detectAndCompute(imageGray, None)
        (kpsB, descsB) = orb.detectAndCompute(templateGray, None)
    
        print ('Keypoints: ',len(kpsA),len(kpsB))
        

        if not matchKnn:
            # match the features w/ brute Force
            #matcher = cv2.BFMatcher(cv2.NORM_HAMMING)#, crossCheck=True)
            matcher = cv2.DescriptorMatcher_create(fmethod)
            matches = matcher.match(descsA, descsB, None)
        	# sort the matches by their distance (the smaller the distance,
        	# the "more similar" the features are)
            matches = sorted(matches, key=lambda x:x.distance)
        	# keep only the top matches
            keep = int(len(matches) * keepPercent)
            print('matching:',keep,' of ',len(matches))
            matches = matches[:keep]
        else:
            
            bf=cv2.BFMatcher()
            matches=bf.knnMatch(descsA,descsB,k=2)
            #apply ratio test
            gmatch=[]
            for m,n in matches:
                if m.distance < 0.75*n.distance:
                    gmatch.append([m])
            print('matching:',len(gmatch),' of ',len(matches))
            matches=gmatch
            
            
            
    	# check to see if we should visualize the matched keypoints
        if debug:
            if not matchKnn:
                matchedVis = cv2.drawMatches(imageGray, kpsA, templateGray, kpsB,
        			matches, None, 15,None,None,None)#,0)
            else:
                matchedVis = cv2.drawMatchesKnn(imageGray, kpsA, templateGray, kpsB,
        			matches, None, 15,None,None,None)#,0)
            
            matchedVis = imutils.resize(matchedVis, width=1000)
            cv2.imshow("Matched Keypoints", matchedVis)
            cv2.waitKey(0)
            
    	# allocate memory for the keypoints (x, y)-coordinates from the
    	# top matches -- we'll use these coordinates to compute our
    	# homography matrix
        if not matchKnn:
            ptsA = np.zeros((len(matches), 2), dtype="float")
            ptsB = np.zeros((len(matches), 2), dtype="float")
            #loop over the top matches
            for (i, m) in enumerate(matches):
                #locate that the two keypoints in the respective images
                #that are close to each other
                ptsA[i] = kpsA[m.queryIdx].pt
                ptsB[i] = kpsB[m.trainIdx].pt
        else:
            ptsA = np.float32([kpsA[m[0].queryIdx].pt for m in matches])
            ptsB = np.float32([kpsB[m[0].trainIdx].pt for m in matches])

        if len(matches) < 5:
            print ('Need least 4 matches for finding homogrpahy...')
            return None,None,None  

    else:
        ptsA=ptsOverride[0]
        ptsB=ptsOverride[1]

      
	# compute the homography matrix between the two sets of matched
	# points
    (H, mask) = cv2.findHomography(ptsA, ptsB, method=cv2.RANSAC)
	# use the homography matrix to align the images
    (h, w) = template.shape[:2]
    print (H)

    if H is None:
        #transform failed
        return None,None,None
    #caluclate in readable measures...
    transform={}    
    tx=H[0,2]
    ty=H[1,2]
    scx=math.sqrt(H[0,0]**2+H[0,1]**2)
    scy=np.linalg.det(H[0:2,0:2])/scx
    shear=(H[0,0]*H[1,0]+H[0,1]*H[1,1])/np.linalg.det(H[0:2,0:2])
    rot = math.atan2(H[0,1],H[0,0])
    transform['tx']=tx
    transform['ty']=ty
    transform['scx']=scx
    transform['scy']=scy
    transform['sh']=shear
    transform['rot']=rot
    transform['H']=H
    transform['wh']=(w,h)
    
    aligned = cv2.warpPerspective(imageGray, H, (w, h))
	# return the aligned image
    return aligned,transform,templateGray

        