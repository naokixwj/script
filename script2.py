# -*- coding: cp936 -*-
import arcpy
import os

#input parameters
bhtb = arcpy.GetParameterAsText(0)
selectedField = arcpy.GetParameterAsText(1)
outputFC = arcpy.GetParameterAsText(2)

arcpy.AddMessage(bhtb)
arcpy.AddMessage(selectedField)
arcpy.AddMessage(outputFC)

#copy data
copied_data = os.path.join(arcpy.env.workspace,"copythis")
arcpy.FeatureClassToFeatureClass_conversion(bhtb,arcpy.env.workspace,"copythis")
#add id field
arcpy.AddField_management (copied_data, "sId", "LONG")
idname = arcpy.Describe(copied_data).OIDFieldName
arcpy.CalculateField_management(copied_data, "sId","!"+idname+"!","PYTHON_9.3")
#convert to lines
feat2lines = os.path.join(arcpy.env.workspace,"feat2lines")
arcpy.FeatureToLine_management (copied_data, feat2lines)
#delete useless field
fieldlist = arcpy.ListFields(feat2lines)
keepFields = [selectedField.lower(),idname.lower(),"shape_area","shape_length","shape","sid"]
dFields = []
for _field in fieldlist:
    if _field.name.lower() not in keepFields:
        dFields.append(_field.name)
arcpy.DeleteField_management (feat2lines, dFields)
#intersect
crossed_data = os.path.join(arcpy.env.workspace,"icrossmyself")
arcpy.Intersect_analysis ([feat2lines,feat2lines], crossed_data)
selectedCrossed = os.path.join(arcpy.env.workspace,"crossed_selected")
arcpy.Select_analysis (crossed_data, selectedCrossed, '"sId" <> "sId_1" AND ' + selectedField +' = ' + selectedField + "_1")
arcpy.DeleteIdentical_management (selectedCrossed, "sId")
#join result back
arcpy.JoinField_management(copied_data, "sId", selectedCrossed, "sId")
arcpy.Select_analysis (copied_data, outputFC, '"sId_12" > 0')

fieldlist = arcpy.ListFields(outputFC)
dFields = []
keepFields = [selectedField.lower(),idname.lower(),"shape_area","shape_length","shape","sid"]
for _field in fieldlist:
    if _field.name.lower() not in keepFields:
        dFields.append(_field.name)
arcpy.DeleteField_management (outputFC, dFields)
#delete
arcpy.Delete_management(copied_data)
arcpy.Delete_management(feat2lines)
arcpy.Delete_management(crossed_data)
arcpy.Delete_management(selectedCrossed)


