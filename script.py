# -*- coding: cp936 -*-
import arcpy
import os

#input parameters
bhtb = arcpy.GetParameterAsText(0)
qsx = arcpy.GetParameterAsText(1)
hsx = arcpy.GetParameterAsText(2)
xzjx = arcpy.GetParameterAsText(3)
manualMonth = str(arcpy.GetParameterAsText(4))
jclb_text = str(arcpy.GetParameterAsText(5))
outputFC = arcpy.GetParameterAsText(6)

#function:test field exists
def CheckFieldNameInFeatureClass(inputFC,inputFN):
    testResult = False
    lstFields = arcpy.ListFields(inputFC)
    for _field in lstFields:
        if _field.name == inputFN:
            testResult = True
            break
    return testResult

#function:get er ji lei
def GetEJL(code):
    if code == None:
        return ""
    dlCode = ["01","02","03","04","05","06","07","08","09","10","11","12"]
    dlText = ["耕地","园地","林地","草地","房屋建筑","铁路与道路","构筑物","推填（堆）土","高尔夫球场","光伏板","水域","围填海（湖）"]
    subCode = str(code)[:2]
    subText = ""
    if subCode in dlCode:
        subText = dlText[dlCode.index(subCode)]
    return subText

#function:get san ji lei
def GetSJL(code):
    if code == None:
        return ""
    dlCode = ["0303","0763","0001","0101","0103","0201","0202","0203","0204","0301","0302","0305","0307","0307A","0307B","0401","0402","0402A","0402B","0501","0502","0503","0504","0505","0505A","0506","0601","0602","0610","0710","0711","0712","0713","0714","0719","0720","0721","0722","0729","0750","0760","0770","0790","0810","0821","0831","0832","0833","0890","1101","1102","1103","1104","1107","1201","1202","1203"]
    dlText = ["红树林","盐田","其他湿地","水田","旱地","果树","茶树","橡胶树","其他园地","乔木林地","竹林地","灌木林地","其他林地","A迹地","B绿化林木","天然草地","人工草地","A绿化草地","B其他人工草地","小区","农村居民点","厂房","别墅","设施农用地","A棚房","其他房屋","公路（含城镇村道路）","农村道路","铁路（含轨道交通）","硬化地表","广场","露天体育场","露天停车场","停机坪与跑道","其他硬化地表","水工设施","堤坝","码头","其它水工构筑物","温室大棚","固化池","工业设施","其他构筑物","采矿用地","尾矿库","拆迁待建工地","房屋建筑工地","道路建筑工地","其他推填（堆）土","河流水面","湖泊水面","水库水面","坑塘水面","沟渠","围海项目","填海项目","填湖项目"]
    subCode = str(code)
    subText = ""
    if subCode in dlCode:
        subText = dlText[dlCode.index(subCode)]
    return subText

#function:get JCBH
def GetJCBH(xzqdm,monthText,fid):
    tmt = str(monthText)
    try:
        tFid = str(fid)
        for i in range(6-len(tFid)):
            tFid = "0"+tFid
        if len(tmt) == 1:
            tmt = "0"+tmt
        return str(xzqdm)+tmt+tFid
    except:
        return "Err!"

#some useful args
outputFields = ["XZQDM,text,6","XMC,text,30","JCBH,text,18","TBLB,text,10","TBLBMC,text,30","TBLX,text,10","TBLXMC,text,30","TZ,text,10",
                "QSX,text,20","HSX,text,20","DQJH,text,100","QQJH,text,100","LZB,double,18,6","BZB,double,18,6","JCMJ,double,17,1","JCLB,text,6","ZDBH,text,30",
                "ZDLX,text,10","QQTBLX,text,10","SFWBHTB,text,2","BZ,text,100","SubArea,double,10,6","PORTION,double,10,6"]
updateFields = ["XZQDM","XZQMC","XMC","JCBH","TBLB","TBLBMC","TBLX","TBLXMC","TZ","QSX","HSX","DQJH",
                "QQJH","LZB","BZB","JCMJ","JCLB","ZDBH","ZDLX","QQTBLX","SFWBHTB","BZ",
                "scenetime","SX","JH","name","FID_bhtb4490","SubArea","PORTION","BIGAREA"]
