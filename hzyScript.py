import random
import arcpy
import os
'''
输入参数1：原始数据
输入参数2：按重点、非重点、不区分进行图斑抽取
输入参数3：

执行流程：
1、对数据进行按图形重排
2、通过耕地范围将将耕地值写进数据图层
2、计算比例，先计算总图斑量，然后计算耕保范围图斑量，计算执法(执法是不考虑边界的，所有符合地类都是执法)的图斑量，计算不在耕保与执法范围
'''
'''
参数顺序依次为：
0、输入图斑图层
1、输入耕地图层
2、抽取权重【耕保、执法、一般、伪变化】（array）
3、是否在耕地边界处切割图形（Boolean）
4、上一次的抽取结果，用于计算重叠率（Optional）
5、上一次的重叠率要求【耕保、执法、一般、伪变化】（array）（Optional）
6、单种地类抽取（Optional）
7、单种地类抽取范围【耕地、执法、所有范围、无】（Optional）
8、输出结果
'''
inputShape = arcpy.GetParameterAsText(0)
inputArableLandShape = arcpy.GetParameterAsText(1)
extractionWeights = arcpy.GetParameter(2)
shouldClipOnBoundaries = arcpy.GetParameter(3)
lastExtraction = arcpy.GetParameterAsText(4)
overlapRatesWithLastExtraction = arcpy.GetParameter(5)
singleClass = arcpy.GetParameterAsText(6)
singleClassExtractionRange = arcpy.GetParameterAsText(7)
outputShape = arcpy.GetParameterAsText(8)

assert sum(extractionWeights) <= 1.5
assert len(extractionWeights) == 4
if lastExtraction is not None and len(lastExtraction) != 0:
    assert len(overlapRatesWithLastExtraction) == 4
    for i in overlapRatesWithLastExtraction:
        assert i <= 1

#图斑分类
zhifaCodes = [
    '1201',
    '0307B',
    '0402A',
    '05',
    '0601',
    '0602',
    '0610',
    '0710',
    '0711',
    '0712',
    '0713',
    '0714',
    '0717',
    '0719',
    '0720',
    '0721',
    '0722',
    '0729',
    '0750',
    '0760',
    '0770',
    '0790',
    '0810',
    '0821',
    '0831',
    '0832',
    '0833',
    '0839',
    '0890',
    '09',
    '10',
    '1104',
    '1107',
    '1202'
]
gengbaoCodes = [
    '0201',
    '0202',
    '0203',
    '0204',
    '0301',
    '0302',
    '0305',
    '0307',
    '0307A',
    '0307B',
    '0402',
    '0402A',
    '0402B',
    '0602',
    '0750',
    '1101',
    '1102',
    '1103',
    '1104',
    '1107'
]


#按图形位置重排
shapeFieldName = arcpy.Describe(inputShape).shapeFieldName
shapeSortByShape = os.path.join(arcpy.env.workspace,"shapeSortByShape")
arcpy.Sort_management (inputShape, shapeSortByShape, [[shapeFieldName, "ASCENDING"]], 'UL')

#耕地图斑Dissolve
dissolvedArableLandShape = os.path.join(arcpy.env.workspace,"dissolvedArableLand")
arcpy.Dissolve_management(inputArableLandShape,dissolvedArableLandShape,multi_part='SINGLE_PART')

#添加字段并写上gengbao
arcpy.AddField_management(dissolvedArableLandShape,'Scope','TEXT',field_length='10')
arcpy.CalculateField_management(dissolvedArableLandShape,'Scope','"gengbao"',expression_type="PYTHON_9.3")

#是否切割图斑判断
spatialJoinOutput = os.path.join(arcpy.env.workspace,"spatialJoinOutput")
#切割图斑
if shouldClipOnBoundaries:
    arcpy.Identity_analysis(shapeSortByShape,dissolvedArableLandShape,spatialJoinOutput)
else:
    #耕地图斑与输入图斑进行空间连接
    #设置FieldMap
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(shapeSortByShape)
    fmap = arcpy.FieldMap()
    fmap.addInputField(dissolvedArableLandShape,'Scope')
    fmap.mergeRule = 'First'
    fieldmappings.addFieldMap(fmap)
    #空间连接
    arcpy.SpatialJoin_analysis(shapeSortByShape, dissolvedArableLandShape, spatialJoinOutput, "#", "#", fieldmappings,match_option='INTERSECT')
