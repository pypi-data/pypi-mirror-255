#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 10:05:19 2023

@author: samwebb
"""

import math
import string
import numpy as np
import os.path
import struct


def agilentFile(filename):
    
#   Function: agilentFile
#   Usage: [wavenumbers, data, width, height, filename] = agilentFile();
#   Usage: [wavenumbers, data, width, height, filename] = agilentFile(filename);
#
#   Extracts the spectra from either an Agilent single tile FPA image, or a
#   mosaic of tiles.
#
#   input:
#   'filename' string containing the full path to either a .seq file (for a
#       single tile) or a .dms file (mosaic) (optional)
# 
#   output:
#   'wavenumbers' is a list of the wavenumbers related to the data
#   'data' is a 3D cube of the data in the file (height x width x wavenumbers)
#   'width' is the width of the image in pixels (rows)
#   'height' is the height of the image in pixels (columns)
#   'filename' is a string containing the full path to the opened file
#
#                     *******Caution******* 
#   This code is a hack of the Agilent format and the location of the data
#   within the file may vary. Always check the output to make sure it is
#   sensible. If you have a file that doesn't work, please contact Alex. 
#
#   Copyright (c) 2017, Alex Henderson 
#   Contact email: alex.henderson@manchester.ac.uk
#   Licenced under the GNU General Public License (GPL) version 3
#   http://www.gnu.org/copyleft/gpl.html
#   Other licensing options are available, please contact Alex for details
#   If you use this file in your work, please acknowledge the author(s) in
#   your publications. 
#
#   version 1.0, June 2017    
#
#   This version is translated to python by Sam Webb (March 4, 2023)
#   from the original Matlab code by Alex Henderson

    [pathstr,ext]=os.path.splitext(filename)
    if ext in ['.dms','.dmt']:
        #agilent mosaic
        return agilentMosaic(filename)
    elif ext in ['.seq','.bsp']:
        return agilentImage(filename)
    else:
        print ('file not Agilent type')
        return None
    
def agilentImage(filename):
    
#   Function: agilentImage
#   Usage: [wavenumbers, data, width, height, filename] = agilentImage(filename);
#
#   Extracts the spectra from an Agilent (formerly Varian) single tile FPA
#   image.
#
#   input:
#   'filename' string containing the full path to the .seq file (optional)
# 
#   output:
#   'wavenumbers' is a list of the wavenumbers related to the data
#   'data' is a 3D cube of the data in the file (height x width x wavenumbers)
#   'width' is the width of the image in pixels (rows)
#   'height' is the height of the image in pixels (columns)
#   'filename' is a string containing the full path to the .bsp file
#
#                     *******Caution******* 
#   This code is a hack of the Agilent format and the location of the data
#   within the file may vary. Always check the output to make sure it is
#   sensible. If you have a file that doesn't work, please contact Alex. 
#
#   Copyright (c) 2011 - 2017, Alex Henderson 
#   Contact email: alex.henderson@manchester.ac.uk
#   Licenced under the GNU General Public License (GPL) version 3
#   http://www.gnu.org/copyleft/gpl.html
#   Other licensing options are available, please contact Alex for details
#   If you use this file in your work, please acknowledge the author(s) in
#   your publications. 
#
#   version 5.0, June 2017 Alex Henderson. Calculate fpa size from data
#       rather than hardcoding as 128x128 pixels.
#       Changed fopen to be compatible with Octave. 
#   version 4.0, June 2017, Added width and height as outputs and changed
#       function name
#   version 3.0, August 2012, replaced loop through matrix with permute and
#       flipdim
#   version 2.1, December 2011, added GPL licence and incorporated
#       the getfilename function
#   version 2.0, June 2011, made date stamp more reliable using regex
#   version 1.0, May 2011, initial release    
#
#   This version is translated to python by Sam Webb (March 4, 2023)
#   from the original Matlab code by Alex Henderson   
    
    #extract the wavenumbers and date from the bsp file

    [pathstr, name] = os.path.split(filename) 
    [rootname,ext] = os.path.splitext(name)
    bspfilename = pathstr+os.sep+rootname+'.bsp'

    fid = open(bspfilename, mode='rb')  

    # wavenumbers
    fid.seek(2228,0)
    startwavenumber = struct.unpack('i',fid.read(4))[0]
    print (startwavenumber)

    fid.seek(2236,0)
    numberofpoints = struct.unpack('i',fid.read(4))[0]
    print (numberofpoints)
    
    fid.seek(2216,0)
    wavenumberstep = struct.unpack('d',fid.read(8))[0]
    print (wavenumberstep)
    
    # some validation
    if startwavenumber < 0:
        print('Start wavenumber is negative. Cannot read this file.');
        return None
    
    wavenumbers = np.arange(1, (startwavenumber + numberofpoints))
    wavenumbers = wavenumbers * wavenumberstep
    wavenumbers = np.delete(wavenumbers, range(0, startwavenumber- 1))

    #wavenumbers = np.arange(startwavenumber,startwavenumber+numberofpoints*wavenumberstep,wavenumberstep,dtype=np.float64)
    fid.close()

    #read the dat file
    datfilename = pathstr+os.sep+rootname+'.dat'        
    fid = open(datfilename, mode='rb')      
    data = fid.read()
    fid.close()
    
    #determine the FPA size
    byt = len(data)
    byt = byt/4
    udata = struct.unpack(f'{int(byt)}f',data)
    byt = byt-255
    byt = byt/len(wavenumbers)
    fpaSize = int(math.sqrt(byt))
    print('data file: ',fpaSize)
    udata = np.array(udata[255:])
    print (udata.shape)
    udata = np.reshape(udata,[len(wavenumbers),fpaSize,fpaSize])
    height = fpaSize
    width = fpaSize
    #vals = len(wavenumbers)
    
    #rotate data to match spectrometer output
    udata = udata[:,::-1,:]
    udata = np.transpose(udata,[1,2,0])
    
    return  [wavenumbers, udata, width, height, filename]

def agilentMosaic(filename):

# Function: agilentMosaic
# Usage: 
#   [wavenumbers, data, width, height, filename] = agilentMosaic(filename);
#
# Purpose:
#   Extracts the spectra from an Agilent (formerly Varian) .dmt/.dms/.dmd
#   file combination. Plots an image of the total signal.
#
#  input:
#   'filename' string containing the full path to the .dms file (optional)
# 
#  output:
#   'wavenumbers' is a list of the wavenumbers related to the data
#   'data' is a 3D cube of the data in the file ((fpaSize x X) x (fpaSize x Y) x wavenumbers)
#   'width' is width in pixels of the entire mosaic
#   'height' is height in pixels of the entire mosaic
#   'filename' is a string containing the full path to the .dms file

#
#                     *******Caution******* 
#   This code is a hack of the Agilent format and the location of the data
#   within the file may vary. Always check the output to make sure it is
#   sensible. If you have a file that doesn't work, please contact Alex.
#
#   Copyright (c) 2011 - 2017, Alex Henderson 
#   Contact email: alex.henderson@manchester.ac.uk
#   Licenced under the GNU General Public License (GPL) version 3
#   http://www.gnu.org/copyleft/gpl.html
#   Other licensing options are available, please contact Alex for details
#   If you use this file in your work, please acknowledge the author(s) in
#   your publications. 
#
#       version 6.1, June 2017
#       version 6.1, June 2017 Alex Henderson. Modified fopen to be
#       compatible with Octave
#       version 6.0, March 2017 Alex Henderson. Calculate fpa size from data
#       rather than hardcoding as 128x128 pixels
#       version 5.0, May 2016 Alex Henderson, Renamed to agilentMosaic. No
#       change to operational code. 
#       version 4.1, March 2015 Alex Henderson, Small change to fix
#       filename case sensitivity issues on Linux. No other functional
#       changes. 
#       version 4.0, January 2014 Alex Henderson, Moved the data allocation
#       outside the file read loop. Also moved the wavenumber truncation
#       for keepme scenarios outside the file read loop.
#       version 3.0, November 2013 Alex Henderson, Added 'keepme' to allow
#       the data to have spectral regions removed during import
#       version 2.0, August 2012 Alex Henderson, replaced loop through
#       matrix with permute and flipdim
#       version 1.3, December 2011 Alex Henderson, added GPL licence and
#       incorporated the getfilename function
#       version 1.2, November 2011 Alex Henderson, the dmt filename is all
#       lowercase while the other filenames are of mixed case. Now we ask
#       for the .dms filename instead and build a lowercase .dmt filename
#       from that. This was only a problem in Linux. 
#       version 1.1, October 2011 Alex Henderson, the dms file only matches
#       the image if the number of tiles is small. Now we read each tile
#       separately. 
#       version 1.0, October 2011 Alex Henderson, initial release, based on
#       readvarian v2

## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Extract the wavenumbers and date from the dmt file
#

    [pathstr, name] = os.path.split(filename) 
    [rootname,ext] = os.path.splitext(name)
# The Agilent software stores all files with mixed case filenames except the
# dmt file which is all lowercase. Therefore we build this from the dms
# filename. 

    rootname = rootname.lower()
    dmtfilename = pathstr+os.sep+rootname+'.dmt'

    fid = open(dmtfilename, mode='rb')  

    # wavenumbers
    fid.seek(2228,0)
    startwavenumber = struct.unpack('i',fid.read(4))[0]
    print (startwavenumber)

    fid.seek(2236,0)
    numberofpoints = struct.unpack('i',fid.read(4))[0]
    print (numberofpoints)
    
    fid.seek(2216,0)
    wavenumberstep = struct.unpack('d',fid.read(8))[0]
    print (wavenumberstep)
    
    # some validation
    if startwavenumber < 0:
        print('Start wavenumber is negative. Cannot read this file.');
        return None
    

    wavenumbers = np.arange(1, (startwavenumber + numberofpoints))
    wavenumbers = wavenumbers * wavenumberstep
    wavenumbers = np.delete(wavenumbers, range(0, startwavenumber- 1))

    #wavenumbers = np.arange(startwavenumber,startwavenumber+numberofpoints*wavenumberstep,wavenumberstep,dtype=np.float64)

    fid.close()
    
# Determine the mosaic dimensions
    tix = xtiles(pathstr,rootname)
    tiy = ytiles(pathstr,rootname)        
    
    tilefilename = pathstr+os.sep+rootname+'_0000_0000.dmd'        
    fid = open(tilefilename, mode='rb')      
    data = fid.read()
    fid.close()
    
    #determine the FPA size
    byt = len(data)
    byt = byt/4
    bytlength = byt-255
    by = bytlength/len(wavenumbers)
    fpaSize = int(math.sqrt(by))    
    print ('data file: ',fpaSize,tix,tiy)
#allocate memmory array
    data = np.zeros([len(wavenumbers),fpaSize*tiy,fpaSize*tix],dtype=np.float32)

#read dmd files
    for y in range(tiy):
        for x in range(tix):
            curr_extn = '_%04d_%04d.dmd' % (x,y)
            tempfilename = pathstr+os.sep+rootname+curr_extn
            fid = open(tempfilename, mode='rb') 
            fid.seek(255*4,0)
            tempdata = fid.read()
            fid.close()           
            print(y,x,len(tempdata))
            udata = struct.unpack(f'{int(bytlength)}f',tempdata)
            udata = np.reshape(udata,[len(wavenumbers),fpaSize,fpaSize])
            #rotate data to match spectrometer output
            udata = udata[:,::-1,:]
            #udata = np.transpose(udata,[1,2,0])
            
            #insert data
            data[:,y*fpaSize:(y+1)*fpaSize,x*fpaSize:(x+1)*fpaSize] = udata

    width = fpaSize*tix
    height = fpaSize*tiy
    data = np.transpose(data,[1,2,0])
    return  [wavenumbers, data, width, height, filename]          

def xtiles(pathstr,rootname):
    #count tiles in x dimension
    tix = 1
    finished = False
    counter = 0
    while not finished:
        curr_extn = '_%04d_0000.dmd' % (counter)
        tempfilename = pathstr+os.sep+rootname+curr_extn
        if os.path.exists(tempfilename):
            counter+=1
        else:
            tix=counter
            finished=True
    return tix

def ytiles(pathstr,rootname):
    #count tiles in y dimension
    tiy = 1
    finished = False
    counter = 0
    while not finished:
        curr_extn = '_0000_%04d.dmd' % (counter)
        tempfilename = pathstr+os.sep+rootname+curr_extn
        if os.path.exists(tempfilename):
            counter+=1
        else:
            tiy=counter
            finished=True
    return tiy   
    

if __name__ == '__main__':
    
#   File
#    pth = "/Users/samwebb/Dropbox/SSRL/BLData/FTIR/agilent/OneDrive_1_4-2-2023/mk_215_s2_15x_1sc_1x1_64bg/mk_215_s2_15x_1sc_1x1_64bg.bsp"
#   Mosaic
    pth = "/Users/samwebb/Dropbox/SSRL/BLData/FTIR/agilent/mk_6573/mk_6573_1b_15x_16sc_2x2.dmt"

#    pth = "/Users/samwebb/Dropbox/SSRL/BLData/FTIR/agilent/OneDrive_1_4-2-2023/mk_215_s2_15x_1sc_1x1_64bg/bg.bsp"

    
    [wavenumbers, data, width, height, filename]=agilentFile(pth)
    print (width,height)
    import matplotlib.pyplot as plt
    plt.imshow(np.sum(data,axis=2))
    plt.show()
    



                  