arcpy.AddMessage("2022 技术室")
arcpy.AddMessage(bhtb)
arcpy.AddMessage(qsx)
arcpy.AddMessage(hsx)
arcpy.AddMessage(xzjx)
arcpy.AddMessage(manualMonth)
arcpy.AddMessage(arcpy.env.workspace)
#reproject to 4490
fc4490 = arcpy.SpatialReference(4490)
rpfc = []
#------------bhtb
out_sorted = os.path.join(arcpy.env.workspace,"bhtbsorted")
arcpy.Sort_management(bhtb, out_sorted, [["Shape", "ASCENDING"]], "UL")
out_dataset = os.path.join(arcpy.env.workspace,"tmpbhtb4490")
if arcpy.Describe(out_sorted).spatialReference.factoryCode != 4490:
    arcpy.Project_management (out_sorted, out_dataset, fc4490)
    #arcpy.AddField_management(out_dataset,"BIGAREA","DOUBLE")
    #arcpy.CalculateField_management(out_dataset, "BIGAREA",'!shape.area@squaremeters!', "PYTHON_9.3")
    rpfc.append(out_dataset)
else:
    arcpy.FeatureClassToFeatureClass_conversion(bhtb,arcpy.env.workspace,"tmpbhtb4490")
    #arcpy.AddField_management(out_dataset,"BIGAREA","DOUBLE")
    #arcpy.CalculateField_management(out_dataset, "BIGAREA",'!shape.area@squaremeters!', "PYTHON_9.3")
    rpfc.append(out_dataset)
#------------qsx
out_dataset = os.path.join(arcpy.env.workspace,"qsx4490")
if arcpy.Describe(qsx).spatialReference.factoryCode != 4490:
    arcpy.Project_management (qsx, out_dataset, fc4490)
    rpfc.append(out_dataset)
else:
    arcpy.FeatureClassToFeatureClass_conversion(qsx,arcpy.env.workspace,"qsx4490")
    rpfc.append(out_dataset)
#------------hsx
out_dataset = os.path.join(arcpy.env.workspace,"hsx4490")
if arcpy.Describe(hsx).spatialReference.factoryCode != 4490:
    arcpy.Project_management(hsx, out_dataset, fc4490)
    rpfc.append(out_dataset)
else:
    arcpy.FeatureClassToFeatureClass_conversion(hsx,arcpy.env.workspace,"hsx4490")
    rpfc.append(out_dataset)
#------------xzjx
out_dataset = os.path.join(arcpy.env.workspace,"xzjx4490")
if arcpy.Describe(xzjx).spatialReference.factoryCode != 4490:
    arcpy.Project_management (xzjx, out_dataset, fc4490)
    rpfc.append(out_dataset)
else:
    arcpy.FeatureClassToFeatureClass_conversion(xzjx,arcpy.env.workspace,"xzjx4490")
    rpfc.append(out_dataset)
for value in rpfc:
    arcpy.AddMessage(value)
#------------clip bhtb
former_rpfc0 = rpfc[0]
clippedByXZQ = os.path.join(arcpy.env.workspace,"bhtb4490")
arcpy.Identity_analysis(rpfc[0], rpfc[3], clippedByXZQ,"ONLY_FID")
arcpy.AddField_management(clippedByXZQ,"BIGAREA","DOUBLE")
arcpy.CalculateField_management(clippedByXZQ, "BIGAREA",'!shape.area@squaremeters!', "PYTHON_9.3")
rpfc[0] = clippedByXZQ
#identity bhtb4490 with qsx,hsx,xzjx
identity1 = os.path.join(arcpy.env.workspace,"bhtb_qsx")
identity2 = os.path.join(arcpy.env.workspace,"bhtb_qsx_hsx")
identity3 = os.path.join(arcpy.env.workspace,"bhtb_qsx_hsx_xzjx")
arcpy.Identity_analysis(rpfc[0],rpfc[1],identity1)
arcpy.Identity_analysis(identity1,rpfc[2],identity2)
arcpy.Identity_analysis(identity2,rpfc[3],identity3)
#check output field and create missing
for field in outputFields:
    lstItem = field.split(",")
    if CheckFieldNameInFeatureClass(identity3,lstItem[0]) == False:
        if len(lstItem) == 3:
            arcpy.AddField_management(identity3,lstItem[0].upper(),lstItem[1],field_length=int(lstItem[2]))
        if len(lstItem) == 4:
            arcpy.AddField_management(identity3,lstItem[0].upper(),lstItem[1],int(lstItem[2]),field_length=int(lstItem[3]))
