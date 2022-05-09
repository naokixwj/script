import code
import os
inFile = r"C:\Users\111\Documents\Arcpy开发\技术室\15.软件需求\script\资源\三级类表.txt"
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
