# -*- coding: utf-8 -*-
import os
import glob

lessons = []

def addLessonModule(module):
    if "lesson" in dir(module):
        lessons.append(module.lesson)

def addLessonsFolder(folder):
    def isPackage(d):
        d = os.path.join(folder, d)
        return os.path.isdir(d) and glob.glob(os.path.join(d, '__init__.py*'))
    folderName = os.path.basename(folder)
    packages = filter(isPackage, os.listdir(folder))

    for p in packages:
        m = __import__(__name__.split(".")[0] + "." + folderName + "." + p, fromlist="dummy")
        addLessonModule(m)

def classFactory(iface):
    from plugin import LessonsPlugin
    return LessonsPlugin(iface)