lstFields = arcpy.ListFields(identity3)
validFields = []
for _field in lstFields:
    if _field.name.startswith("XZQDM"):
        validFields.append(_field.name)
    if _field.name.startswith("XZQMC"):
        validFields.append(_field.name)
if "XZQMC_1" in validFields:
    arcpy.CalculateField_management(identity3, "XMC","!XZQMC_1!","PYTHON_9.3")
else:
    arcpy.CalculateField_management(identity3, "XMC","!XZQMC!","PYTHON_9.3")
if "XZQDM_1" in validFields:
    arcpy.CalculateField_management(identity3, "XZQDM","!XZQDM_1!","PYTHON_9.3")
        
        
#dissolove
dissolved = os.path.join(arcpy.env.workspace,"identity3_dissolved")
sortedData = os.path.join(arcpy.env.workspace,"sortedData")
arcpy.Dissolve_management (identity3, dissolved, updateFields)
arcpy.CalculateField_management(dissolved, "SubArea",'!shape.area@squaremeters!', "PYTHON_9.3")
arcpy.CalculateField_management(dissolved, "PORTION",'(!SubArea!/!BIGAREA!)*100', "PYTHON_9.3")
arcpy.Sort_management(dissolved, sortedData, [["FID_bhtb4490", "ASCENDING"], ["PORTION", "DESCENDING"]])
arcpy.DeleteIdentical_management (sortedData, ["FID_bhtb4490"])

arcpy.CalculateField_management(sortedData, "TBLBMC",'GetEJL(!TBLX!)', "PYTHON_9.3",'''def GetEJL(code):
    if code == None:
        return ""
    dlCode = ["00","01","02","03","04","05","06","07","08","09","10","11","12"]
    dlText = ["湿地","耕地","园地","林地","草地","房屋建筑","铁路与道路","构筑物","推填（堆）土","高尔夫球场","光伏板","水域","围填海（湖）"]
    subCode = str(code)[:2]
    subText = ""
    if subCode in dlCode:
        subText = dlText[dlCode.index(subCode)]
    return subText''')

arcpy.CalculateField_management(sortedData, "TBLXMC",'GetSJL(!TBLX!)', "PYTHON_9.3",'''def GetSJL(code):
    if code == None:
        return ""
    dlCode = ['0303', '0763', '0001', '0101', '0103', '0201', '0202', '0203', '0204', '0301', '0302', '0305', '0307', '0307A', '0307B', '0401', '0402', '0402A', '0402B', '0501', '0502', '0503', '0504', '0505', '0505A', '0506', '0601', '0602', '0610', '0710', '0711', '0712', '0713', '0714', '0719', '0717', '0718', '0720', '0721', '0722', '0729', '0750', '0760', '0770', '0790', '0810', '0821', '0831', '0832', '0833', '0839', '0849', '0890', '1101', '1102', '1103', '1104', '1107', '1201', '1202', '1203']
    dlText = ["红树林","盐田","其他湿地","水田","旱地","果树","茶树","橡胶树","其他园地","乔木林地","竹林地","灌木林地","其他林地","迹地","绿化林木","天然草地","人工草地","绿化草地","其他人工草地","小区","农村居民点","厂房","别墅","设施农用地","棚房","其他房屋","公路（含城镇道路）","农村道路","铁路（含轨道交通）","硬化地表","广场","露天体育场","露天停车场","停机坪与跑道","其他硬化地表","露天堆放场","碾压踩踏地表","水工设施","堤坝","码头","其它水工构筑物","温室大棚","固化池","工业设施","其他构筑物","采矿用地","尾矿库","拆迁待建工地","房屋建筑工地","道路建筑工地","其他拆建地表","其他整理地表","其他推填（堆）土","河流水面","湖泊水面","水库水面","坑塘水面","沟渠","围海项目","填海项目","填湖项目"]
    subCode = str(code)
    subText = ""
    if subCode in dlCode:
        subText = dlText[dlCode.index(subCode)]
    return subText''')
