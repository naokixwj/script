# -*- coding: cp936 -*-
import arcpy
import os

#input parameters
bhtb = arcpy.GetParameterAsText(0)
qsx = arcpy.GetParameterAsText(1)
hsx = arcpy.GetParameterAsText(2)
jclb_text = str(arcpy.GetParameterAsText(3))
outputFC = arcpy.GetParameterAsText(4)
manualMonth = "01"
try:
    jclb_text = jclb_text.strip()
    if len(jclb_text) == 6:
        manualMonth = jclb_text[-2:]
    else:
        arcpy.AddError("JCLB��������")
except:
    arcpy.AddError("�������·�ʱ����")

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
    dlText = ["����","԰��","�ֵ�","�ݵ�","���ݽ���","��·���·","������","����ѣ���","�߶�����","�����","ˮ��","Χ�������"]
    subCode = str(code)[:2]
    subText = ""
    if subCode in dlCode:
        subText = dlText[dlCode.index(subCode)]
    return subText

#function:get san ji lei
def GetSJL(code):
    if code == None:
        return ""
    dlCode = ['0101','0103','0201','0202','0203','0204','0301','0302','0305','0307','0307A','0307B','0401','0402','0402A','0402B','0601','0602','0610','0710','0711','0712','0713','0714','0719','0717','0720','0721','0722','0729','0750','0760','0770','0790','0810','0821','0831','0832','0833','0839','0890','1101','1102','1103','1104','1107','1201','1202','1203']
    dlText = ['ˮ��','����','����','����','����','����԰��','��ľ�ֵ�','���ֵ�','��ľ�ֵ�','�����ֵ�','����','�̻���ľ','��Ȼ�ݵ�','�˹��ݵ�','�̻��ݵ�','�����˹��ݵ�','��·���������·��','ũ���·','��·���������ͨ��','Ӳ���ر�','�㳡','¶��������','¶��ͣ����','ͣ��ƺ���ܵ�','����Ӳ���ر�','¶��ѷų�','ˮ����ʩ','�̰�','��ͷ','����ˮ��������','���Ҵ���','�̻���','��ҵ��ʩ','����������','�ɿ��õ�','β���','��Ǩ��������','���ݽ�������','��·��������','�����𽨵ر�','��������ѣ���','����ˮ��','����ˮ��','ˮ��ˮ��','����ˮ��','����','Χ����Ŀ','���Ŀ','�����Ŀ']
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
outputFields = ["XZQDM,text,6",
                "XMC,text,30",
                "JCBH,text,18",
                "TBLB,text,10",
                "TBLBMC,text,30",
                "TBLX,text,10",
                "TBLXMC,text,30",
                "TZ,text,10",
                "QSX,text,20",
                "HSX,text,20",
                "DQJH,text,254",
                "QQJH,text,254",
                "LZB,double,18,6",
                "BZB,double,18,6",
                "JCMJ,double,17,1",
                "JCLB,text,6",
                "ZDBH,text,30",
                "ZDHQLX,text,10",
                "ZDQQLX,text,10",
                "QQTBLX,text,254",
                "SFWBHTB,text,2",
                "BZ,text,100",
                "YXSJLY,text,254",
                "SubArea,double,10,6",
                "PORTION,double,10,6"
                ]
updateFields = ["XZQDM",
              "XMC",
              "JCBH",
              "TBLB",
              "TBLBMC",
              "TBLX",
              "TBLXMC",
              "TZ",
              "QSX",
              "HSX",
              "DQJH",
              "QQJH",
              "LZB",
              "BZB",
              "JCMJ",
              "JCLB",
              "ZDBH",
              "ZDHQLX",
              "ZDQQLX",
              "QQTBLX",
              "SFWBHTB",
              "BZ",
              "YXSJLY",
              "scenetime",
              "SX",
              "JH",
              "name",
              "FID_bhtb4490",
              "SubArea",
              "PORTION",
              "BIGAREA"
              ]
