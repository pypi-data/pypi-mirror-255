#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 12:22:26 2022

@author: samwebb
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 15:39:33 2022

@author: samwebb
"""
import h5py
import imutils
import os
import time

import cv2
import numpy as np
from PIL import Image

#local
import globalfuncs


#machinve vision version
def stitch_hdf(filename,left=0,right=0,view=False):

    # ap = argparse.ArgumentParser()
    # ap.add_argument("-f", "--file", type=str, required=True,
    # 	help="file name of hdf images to stitch")
    # #ap.add_argument("-o", "--output", type=str, required=True,
    # #	help="path to the output image")
    # ap.add_argument("-v", "--view", default=False, action='store_true',
    # 	help="view each individual image")
    # args = vars(ap.parse_args())
    
    # grab the paths to the input images and initialize our images list
    print("[INFO] loading images...")
    #imagePaths = sorted(list(paths.list_images(args["images"])))
    
    images = []
    
    #open hdf
    h=h5py.File(filename,'r')
    ash = h['/main/mapdata'][()].shape
    xc=int(h['/main'].attrs['xc'])
    yc=int(h['/main'].attrs['yc'])
    xdat=h['/main/xdata'][()]
    ydat=h['/main/ydata'][()]
    #if h['/main'].attrs.get('rf') is not None:
    #    rf = float(h['/main'].attrs['rf'])
    #else:
    #    rf = 1
    
    #loop and read images
    for i in range(0,ash[0]):
        images.append(h['/main/mapdata/'][i,left:-1-right,:,:])
        if i==0:
            imgh=h['/main/mapdata/'][i,:,left:-1-right,:].shape[0]
            imgw=h['/main/mapdata/'][i,:,left:-1-right,:].shape[1]
        print (h['/main/mapdata/'][i,:,left:-1-right,:].shape)
        if view:
            cv2.imshow(str(i),h['/main/mapdata/'][i,:,left:-1-right,:])
            cv2.waitKey()
    h.close()
    
    rf = float(imgh)/480.0
    
    print ("hxw:",imgh,imgw,rf)
    print("[INFO] stitching images...")
    t=time.time()
    
    stitcher = cv2.createStitcher(cv2.Stitcher_SCANS) if imutils.is_cv3() else cv2.Stitcher_create(cv2.Stitcher_SCANS)
    stitcher.setInterpolationFlags(2)
    (status, stitched) = stitcher.stitch(images)
    
    print(time.time()-t)
    
    # if the status is '0', then OpenCV successfully performed image
    if status != 0:
        print("[INFO] image stitching failed ({})".format(status))
        return 0
    #if len(stitched.shape)>2:
    #    stitched = stitched[::-1,:,:]
    #else:
    #    stitched = stitched[::-1,:]
    # write the output stitched image to disk
    
    outfnbase = os.path.splitext(filename.replace("raw","out"))[0]
    cv2.imwrite(outfnbase+".jpeg", stitched)
    #cv2.imshow("Stitched", stitched)
    #cv2.waitKey(3000)  
    
    grimg = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
    print ("stitch",grimg.shape)   
    cv2.imwrite(outfnbase.replace("out","outgs")+".jpeg", grimg) 
    #cv2.imshow("Stitched-GS", grimg)
    #cv2.waitKey(3000)
    
    #crop image to data collection area
    #default res is 480x640...
    fullsh = stitched.shape
    print (fullsh,imgh,imgw,xc,yc,rf)
    print (int(yc*rf),fullsh[0]-imgh+int(yc*rf),int(xc*rf),fullsh[1]-imgw+int(xc*rf))
    stzoom=stitched[int(yc*rf):fullsh[0]-imgh+int(yc*rf),int(xc*rf):fullsh[1]-imgw+int(xc*rf),:]
    print ("zoom-in",stzoom.shape)
    #cv2.imshow("Stitched-Z", stzoom)
    #cv2.waitKey(0)  
    if len(stzoom.shape)>2:
        stzoom = stzoom[::-1,:,:]
    else:
        stzoom = stzoom[::-1,:]    
    cv2.imwrite(outfnbase.replace("out","outscaled")+".jpeg", stzoom) 
    
    
    rx=float(xdat[-1])-float(xdat[0])
    ry=float(ydat[-1])-float(ydat[0])
    print (ry,rx)
    
    (dely,delx) = (ry/stzoom.shape[0],rx/stzoom.shape[1])
    print (dely,delx)
    
    ndel = int(10000*min(abs(dely),abs(delx)))/10000.
    print (ndel)
    newscaleY = abs(dely)/ndel
    newscaleX = abs(delx)/ndel
    
    #interpolate to new spacing...
    scaledimg = cv2.resize(stzoom,None,fy=newscaleY,fx=newscaleX,interpolation=cv2.INTER_CUBIC)
    print (scaledimg.shape)
    (dely,delx) = (ry/scaledimg.shape[0],rx/scaledimg.shape[1])
    print (dely,delx)
    #cv2.imshow("Stitched-Z", scaledimg)
    #cv2.waitKey(0) 
    
    #save smak hdf
    
    #data = mapdata
    #       --attr: channels (list), origin (name), isVert (bool), 
    #               labels (list), comments (text), energy (val)
    #xdata = xdata   -- attr pts
    #ydata = ydata   -- attr pts
    
    hdfn = outfnbase+".hdf5"
    channels=4
    xvals = globalfuncs.frange(xdat[0],xdat[-1],delx)[:-1]
    yvals = globalfuncs.frange(ydat[0],ydat[-1],dely)[:-1]
    nxpts = len(xvals)
    nypts = len(yvals)
    print (nxpts,nypts)
    
    dt = np.zeros((nypts,nxpts,channels+2),dtype=np.float32)
    dt[:,:,2:-1]=scaledimg
    grscimg = cv2.cvtColor(scaledimg, cv2.COLOR_BGR2GRAY)
    dt[:,:,-1]=grscimg
    
    #add coordinates to dt matrix
    for i in range(nxpts):
        dt[:,i,0] = np.ones((nypts))*xvals[i]
    for j in range(nypts):
        dt[j,:,1] = np.ones((nxpts))*yvals[j]
    
    hdf5=h5py.File(hdfn,'w')
    
    hdf5group=hdf5.create_group("main")
    hdf5data=hdf5group.create_dataset("mapdata",(nypts,nxpts,channels+2),data=dt,maxshape=(nypts,nxpts,None),dtype='float')
    hdf5xd=hdf5group.create_dataset("xdata",(nxpts,),dtype='float',data=xvals)
    hdf5yd=hdf5group.create_dataset("ydata",(nypts,),dtype='float',data=yvals)
    hdf5xd.attrs.create("pts",nxpts)
    hdf5yd.attrs.create("pts",nypts)
    hdf5group.attrs.create("channels",channels)
    hdf5group.attrs.create("origin","USDCimage")
    hdf5group.attrs.create("isVert",False)
    hdf5group.attrs.create("labels",[b"BLUE",b"GREEN",b"RED",b"GREY"])
    hdf5group.attrs.create("comments","picture stitch")
    hdf5group.attrs.create("energy",1)
    
    hdf5.close()
    
    return hdfn

    
#"manual" version using strict overlays
def stitch_hdf_man(filename,left=0,right=0,view=False):

    # ap = argparse.ArgumentParser()
    # ap.add_argument("-f", "--file", type=str, required=True,
    # 	help="file name of hdf images to stitch")
    # #ap.add_argument("-o", "--output", type=str, required=True,
    # #	help="path to the output image")
    # ap.add_argument("-v", "--view", default=False, action='store_true',
    # 	help="view each individual image")
    # args = vars(ap.parse_args())
    
    # grab the paths to the input images and initialize our images list
    print("[INFO] loading images...")
    #imagePaths = sorted(list(paths.list_images(args["images"])))
    
    images = []
    offsets = []
    
    #open hdf
    h=h5py.File(filename,'r')
    ash = h['/main/mapdata'][()].shape
    xc=int(h['/main'].attrs['xc'])
    yc=int(h['/main'].attrs['yc'])
    xdat=h['/main/xdata'][()]
    ydat=h['/main/ydata'][()]
    xl = len(xdat)
    yl = len(ydat)
    
    #loop and read images
    for i in range(0,ash[0]):
        if i+1>=ash[0]: 
            continue
        newim = h['/main/mapdata/'][i+1,:,left:-1-right,:]
        newim = newim[1:,1:,:]
        images.append(newim)
        if i==0:
            imgh=newim.shape[0]
            imgw=newim.shape[1]
            initx=xdat[i]
            inity=ydat[i]
        print (h['/main/mapdata/'][i,:,left:-1-right,:].shape)
        if view:
            cv2.imshow(str(i),h['/main/mapdata/'][i,:,left:-1-right,:])
            cv2.waitKey()
        #calc offsets
        
        xi = i%xl
        yi = int(i/xl)
        xv = xdat[xi]
        yv = ydat[yi]
        xo=float(xv-initx)/float(h['/main'].attrs['xfov'])*imgw
        yo=float(yv-inity)/float(h['/main'].attrs['yfov'])*imgh
        offsets.append([xo,yo])

    xolap = (xdat[-1]-xdat[-2])/float(h['/main'].attrs['xfov'])*imgw
    yolap = (ydat[-1]-ydat[-2])/float(h['/main'].attrs['yfov'])*imgh
    print ('xy olaps:',xolap,yolap)
    h.close()
    
    rf = float(imgh)/480.0
    
    print ("hxw:",imgh,imgw,rf)
    print("[INFO] stitching images...")
    t=time.time()
    
    total_width = int(imgw*(xl)/2)+int(xolap)
    total_height = int(imgh*(yl)/2)+int(yolap)
    stitched = np.zeros( (total_height, total_width, 3))
    stwt = np.zeros( (total_height, total_width, 3))

    for im,ofs in zip(images,offsets):
        print (stitched.shape,im.shape,ofs,np.count_nonzero(im[:,:,0]==0))
        stitched[int(ofs[1]):int(ofs[1])+imgh,int(ofs[0]):int(ofs[0])+imgw,:] += im[::-1,:,:] #(im[::-1,:,:]<50).astype(np.int8)
        stwt[int(ofs[1]):int(ofs[1])+imgh,int(ofs[0]):int(ofs[0])+imgw,:] += np.ones(im[::-1,:,:].shape)
    
    stitched = np.where(stwt==0,0,stitched/stwt)
    #convert to numpy
    stitched = np.array(stitched,dtype=np.float32)
    stitched = stitched [::-1,:,:]
    status=0
    
    print(time.time()-t)
    # if the status is '0', then OpenCV successfully performed image
    if status != 0:
        print("[INFO] image stitching failed ({})".format(status))
        return 0
    
    outfnbase = os.path.splitext(filename.replace("raw","out"))[0]
    cv2.imwrite(outfnbase+".jpeg", stitched)
    #cv2.imshow("Stitched", stitched)
    #cv2.waitKey(3000)  
    
    grimg = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
    print ("stitch",grimg.shape)   
    cv2.imwrite(outfnbase.replace("out","outgs")+".jpeg", grimg) 
    #cv2.imshow("Stitched-GS", grimg)
    #cv2.waitKey(3000)
    stitched = stitched [::-1,:,:]
    
    #crop image to data collection area
    #default res is 480x640...
    fullsh = stitched.shape
    print (fullsh,imgh,imgw,xc,yc,rf)
    stzoom=stitched[int(yc*rf):fullsh[0]-imgh+int(yc*rf),int(xc*rf):fullsh[1]-imgw+int(xc*rf),:]
    print ("zoom-in",stzoom.shape)
    #cv2.imshow("Stitched-Z", stzoom)
    #cv2.waitKey(0)  
    #if len(stzoom.shape)>2:
    #    stzoom = stzoom[::-1,:,:]
    #else:
    #    stzoom = stzoom[::-1,:]    
    cv2.imwrite(outfnbase.replace("out","outscaled")+".jpeg", stzoom) 
    
    
    rx=float(xdat[-1])-float(xdat[0])
    ry=float(ydat[-1])-float(ydat[0])
    print (ry,rx)
    
    (dely,delx) = (ry/stzoom.shape[0],rx/stzoom.shape[1])
    print (dely,delx)
    
    ndel = int(10000*min(abs(dely),abs(delx)))/10000.
    print (ndel)
    newscaleY = abs(dely)/ndel
    newscaleX = abs(delx)/ndel
    
    #interpolate to new spacing...
    scaledimg = cv2.resize(stzoom,None,fy=newscaleY,fx=newscaleX,interpolation=cv2.INTER_CUBIC)
    print (scaledimg.shape)
    (dely,delx) = (ry/scaledimg.shape[0],rx/scaledimg.shape[1])
    print (dely,delx)
    #cv2.imshow("Stitched-Z", scaledimg)
    #cv2.waitKey(0) 
    
    #save smak hdf
    
    #data = mapdata
    #       --attr: channels (list), origin (name), isVert (bool), 
    #               labels (list), comments (text), energy (val)
    #xdata = xdata   -- attr pts
    #ydata = ydata   -- attr pts
    
    hdfn = outfnbase+".hdf5"
    channels=4
    xvals = globalfuncs.frange(xdat[0],xdat[-1],delx)[:-1]
    yvals = globalfuncs.frange(ydat[0],ydat[-1],dely)[:-1]
    nxpts = len(xvals)
    nypts = len(yvals)
    print (nxpts,nypts)
    
    dt = np.zeros((nypts,nxpts,channels+2),dtype=np.float32)
    dt[:,:,2:-1]=scaledimg
    grscimg = cv2.cvtColor(scaledimg, cv2.COLOR_BGR2GRAY)
    dt[:,:,-1]=grscimg
    
    #add coordinates to dt matrix
    for i in range(nxpts):
        dt[:,i,0] = np.ones((nypts))*xvals[i]
    for j in range(nypts):
        dt[j,:,1] = np.ones((nxpts))*yvals[j]
    
    hdf5=h5py.File(hdfn,'w')
    
    hdf5group=hdf5.create_group("main")
    hdf5data=hdf5group.create_dataset("mapdata",(nypts,nxpts,channels+2),data=dt,maxshape=(nypts,nxpts,None),dtype='float')
    hdf5xd=hdf5group.create_dataset("xdata",(nxpts,),dtype='float',data=xvals)
    hdf5yd=hdf5group.create_dataset("ydata",(nypts,),dtype='float',data=yvals)
    hdf5xd.attrs.create("pts",nxpts)
    hdf5yd.attrs.create("pts",nypts)
    hdf5group.attrs.create("channels",channels)
    hdf5group.attrs.create("origin","USDCimage")
    hdf5group.attrs.create("isVert",False)
    hdf5group.attrs.create("labels",[b"BLUE",b"GREEN",b"RED",b"GREY"])
    hdf5group.attrs.create("comments","picture stitch")
    hdf5group.attrs.create("energy",1)
    
    hdf5.close()
    
    return hdfn
   
    