arcpy.CalculateField_management(sortedData, "TBLB","!TBLX![:2]","PYTHON_9.3")
arcpy.CalculateField_management(sortedData, "QSX","!SX!","PYTHON_9.3")
arcpy.CalculateField_management(sortedData, "HSX","!scenetime!","PYTHON_9.3")
arcpy.CalculateField_management(sortedData, "DQJH","!name!","PYTHON_9.3")
arcpy.CalculateField_management(sortedData, "QQJH","!JH!","PYTHON_9.3")
arcpy.CalculateField_management(sortedData, "JCLB",jclb_text,"PYTHON_9.3")
arcpy.CalculateField_management(sortedData, "SFWBHTB","!SFWBHTB!","PYTHON_9.3")
arcpy.CalculateField_management(sortedData, "LZB","!SHAPE.CENTROID.X!","PYTHON_9.3")
arcpy.CalculateField_management(sortedData, "BZB","!SHAPE.CENTROID.Y!","PYTHON_9.3")
arcpy.CalculateField_management(sortedData, "JCMJ",'float("%.1f"%(!BIGAREA!/666.667))',"PYTHON_9.3")
arcpy.CalculateField_management(sortedData, "JCBH",'GetJCBH(!XZQDM!,'+manualMonth+',!FID_bhtb4490!)', "PYTHON_9.3",'''def GetJCBH(xzqdm,monthText,fid):
    tmt = str(monthText)
    try:
        tFid = str(fid)
        for i in range(6-len(tFid)):
            tFid = "0"+tFid
        if len(tmt) == 1:
            tmt = "0"+tmt
        return str(xzqdm)+tmt+tFid
    except:
        return "Err!"''')
keepFields = ["XZQDM","XMC","JCBH","TBLB","TBLBMC","TBLX","TBLXMC","TZ","QSX","HSX","DQJH","QQJH","SFWBHTB","LZB","BZB","JCMJ","JCLB","ZDBH","ZDLX","QQTBLX","BZ","FID_bhtb4490",arcpy.Describe(sortedData).OIDFieldName,"Shape","Shape_Area","Shape_Length"]
lstFields = arcpy.ListFields(sortedData)
dFields = []
for _field in lstFields:
    if _field.name not in keepFields:
        dFields.append(_field.name)
arcpy.DeleteField_management (sortedData, dFields)

dFields = []
lstFields = arcpy.ListFields(rpfc[0])
oidFieldName = arcpy.Describe(rpfc[0]).OIDFieldName
keepFields2 = [oidFieldName.lower(),"shape_area","shape_length","shape"]
for _field in lstFields:
    if _field.name.lower() not in keepFields2:
        dFields.append(_field.name)

arcpy.DeleteField_management (rpfc[0], dFields)

leftOID = str(arcpy.Describe(rpfc[0]).OIDFieldName)
arcpy.JoinField_management (rpfc[0], leftOID, sortedData, "FID_bhtb4490", ["XZQDM","XMC","JCBH","TBLB","TBLBMC","TBLX","TBLXMC","TZ","QSX","HSX","DQJH","QQJH","SFWBHTB","LZB","BZB","JCMJ","JCLB","ZDBH","ZDLX","QQTBLX","BZ"])

arcpy.Copy_management(rpfc[0],outputFC)
arcpy.AddMessage("2022 技术室")

#clear
arcpy.Delete_management(out_sorted)
arcpy.Delete_management(rpfc[1])
arcpy.Delete_management(rpfc[2])
arcpy.Delete_management(rpfc[3])
arcpy.Delete_management(identity1)
arcpy.Delete_management(identity2)
arcpy.Delete_management(identity3)
arcpy.Delete_management(sortedData)
arcpy.Delete_management(dissolved)
arcpy.Delete_management(rpfc[0])
arcpy.Delete_management(former_rpfc0)









