import code
import os
inFile = r"C:\Users\111\Documents\Arcpy����\������\15.�������\script\��Դ\�������.txt"
codes = []
ctext = []
with open(inFile,'r') as f:
    rlines = f.readlines()
    for line in rlines:
        line = line.strip()
        c,t = line.split(",")
        codes.append(c)
        ctext.append(t)
print("','".join(codes))
print("','".join(ctext))
