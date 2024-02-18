#define colormaps

import string

fid=open('colormaps.txt')

maps={}
maplist=[]
exit = 0

while exit == 0:
    name=fid.readline().strip()
    if name == "":
        exit == 1
    maplist.append(name)
    temp=[]
    i=0
    if not exit:
        while i<256:
            map=fid.readline().split()
            try:
                temp.append([float(map[0]),float(map[1]),float(map[2])])
            except:
                exit=1
            i=i+1
    if not exit:
        maps[name]= temp

i=maplist.index('Jet')
maplist.insert(0,maplist.pop(i))
fid.close()
 
