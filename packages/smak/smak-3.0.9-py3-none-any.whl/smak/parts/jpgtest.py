
from Numeric import *
from string import *

import Image
import ImageFile
import ImageGrab


fn='smak_sm.jpg'

im=Image.open(fn)

im.load()

print(im.mode)
new=im.convert('L')
print(new.mode)
#print list(new.getdata())
#new.show()
print(new.size) #w,ht