arcpy.AddMessage("2022 ������")
arcpy.AddMessage(bhtb)
arcpy.AddMessage(qsx)
arcpy.AddMessage(hsx)
arcpy.AddMessage(manualMonth)
arcpy.AddMessage(arcpy.env.workspace)
#reproject to 4490
fc4490 = arcpy.SpatialReference(4490)
rpfc = []
#------------bhtb
out_sorted = os.path.join(arcpy.env.workspace,"bhtbsorted")
arcpy.Sort_management(bhtb, out_sorted, [["Shape", "ASCENDING"]], "UL")
out_dataset = os.path.join(arcpy.env.workspace,"bhtb4490")
if arcpy.Describe(out_sorted).spatialReference.factoryCode != 4490:
    arcpy.Project_management (out_sorted, out_dataset, fc4490)
    rpfc.append(out_dataset)
else:
    arcpy.FeatureClassToFeatureClass_conversion(bhtb,arcpy.env.workspace,"bhtb4490")
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
#---------------#
arcpy.AddField_management(rpfc[0],"BIGAREA","DOUBLE")
arcpy.CalculateField_management(rpfc[0], "BIGAREA",'!shape.area@squaremeters!', "PYTHON_9.3")
#identity bhtb4490 with qsx,hsx,xzjx
identity1 = os.path.join(arcpy.env.workspace,"bhtb_qsx")
identity3 = os.path.join(arcpy.env.workspace,"bhtb_qsx_hsx")
arcpy.Identity_analysis(rpfc[0],rpfc[1],identity1)
arcpy.Identity_analysis(identity1,rpfc[2],identity3)
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
    dlCode = ["01","02","03","04","05","06","07","08","09","10","11","12"]
    dlText = ["����","԰��","�ֵ�","�ݵ�","������","��·���·","������","����ѣ���","�߶�����","���","ˮ��","Χ�������"]
    subCode = str(code)[:2]
    subText = ""
    if subCode in dlCode:
        subText = dlText[dlCode.index(subCode)]
    return subText''')

arcpy.CalculateField_management(sortedData, "TBLXMC",'GetSJL(!TBLX!)', "PYTHON_9.3",'''def GetSJL(code):
    if code == None:
        return ""
    dlCode = ['0101','0103','0201','0202','0203','0204','0301','0302','0305','0307','0307A','0307B','0401','0402','0402A','0402B','0601','0602','0610','0710','0711','0712','0713','0714','0719','0717','0720','0721','0722','0729','0750','0760','0770','0790','0810','0821','0831','0832','0833','0839','0890','1101','1102','1103','1104','1107','1201','1202','1203']
    dlText = ['ˮ��','����','����','����','����','����԰��','��ľ�ֵ�','���ֵ�','��ľ�ֵ�','�����ֵ�','����','�̻���ľ','��Ȼ�ݵ�','�˹��ݵ�','�̻��ݵ�','�����˹��ݵ�','��·���������·��','ũ���·','��·���������ͨ��','Ӳ���ر�','�㳡','¶��������','¶��ͣ����','ͣ��ƺ���ܵ�','����Ӳ���ر�','¶��ѷų�','ˮ����ʩ','�̰�','��ͷ','����ˮ��������','���Ҵ���','�̻���','��ҵ��ʩ','����������','�ɿ��õ�','β���','��Ǩ��������','���ݽ�������','��·��������','�����𽨵ر�','��������ѣ���','����ˮ��','����ˮ��','ˮ��ˮ��','����ˮ��','����','Χ����Ŀ','���Ŀ','�����Ŀ']
    subCode = str(code)
    subText = ""
    if subCode in dlCode:
        subText = dlText[dlCode.index(subCode)]
    return subText''')
try:
    arcpy.CalculateField_management(sortedData, "TBLB","!TBLX![:2]","PYTHON_9.3")
except:
    arcpy.AddWarning("TBLX �����ڣ�TBLB���Ϊ��")
try:
    arcpy.CalculateField_management(sortedData, "QSX","!SX!","PYTHON_9.3")
except:
    arcpy.AddWarning("SX �����ڣ�QSX���Ϊ��")
try:
    arcpy.CalculateField_management(sortedData, "ZDHQLX","!ZDTBHSXLX!","PYTHON_9.3")
except:
    arcpy.AddWarning("ZDTBHSXLX �����ڣ�ZDHQLX���Ϊ��")
try:
    arcpy.CalculateField_management(sortedData, "ZDQQLX","!ZDTBQSXLX!","PYTHON_9.3")
except:
    arcpy.AddWarning("ZDTBQSXLX �����ڣ�ZDQQLX���Ϊ��")
try:
    arcpy.CalculateField_management(sortedData, "HSX","!scenetime!","PYTHON_9.3")
except:
    arcpy.AddWarning("scenetime �����ڣ�HSX���Ϊ��")
try:
    arcpy.CalculateField_management(sortedData, "DQJH","!name!","PYTHON_9.3")
except:
    arcpy.AddWarning("name �����ڣ�DQJH���Ϊ��")
try:
    arcpy.CalculateField_management(sortedData, "QQJH","!JH!","PYTHON_9.3")
except:
    arcpy.AddWarning("JH �����ڣ�QQJH���Ϊ��")
try:
    arcpy.CalculateField_management(sortedData, "JCLB",jclb_text,"PYTHON_9.3")
except:
    arcpy.AddWarning("���������ֵ�쳣��JCLB���Ϊ��")
try:
    arcpy.CalculateField_management(sortedData, "LZB","!SHAPE.CENTROID.X!","PYTHON_9.3")
    arcpy.CalculateField_management(sortedData, "BZB","!SHAPE.CENTROID.Y!","PYTHON_9.3")
except:
    arcpy.AddWarning("ͼ�������⣬LZB��BZB���Ϊ��")
try:
    arcpy.CalculateField_management(sortedData, "JCBH",'GetJCBH(!XZQDM!,'+manualMonth+',!FID_bhtb4490!)', "PYTHON_9.3",'''def GetJCBH(xzqdm,monthText,fid):
    tmt = str(monthText)
    try:
        tFid = str(fid)
        for i in range(6-len(tFid)):
            tFid = "0"+tFid
        if len(tmt) == 1:
            tmt = "0"+tmt
        return tmt+tFid
    except:
        return "Err!"''')
except:
    arcpy.AddWarning("GetJCBH ���г���JCBH���Ϊ��")
try:
    arcpy.CalculateField_management(sortedData, "JCMJ",'float("%.1f"%(!BIGAREA!/666.667))',"PYTHON_9.3")
except:
    arcpy.AddWarning("BIGAREA �����ڣ�JCMJ���Ϊ��")

keepFields = ["XZQDM",
              "XMC",
              "JCBH",
              "TBLB",
              "TBLBMC",
              "TBLX",
              "TBLXMC",
              "TZ",
              "QSX",
              "HSX",
              "DQJH",
              "QQJH",
              "LZB",
              "BZB",
              "JCMJ",
              "JCLB",
              "ZDBH",
              "ZDHQLX",
              "ZDQQLX",
              "QQTBLX",
              "SFWBHTB",
              "BZ",
              "YXSJLY",
              "FID_bhtb4490",
              arcpy.Describe(sortedData).OIDFieldName,
              "Shape",
              "Shape_Area",
              "Shape_Length"
              ]
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
arcpy.JoinField_management (rpfc[0], leftOID, sortedData, "FID_bhtb4490", ["XZQDM",
              "XMC",
              "JCBH",
              "TBLB",
              "TBLBMC",
              "TBLX",
              "TBLXMC",
              "TZ",
              "QSX",
              "HSX",
              "DQJH",
              "QQJH",
              "LZB",
              "BZB",
              "JCMJ",
              "JCLB",
              "ZDBH",
              "ZDHQLX",
              "ZDQQLX",
              "QQTBLX",
              "SFWBHTB",
              "BZ",
              "YXSJLY"])

arcpy.Copy_management(rpfc[0],outputFC)
arcpy.AddMessage("2022 ������")

#clear
arcpy.Delete_management(out_sorted)
arcpy.Delete_management(rpfc[1])
arcpy.Delete_management(rpfc[2])
arcpy.Delete_management(identity1)
arcpy.Delete_management(identity3)
arcpy.Delete_management(sortedData)
arcpy.Delete_management(dissolved)
arcpy.Delete_management(rpfc[0])









