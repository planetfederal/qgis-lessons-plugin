# -*- coding: utf-8 -*-
import os
import glob
from lessons.lesson import lessonFromYamlFile

lessons = []

def addLessonModule(module):
    if "lesson" in dir(module):
        lessons.append(module.lesson)

def addLessonsFolder(folder):
    def isPackage(d):
        d = os.path.join(folder, d)
        return os.path.isdir(d) and glob.glob(os.path.join(d, '__init__.py*'))
    def isYamlLessonFolder(d):
        d = os.path.join(folder, d)
        return os.path.isdir(d) and glob.glob(os.path.join(d, 'lesson.yaml'))
    subname = os.path.basename(folder)
    name = os.path.basename(os.path.dirname(folder))
    packages = filter(isPackage, os.listdir(folder))
    for p in packages:
        m = __import__(".".join([name,subname,p]), fromlist="dummy")
        addLessonModule(m)
    folders = filter(isYamlLessonFolder, os.listdir(folder))
    for f in folders:
        lessons.append(lessonFromYamlFile(os.path.join(folder, f, "lesson.yaml")))


def classFactory(iface):
    from plugin import LessonsPlugin
    return LessonsPlugin(iface)