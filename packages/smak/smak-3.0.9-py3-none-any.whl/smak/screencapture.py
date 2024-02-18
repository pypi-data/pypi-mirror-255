print("enter SC")

import pyscreenshot as pySS
from PIL import Image
from PIL import JpegImagePlugin    
from PIL import PpmImagePlugin
from PIL import PngImagePlugin
from PIL import TiffImagePlugin
from PIL import WmfImagePlugin
from PIL import GifImagePlugin
from PIL import BmpImagePlugin
Image._initialized = 1

#blatant fix...
Image.SAVE["JPEG"]=JpegImagePlugin._save
Image.EXTENSION[".jpg"]="JPEG"
Image.SAVE["PPM"]=PpmImagePlugin._save
Image.EXTENSION[".ppm"]="PPM"
Image.SAVE["PNG"]=PngImagePlugin._save
Image.EXTENSION[".png"]="PNG"
Image.SAVE["TIFF"]=TiffImagePlugin._save
Image.EXTENSION[".tif"]="TIFF"
Image.SAVE["WMF"]=WmfImagePlugin._save
Image.EXTENSION[".wmf"]="WMF"
Image.SAVE["GIF"]=GifImagePlugin._save
Image.EXTENSION[".gif"]="GIF"
Image.SAVE["BMP"]=BmpImagePlugin._save
Image.EXTENSION[".bmp"]="BMP"

def capture(x,y,w,h,fn):
    im = pySS.grab(bbox=(x,y,x+w,y+h))
    print(im.size,im)
    im=im.convert("RGB")
    im.save(fn)
    #screen=wx.ScreenDC()
    #bmp=wx.EmptyBitmap(w,h)
    #mem=wx.MemoryDC(bmp)
    #mem.Blit(0,0,w,h,screen,x,y)

    #sf=os.path.splitext(fn)[0]+".jpg"
    #bmp.SaveFile(sf,wx.BITMAP_TYPE_JPEG)

    #del mem

def saveMe(im,fn):
    
    print(im.size,im)
    im.save(fn)    