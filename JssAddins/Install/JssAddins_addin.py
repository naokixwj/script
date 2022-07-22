# -*- coding: UTF-8 -*-
import arcpy
import pythonaddins

def getCornerPoints(extent):
    """
        X 为纵坐标 Y 为横坐标
        判断任意一点是否在框内
        1. 判断图形框任意一点是否在显示框的范围内
        2. 判断显示框任意一点是否在图形框的范围内
        3. 如果1和2都判断为否，则两图形无重叠
    """
    UL = [extent.XMax,extent.YMin]
    UR = [extent.XMax,extent.YMax]
    LL = [extent.XMin,extent.YMin]
    LR = [extent.XMin,extent.YMax]
    

class ButtonClass22(object):
    """Implementation for JssAddins_addin.button (Button)"""
    # "C:\Python27\ArcGIS10.5\python.exe"
    def __init__(self):
        self.enabled = True
        self.currentLyrs = []
        self.checked = False
    def onClick(self):
        self.currentLyrs = []
        mxd = arcpy.mapping.MapDocument("current")
        if 1 == 1:
            lyrs = arcpy.mapping.ListLayers(mxd)
            for lyr in lyrs:
                if lyr.isGroupLayer and lyr.name.lower() == 'yxz':
                    lyrs2 = arcpy.mapping.ListLayers(lyr)
                    for lyr2 in lyrs2:
                        if lyr2 != lyr:
                            self.currentLyrs.append([lyr2,lyr2.getExtent()])
        if len(self.currentLyrs) == 0:
            pythonaddins.MessageBox(u"未发现可操作图层，或者yxz图层组不存在",u"未发现可用图层")
        df_extent = mxd.activeDataFrame.extent
        dfXMIN = df_extent.XMin
        dfXMAX = df_extent.XMax
        dfYMIN = df_extent.YMin
        dfYMAX = df_extent.YMax
        for item in self.currentLyrs:
            XMIN = item[1].XMin
            XMAX = item[1].XMax
            YMIN = item[1].YMin
            YMAX = item[1].YMax
            item[0].visible = False
            # Map frame in feature frame
            if XMIN <= dfXMIN <= XMAX or XMIN <= dfXMAX <= XMAX:
                if YMIN <= dfYMIN <= YMAX or YMIN <= dfYMAX <= YMAX:
                    item[0].visible = True
            # Feature frame in map frame
            if item[0].visible != True:
                if dfXMIN <= XMIN <= dfXMAX or dfXMIN <= XMAX <= dfXMAX:
                    if dfYMIN <= YMIN <= dfYMAX or dfYMIN <= YMAX <= dfYMAX:
                        item[0].visible = True
            # if item[0].visible != True:
            #     if XMAX <= dfXMAX or XMIN >= dfXMIN:
            #         if YMAX <= dfYMAX or YMIN >= dfYMIN:
            #             item[0].visible = True
            # if item[0].visible != True:
            #     if YMAX <= dfYMAX and YMIN >= dfYMIN:
            #         if XMAX <= dfXMAX or XMIN >= dfXMIN:
            #             item[0].visible = True
        arcpy.RefreshActiveView()