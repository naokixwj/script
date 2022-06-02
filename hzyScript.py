import random
import arcpy
import os
'''
�������1��ԭʼ����
�������2�����ص㡢���ص㡢�����ֽ���ͼ�߳�ȡ
�������3��

ִ�����̣�
1�������ݽ��а�ͼ������
2��ͨ�����ط�Χ��������ֵд������ͼ��
2������������ȼ�����ͼ������Ȼ����������Χͼ����������ִ��(ִ���ǲ����Ǳ߽�ģ����з��ϵ��඼��ִ��)��ͼ���������㲻�ڸ�����ִ����Χ
'''
'''
����˳������Ϊ��
0������ͼ��ͼ��
1���������ͼ��
2����ȡȨ�ء�������ִ����һ�㡢α�仯����array��
3���Ƿ��ڸ��ر߽紦�и�ͼ�Σ�Boolean��
4����һ�εĳ�ȡ��������ڼ����ص��ʣ�Optional��
5����һ�ε��ص���Ҫ�󡾸�����ִ����һ�㡢α�仯����array����Optional��
6�����ֵ����ȡ��Optional��
7�����ֵ����ȡ��Χ�����ء�ִ�������з�Χ���ޡ���Optional��
8��������
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

#ͼ�߷���
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


#��ͼ��λ������
shapeFieldName = arcpy.Describe(inputShape).shapeFieldName
shapeSortByShape = os.path.join(arcpy.env.workspace,"shapeSortByShape")
arcpy.Sort_management (inputShape, shapeSortByShape, [[shapeFieldName, "ASCENDING"]], 'UL')

#����ͼ��Dissolve
dissolvedArableLandShape = os.path.join(arcpy.env.workspace,"dissolvedArableLand")
arcpy.Dissolve_management(inputArableLandShape,dissolvedArableLandShape,multi_part='SINGLE_PART')

#����ֶβ�д��gengbao
arcpy.AddField_management(dissolvedArableLandShape,'Scope','TEXT',field_length='10')
arcpy.CalculateField_management(dissolvedArableLandShape,'Scope','"gengbao"',expression_type="PYTHON_9.3")

#�Ƿ��и�ͼ���ж�
spatialJoinOutput = os.path.join(arcpy.env.workspace,"spatialJoinOutput")
#�и�ͼ��
if shouldClipOnBoundaries:
    arcpy.Identity_analysis(shapeSortByShape,dissolvedArableLandShape,spatialJoinOutput)
else:
    #����ͼ��������ͼ�߽��пռ�����
    #����FieldMap
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(shapeSortByShape)
    fmap = arcpy.FieldMap()
    fmap.addInputField(dissolvedArableLandShape,'Scope')
    fmap.mergeRule = 'First'
    fieldmappings.addFieldMap(fmap)
    #�ռ�����
    arcpy.SpatialJoin_analysis(shapeSortByShape, dissolvedArableLandShape, spatialJoinOutput, "#", "#", fieldmappings,match_option='INTERSECT')
#����ص�ͼ��
if lastExtraction is not None and len(lastExtraction.strip()) != 0:
    #����ͼ��
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

#�������
totalShapesCount = int(arcpy.GetCount_management(spatialJoinOutput).getOutput(0))
totalGenbaoRecordIds = []
totalZhifaRecordIds = []
totalGeneralIds = []
totalFakeChangeRecordIds = []
totalOverlapRecordIds = []

#��ͼ�߽��з���
oidFieldName = arcpy.Describe(spatialJoinOutput).OIDFieldName
fc_fields = arcpy.ListFields(spatialJoinOutput)
cur_fields = [field.name for field in fc_fields]
fieldQueryScheme = [oidFieldName,'TBLX','SFWBHTB','Scope']
if 'Overlap' in cur_fields:
    fieldQueryScheme.append('Overlap')
with arcpy.da.SearchCursor(spatialJoinOutput,fieldQueryScheme) as cursor:
    for row in cursor:
            #ͼ�����ص�ͼ��
            if row[2].strip() == '2':
                #����ִ�����࣬����ִ��ͼ��
                if row[1] in zhifaCodes:
                    totalZhifaRecordIds.append(row[0])
                else:
                    #���ڸ����������ڸ��ط�Χ�ڣ����ڸ���ͼ��
                    if row[1] in gengbaoCodes and row[3] == 'gengbao':
                        totalGenbaoRecordIds.append(row[0])
                    #�����ڸ���������ڸ��ط�Χ�ڣ�����һ��ͼ��
                    else:
                        totalGeneralIds.append(row[0])
            #ͼ���Ƿ��ص�ͼ��
            elif row[2].strip() == '1':
                totalFakeChangeRecordIds.append(row[0])
            #ͼ�����ص�ͼ��
            if 'Overlap' in cur_fields:
                if row[4] == 1:
                    totalOverlapRecordIds.append(row[0])

#������Ҫ��ȡ��ͼ������
avaliableGenbaoShapesCount = int(len(totalGenbaoRecordIds)*extractionWeights[0])
avaliableZhifaShapesCount = int(len(totalZhifaRecordIds)*extractionWeights[1])
avaliableGeneralShapesCount = int(len(totalGeneralIds)*extractionWeights[2])
avaliableFakeChangeShapesCount = int(len(totalFakeChangeRecordIds)*extractionWeights[3])

#�����ظ���ͼ��
#���ظ���ͼ��ID��ȡ�������ŵ����б��У�Ȼ����Դ�б���ɾ����ͼ��ID
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

#����
random.shuffle(totalGenbaoRecordIds)
random.shuffle(totalZhifaRecordIds)
random.shuffle(totalGeneralIds)
random.shuffle(totalFakeChangeRecordIds)

#������ȡͼ��id�����б�
#�����Ҫ�ظ������ȸ�������İٷֱȼ���ʵ���ظ���ͼ������Ȼ���ڸ����ֱ��нضϣ��׶κ��ٲ�����Ҫ�ظ���ID
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

#����ͼ�㲢����ͼ��id��ȡͼ��
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

#���������ֶγ�ȡͼ��
selectedOutput = os.path.join(arcpy.env.workspace,"selectedOutput")
arcpy.Select_analysis(spatialJoinOutput,selectedOutput,"\"Scope\" IS NOT NULL AND \"Scope\" <> '' AND \"Scope\" <> 'gengbao'")
if 'Overlap' in cur_fields:
    arcpy.DeleteField_management(selectedOutput,"Overlap")

#�����������ļ�
arcpy.Copy_management(selectedOutput,outputShape)

#ɾ������ͼ��
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




