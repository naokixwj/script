# -*- coding: unicode -*-
import os
import arcpy

inputFeatureLayer = arcpy.GetParameter(0)
inputFieldName = arcpy.GetParameterAsText(1)
outputFolder = arcpy.GetParameterAsText(2)

lstFields = arcpy.ListFields(inputFeatureLayer)
selectField = None
for _field in lstFields:
    if _field.name == inputFieldName:
        selectField = _field
        
if selectField == None:
    arcpy.AddError(u"字段不存在")
    exit()
if selectField.type != "String":
    arcpy.AddError(u"字段不是字符型")
    exit()

existingValues = []
with arcpy.da.SearchCursor(inputFeatureLayer,[inputFieldName]) as cursor:
    for row in cursor:
        try:
            itemValue = row[0]
            if itemValue is None or len(itemValue.strip()) == 0:
                itemValue = ""
            else:
                if itemValue not in existingValues:
                    existingValues.append(itemValue)
        except:
            arcpy.AddWarning("Unsupported field value:")
            arcpy.AddWarning(row[0])
outFeatures = []
for item in existingValues:
    itemValue = item
    try:
        where_clause = '"%s" = \'%s\''%(inputFieldName,itemValue)
        try:
            if len(item.strip()) == 0:
                itemValue = "p_" + str(item)
                where_clause = '"%s" = \'%s\''%(inputFieldName,item)
            if item == None:
                itemValue = "p_None"
                where_clause = '"%s" IS None'%inputFieldName
            if item.isdigit():
                itemValue = "p_" + item
                where_clause = '"%s" = \'%s\''%(inputFieldName,item)
        except Exception as ex:
            arcpy.AddWarning(ex)
        sourceItemValue = itemValue
        itemValue = itemValue.replace('.','_').replace('-','_')
        #itemValue = itemValue.replace('-','_')
        outFeature = os.path.join(outputFolder,itemValue)
        desc = arcpy.Describe(outputFolder)
        if desc.dataType == 'Folder':
            if os.path.exists(outFeature + ".shp"):
                arcpy.Delete_management(outFeature + ".shp")
        else:
            if arcpy.Exists(outFeature):
                arcpy.Delete_management(outFeature)
        arcpy.Select_analysis(inputFeatureLayer,outFeature,where_clause)
        if desc.dataType == 'Folder':
            currentFiles = os.listdir(outputFolder)
            for mfile in currentFiles:
                filename = mfile[:-4]
                trailType = mfile[-4:]
                try:
                    if filename == itemValue:
                        os.rename(os.path.join(outputFolder,mfile),os.path.join(outputFolder,sourceItemValue + trailType))
                except:
                    arcpy.AddWarning("rename failed")
        arcpy.AddMessage(outFeature)
    except Exception as ex:
        arcpy.AddWarning(itemValue)
        arcpy.AddWarning(ex)
