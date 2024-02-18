
#from Numeric import *
import time

a=100
b=10000
t=time.clock()
na=[]
for j in range(b):
    nar=[]
    for i in range(a):
        nar.append(float(i))
    na.append(nar)
na=array(na)
t1=time.clock()
na=zeros((a,b),Float)
for j in range(b):
    nar=[]
    for i in range(a):
        nar.append(float(i))
    na[:,j]=array(nar,typecode=Float)
t2=time.clock()
print (t1-t)
print (t2-t1)


    