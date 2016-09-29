# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
from lessons.lesson import Lesson, Step
from lessons.utils import *
from qgis.utils import iface
from lessons import addLessonModule

def isLayerActive():
    layer = iface.activeLayer()
    return layer is not None and layer.name() == "points"

def setActiveLayer():
    layer = layerFromName("points")
    iface.setActiveLayer(layer)

lesson = Lesson("Export to geojson", "Basic lessons", "lesson.html")
lesson.addStep("Set 'points' layer as active layer", "activelayer.html",
               function = setActiveLayer, endcheck=isLayerActive, steptype=Step.MANUALSTEP)
lesson.addMenuClickStep("Layer/Save As...")
lesson.addStep("Save the file as geojson", "saveas.html", steptype=Step.MANUALSTEP)
lesson.addNextLesson("Basic lessons", "Export to geojson (yaml example)")

