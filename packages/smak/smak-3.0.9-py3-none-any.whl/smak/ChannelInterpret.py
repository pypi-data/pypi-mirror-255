import string

import atomic_sub

esym=[  "H" , "He", "Li", "Be", "B" , "C" , "N" , "O" , "F" , "Ne", "Na",
        "Mg", "Al", "Si", "P" , "S" , "Cl", "Ar", "K" , "Ca", "Sc", "Ti",
        "V" , "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As",
        "Se", "Br", "Kr", "Rb", "Sr", "Y" , "Zr", "Nb", "Mo", "Tc", "Ru",
        "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I" , "Xe", "Cs",
        "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy",
        "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W" , "Re", "Os", "Ir",
        "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra",
        "Ac", "Th", "Pa", "U" , "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es",
        "Fm", "Md", "No", "Lw"]

def value(v):
    v=str(v)
    #check to see if v has an energy in it
    firstnum=-1
    lastnum=-1
    for i in range(len(v)):
        try:
            int(v[i])
            if firstnum==-1:
                firstnum=i
                lastnum=i+1
            if lastnum==i:
                lastnum=i+1
        except: pass
    if firstnum!=-1:
        if lastnum!=firstnum:
            return float(v[firstnum:lastnum])
        else:
            if firstnum+1<len(v):
                return float(v[firstnum:firstnum+1])
            else:
                return float(v[firstnum:])
    #try for esyms
    tZ=-1
    if v[0:2] in esym:
        tZ=atomic_sub.sym2Z(v[0:2])
    elif v[0] in esym:
        tZ=atomic_sub.sym2Z(v[0])
    if tZ==-1: return ''
    tK=atomic_sub.get_fl(tZ,0)
    tL=atomic_sub.get_fl(tZ,1)
    if tK<25000: return tK
    else: return tL
    