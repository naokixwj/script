# -*- coding: UTF-8 -*-
import os
import arcpy
from datetime import datetime

#input parameters
inputFeature1 = arcpy.GetParameterAsText(0)
inputDaySpan1 = arcpy.GetParameter(1)
outputFeature = arcpy.GetParameterAsText(2)

#helper functions
def GetFeatureFieldsList(inFeature):
    resultList = []
    lstField = arcpy.ListFields(inFeature)
    for item in lstField:
        resultList.append(item.name)
    return resultList

def CheckField(inFeature,toCheckFields):
    try:
        lstField = GetFeatureFieldsList(inFeature)
        missingField = []
        for _field in toCheckFields:
            if _field not in lstField:
                missingField.append(_field)
        return missingField
    except:
        return []

#step 1 function
#playing with same period
def Step1Func(_inputFeature,outName,daySpan):
    #varibale
    inShapePath = os.path.join(arcpy.env.workspace,"inShape1")
    intersectOutput = os.path.join(arcpy.env.workspace,"iOutput1")
    selectNotDEL = os.path.join(arcpy.env.workspace,"selectNotDEL")
    dissolevedOutput = os.path.join(arcpy.env.workspace,outName)
    arcpy.FeatureClassToFeatureClass_conversion(_inputFeature,arcpy.env.workspace,"inShape1")
    arcpy.AddField_management(inShapePath,"CH","FLOAT")
    arcpy.AddField_management(inShapePath,"CV","FLOAT")
    arcpy.CalculateField_management(inShapePath,"CH","!Shape.CENTROID.Y!","PYTHON_9.3")
    arcpy.CalculateField_management(inShapePath,"CV","!Shape.CENTROID.X!","PYTHON_9.3")
    arcpy.Intersect_analysis([inShapePath,inShapePath],intersectOutput)
    keepList = {}
    uniqueList = {}
    oid = arcpy.Describe(intersectOutput).OIDFieldName
    lstField = GetFeatureFieldsList(intersectOutput)
    cursorField = ["Shape_Length","Shape_Area",oid, 'scenetime','imagegsd','scenetime_1', 'imagegsd_1','CH','CV', 'CH_1','CV_1','FID_inShape1']
    missingField = CheckField(intersectOutput,cursorField)
    if len(missingField) > 0:
        #arcpy.AddWarning(u"字段缺失,跳过此图层")
        arcpy.AddWarning(str(missingField))
        arcpy.Delete_management(inShapePath)
        arcpy.Delete_management(intersectOutput)
        return None
    with arcpy.da.SearchCursor(intersectOutput, cursorField) as cursor:
        for row in cursor:
            key = str(row[0]) + str(row[1])
            date1 = datetime.strptime(row[3],'%Y-%m-%d')
            date2 = datetime.strptime(row[5],'%Y-%m-%d')
            gsd1 = float(str(row[4]))
            gsd2 = float(str(row[6]))
            if key not in keepList:
                keepList[key] = []
            if abs((date1 - date2).days) > daySpan and date1 > date2:
                keepList[key].append(row[11])
            elif abs((date1 - date2).days) <= daySpan or date1 == date2:
                #优于
                if gsd1 < gsd2:
                    keepList[key].append(row[11])
                elif gsd1 == gsd2:
                    if row[8] < row[10]:
                        if row[7] < row[9]:
                            keepList[key].append(row[11])
                    elif row[7] < row[9]:
                        if row[8] < row[10]:
                            keepList[key].append(row[11])
                    elif row[8] == row[10] and row[7] == row[9]:
                        keepList[key].append(row[11])
    for item in keepList:
        uniqueList[item] = max(set(keepList[item]), key=keepList[item].count)
        arcpy.AddMessage(item + ":" + str(uniqueList[item]))
    with arcpy.da.UpdateCursor(intersectOutput,["Shape_Length","Shape_Area",'FID_inShape1','name',oid]) as cursor:
            for row in cursor:
                key = str(row[0]) + str(row[1])
                if uniqueList[key] != row[2]:
                    row[3] = "DEL"
                    cursor.updateRow(row)
    arcpy.Select_analysis(intersectOutput,selectNotDEL,'"name" <> \'DEL\'')
    lstField = GetFeatureFieldsList(_inputFeature)
    oidFieldName = arcpy.Describe(_inputFeature).OIDFieldName
    dissolvedFields = []
    for item in lstField:
        if item not in [oidFieldName,"Shape","Shape_Area","Shape_Length"]:
            dissolvedFields.append(item)
    arcpy.Dissolve_management(selectNotDEL,dissolevedOutput,dissolvedFields,multi_part="SINGLE_PART")
    arcpy.Delete_management(inShapePath)
    arcpy.Delete_management(intersectOutput)
    arcpy.Delete_management(selectNotDEL)
    return dissolevedOutput

#step 2 function
#playing with different period
def Step2Func(_inputFeature1,_inputFeature2,_outputFeature,daySpan):
    #varibale
    inShapePath1 = os.path.join(arcpy.env.workspace,"inShape1")
    inShapePath2 = os.path.join(arcpy.env.workspace,"inShape2")
    intersectOutput = os.path.join(arcpy.env.workspace,"iOutput")
    mergeOutput = os.path.join(arcpy.env.workspace,"mergeOutput")
    eraseOutput = os.path.join(arcpy.env.workspace,"eraseOutput")
    arcpy.FeatureClassToFeatureClass_conversion(_inputFeature1,arcpy.env.workspace,"inShape1")
    arcpy.FeatureClassToFeatureClass_conversion(_inputFeature2,arcpy.env.workspace,"inShape2")
    arcpy.Intersect_analysis([inShapePath2,inShapePath1],intersectOutput)
    arcpy.AddField_management(intersectOutput,"PBZ","TEXT",field_length=254)
    with arcpy.da.UpdateCursor(intersectOutput,['PBZ','scenetime','scenetime_1']) as cursor:
        for row in cursor:
            date1 = datetime.strptime(row[1],'%Y-%m-%d')
            date2 = datetime.strptime(row[2],'%Y-%m-%d')
            if abs((date1 - date2).days) > daySpan and date1 > date2:
                row[0] = ">30"
                cursor.updateRow(row)
            elif abs((date1 - date2).days) <= daySpan and date1 > date2:
                row[0] = "<=30"
                cursor.updateRow(row)
    #arcpy.Select_analysis(intersectOutput,selectNotDEL,' "PBZ" LIKE \'\%30\%\'')
    lstField1 = GetFeatureFieldsList(inShapePath1)
    lstField1.append('PBZ')
    lstField2 = GetFeatureFieldsList(intersectOutput)
    toDeleteFields = []
    for item in lstField2:
        if item not in lstField1:
            toDeleteFields.append(item)
    arcpy.DeleteField_management(intersectOutput,toDeleteFields)
    arcpy.Merge_management([inShapePath2,inShapePath1],mergeOutput)
    arcpy.Erase_analysis(mergeOutput,intersectOutput,eraseOutput)
    arcpy.Merge_management([eraseOutput,intersectOutput],_outputFeature)
    return True
    
if __name__ == "__main__":
    arcpy.AddMessage("%s:%s"%(str(1),inputFeature1))
    result1 = Step1Func(inputFeature1,outputFeature,inputDaySpan1)