#标记重叠图斑
if lastExtraction is not None and len(lastExtraction.strip()) != 0:
    #复制图形
    spatialJoinWithLastOutput = os.path.join(arcpy.env.workspace,"spatialJoinWithLastOutput")
    lastExtractionCopy = os.path.join(arcpy.env.workspace,"lastExtractionCopy")
    arcpy.FeatureClassToFeatureClass_conversion (lastExtraction, arcpy.env.workspace, 'lastExtractionCopy')
    arcpy.AddMessage(lastExtraction)
    arcpy.AddField_management(lastExtractionCopy,'Overlap','SHORT')
    arcpy.CalculateField_management(lastExtractionCopy,'Overlap',1,expression_type="PYTHON_9.3")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(spatialJoinOutput)
    fmap = arcpy.FieldMap()
    fmap.addInputField(lastExtractionCopy,'Overlap')
    fmap.mergeRule = 'First'
    fieldmappings.addFieldMap(fmap)
    arcpy.SpatialJoin_analysis(spatialJoinOutput, lastExtractionCopy, spatialJoinWithLastOutput, "#", "#", fieldmappings,match_option='ARE_IDENTICAL_TO')
    arcpy.Delete_management(spatialJoinOutput)
    spatialJoinOutput = spatialJoinWithLastOutput

#计算比例
totalShapesCount = int(arcpy.GetCount_management(spatialJoinOutput).getOutput(0))
totalGenbaoRecordIds = []
totalZhifaRecordIds = []
totalGeneralIds = []
totalFakeChangeRecordIds = []
totalOverlapRecordIds = []

#对图斑进行分类
oidFieldName = arcpy.Describe(spatialJoinOutput).OIDFieldName
fc_fields = arcpy.ListFields(spatialJoinOutput)
cur_fields = [field.name for field in fc_fields]
fieldQueryScheme = [oidFieldName,'TBLX','SFWBHTB','Scope']
if 'Overlap' in cur_fields:
    fieldQueryScheme.append('Overlap')
with arcpy.da.SearchCursor(spatialJoinOutput,fieldQueryScheme) as cursor:
    for row in cursor:
            #图斑是重点图斑
            if row[2].strip() == '2':
                #属于执法地类，属于执法图斑
                if row[1] in zhifaCodes:
                    totalZhifaRecordIds.append(row[0])
                else:
                    #属于耕保地类且在耕地范围内，属于耕保图斑
                    if row[1] in gengbaoCodes and row[3] == 'gengbao':
                        totalGenbaoRecordIds.append(row[0])
                    #不属于耕保地类或不在耕地范围内，属于一般图斑
                    else:
                        totalGeneralIds.append(row[0])
            #图斑是非重点图斑
            elif row[2].strip() == '1':
                totalFakeChangeRecordIds.append(row[0])
            #图斑是重叠图斑
            if 'Overlap' in cur_fields:
                if row[4] == 1:
                    totalOverlapRecordIds.append(row[0])

#计算需要抽取的图斑数量
avaliableGenbaoShapesCount = int(len(totalGenbaoRecordIds)*extractionWeights[0])
avaliableZhifaShapesCount = int(len(totalZhifaRecordIds)*extractionWeights[1])
avaliableGeneralShapesCount = int(len(totalGeneralIds)*extractionWeights[2])
avaliableFakeChangeShapesCount = int(len(totalFakeChangeRecordIds)*extractionWeights[3])

#计算重复的图斑
#将重复的图斑ID提取出来，放到新列表中，然后在源列表中删除该图斑ID
duplicatedGengbaoIds = []
duplicatedZhifaIds = []
duplicatedGeneralIds = []
duplicatedFakeChangeIds = []
duplicatedGengbaoShapesCount = 0
duplicatedZhifaShapesCount = 0
duplicatedGeneralShapesCount = 0
duplicatedFakeChangeShapesCount = 0
if len(lastExtraction.strip()) != 0:
    for id in totalOverlapRecordIds:
        if id in totalGenbaoRecordIds:
            duplicatedGengbaoIds.append(id)
            totalGenbaoRecordIds.remove(id)
        elif id in totalZhifaRecordIds:
            duplicatedZhifaIds.append(id)
            totalZhifaRecordIds.remove(id)
        elif id in totalGeneralIds:
            duplicatedGeneralIds.append(id)
            totalGeneralIds.remove(id)
        elif id in totalFakeChangeRecordIds:
            duplicatedFakeChangeIds.append(id)
            totalFakeChangeRecordIds.remove(id)
    duplicatedGengbaoShapesCount = int(len(duplicatedGengbaoIds)*overlapRatesWithLastExtraction[0])
    duplicatedZhifaShapesCount = int(len(duplicatedZhifaIds)*overlapRatesWithLastExtraction[1])
    duplicatedGeneralShapesCount = int(len(duplicatedGeneralIds)*overlapRatesWithLastExtraction[2])
    duplicatedFakeChangeShapesCount = int(len(duplicatedFakeChangeIds)*overlapRatesWithLastExtraction[3])

