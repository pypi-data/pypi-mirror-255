
import sblite
import random
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

random.seed(0)
a=[]
b=np.arange(55,dtype=np.float)
c=np.arange(55,dtype=np.float)
d=np.arange(55,dtype=np.float)
e=np.arange(55,dtype=np.float)
for i in range(55):
    b[i] = b[i] + random.gauss(0,3)
    c[i] = c[i] + random.gauss(0, 2)
    d[i] = d[i] + random.gauss(0, 4)
    e[i] = e[i] + random.gauss(0, 1.5)

a.append(b)
a.append(c)
a.append(d)
a.append(e)

h=[0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]
h=np.array(h)

test = 0

if test==0:
    print(len(h))
    g=sblite.PairGrid(a,[0,1,2,3],aspect=0.5,xlabels=['S1','S2','S3','S4'],hue=h)
    g=g.map_offdiag(plt.scatter,s=5)
    g=g.map_diag(sblite.plot_scpkde)
    g=g.add_legend()
if test==1:
    g=sblite.GridPlot(5,layout_pad=2.75)
    g=g.add([a[0],a[1]],['a','b'],'File1',plt.scatter)
    g=g.add([a[0],a[2]],['a','b'],'File2',plt.scatter)
    g=g.add([a[0],a[3]],['a','b'],'File3',plt.scatter)
    g=g.add([a[1],a[2]],['a','b'],'File4',plt.scatter)
    g=g.add([a[0],a[1]],['a','b'],'File5',plt.scatter)
plt.show()