#乱序
random.shuffle(totalGenbaoRecordIds)
random.shuffle(totalZhifaRecordIds)
random.shuffle(totalGeneralIds)
random.shuffle(totalFakeChangeRecordIds)

#将带抽取图斑id放入列表
#如果需要重复，首先根据输入的百分比计算实际重复的图斑数；然后在各个分表中截断；阶段后再补充需要重复的ID
totalSelection = []
GenBaoSelection = totalGenbaoRecordIds[:avaliableGenbaoShapesCount-duplicatedGengbaoShapesCount]
GenBaoSelection.extend(duplicatedGengbaoIds[:duplicatedGengbaoShapesCount])
ZhifaSelection = totalZhifaRecordIds[:avaliableZhifaShapesCount-duplicatedZhifaShapesCount]
ZhifaSelection.extend(duplicatedZhifaIds[:duplicatedZhifaShapesCount])
GeneralSelection = totalGeneralIds[:avaliableGeneralShapesCount-duplicatedGeneralShapesCount]
GeneralSelection.extend(duplicatedGeneralIds[:duplicatedGeneralShapesCount])
FakeChangeSelection = totalFakeChangeRecordIds[:avaliableFakeChangeShapesCount-duplicatedFakeChangeShapesCount]
FakeChangeSelection.extend(duplicatedFakeChangeIds[:duplicatedFakeChangeShapesCount])
totalSelection.extend(GenBaoSelection)
totalSelection.extend(ZhifaSelection)
totalSelection.extend(GeneralSelection)
totalSelection.extend(FakeChangeSelection)

#迭代图层并根据图层id抽取图形
with arcpy.da.UpdateCursor(spatialJoinOutput,[oidFieldName,'Scope']) as cursor:
    for row in cursor:
        if row[0] in totalSelection:
            if row[0] in ZhifaSelection:
                row[1] = 'ZF'
                ZhifaSelection.remove(row[0])
            elif row[0] in GenBaoSelection:
                row[1] = 'GB'
                GenBaoSelection.remove(row[0])
            elif row[0] in GeneralSelection:
                row[1] = 'YB'
                GeneralSelection.remove(row[0])
            elif row[0] in FakeChangeSelection:
                row[1] = 'WBH'
                FakeChangeSelection.remove(row[0])
            totalSelection.remove(row[0])
        else:
            row[1] = None
        cursor.updateRow(row)
        if len(totalSelection) == 0:
            break

#根据属性字段抽取图斑
selectedOutput = os.path.join(arcpy.env.workspace,"selectedOutput")
arcpy.Select_analysis(spatialJoinOutput,selectedOutput,"\"Scope\" IS NOT NULL AND \"Scope\" <> '' AND \"Scope\" <> 'gengbao'")
if 'Overlap' in cur_fields:
    arcpy.DeleteField_management(selectedOutput,"Overlap")

#将结果输出到文件
arcpy.Copy_management(selectedOutput,outputShape)

#删除过程图层
try:
    arcpy.Delete_management(spatialJoinOutput)
except:
    pass
try:
    arcpy.Delete_management(selectedOutput)
except:
    pass
try:
    arcpy.Delete_management(dissolvedArableLandShape)
except:
    pass
try:
    arcpy.Delete_management(lastExtractionCopy)
except: 
    pass
try:
    arcpy.Delete_management(shapeSortByShape)
except:
    pass
# arcpy.AddMessage(totalShapesCount)
# arcpy.AddMessage(int(totalShapesCount*0.1))
# arcpy.AddMessage(int(len(totalGenbaoRecordIds)*0.4))
# arcpy.AddMessage(int(len(totalZhifaRecordIds)*0.4))
# arcpy.AddMessage(int(len(totalGeneralIds)*0.1))
# arcpy.AddMessage(int(len(totalFakeChangeRecordIds)*0.1))




