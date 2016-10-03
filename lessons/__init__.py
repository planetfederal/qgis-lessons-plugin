# -*- coding: utf-8 -*-
import os
import glob
import zipfile
from lessons.lesson import lessonFromYamlFile
from PyQt4.QtCore import QDir
from qgis.core import QgsApplication

lessons = []

def _addLesson(toAdd):
    for lesson in lessons:
        if lesson.name == toAdd.name and lesson.group == toAdd.group:
            return
    lessons.append(toAdd)

def _removeLesson(toRemove):
    for lesson in lessons[::-1]:
        if lesson.name == toRemove.name and lesson.group == toRemove.group:
            lessons.remove(lesson)

def addLessonModule(module):
    if "lesson" in dir(module):
        _addLesson(module.lesson)

def removeLessonModule(module):
    if "lesson" in dir(module):
        _removeLesson(module.lesson)

def isPackage(folder, subfolder):
    path = os.path.join(folder, subfolder)
    return os.path.isdir(path) and glob.glob(os.path.join(path, '__init__.py*'))

def isYamlLessonFolder(folder, subfolder):
    path = os.path.join(folder, subfolder)
    return os.path.isdir(path) and glob.glob(os.path.join(path, 'lesson.yaml'))

def addLessonsFolder(folder):
    subname = os.path.basename(folder)
    name = os.path.basename(os.path.dirname(folder))
    packages = filter(lambda x: isPackage(folder, x), os.listdir(folder))
    for p in packages:
        m = __import__(".".join([name,subname,p]), fromlist="dummy")
        addLessonModule(m)
    folders = filter(lambda x: isYamlLessonFolder(folder, x), os.listdir(folder))
    for f in folders:
        _addLesson(lessonFromYamlFile(os.path.join(folder, f, "lesson.yaml")))

def removeLessonsFolder(folder):
    subname = os.path.basename(folder)
    name = os.path.basename(os.path.dirname(folder))
    packages = filter(lambda x: isPackage(folder, x), os.listdir(folder))
    for p in packages:
        m = __import__(".".join([name,subname,p]), fromlist="dummy")
        removeLessonModule(m)
    folders = filter(lambda x: isYamlLessonFolder(folder, x), os.listdir(folder))
    for f in folders:
        _removeLesson(lessonFromYamlFile(os.path.join(folder, f, "lesson.yaml")))

def lessonFromName(group, name):
    for lesson in lessons:
        if lesson.group == group and lesson.name == name:
            return lesson


def lessonsFolder():
    folder = os.path.join(QgsApplication.qgisSettingsDirPath(), 'python', 'plugins', 'lessons', '_lessons')
    if not QDir(folder).exists():
        QDir().mkpath(folder)

    return QDir.toNativeSeparators(folder)

def installLessonsFromZipFile(path):
    with zipfile.ZipFile(path, "r") as z:
        z.extractall(lessonsFolder())
        lessons = list(set([os.path.split(os.path.dirname(x))[0] for x in z.namelist()]))
        for lesson in lessons:
            addLessonsFolder(os.path.join(lessonsFolder, lesson))

def classFactory(iface):
    from plugin import LessonsPlugin
    return LessonsPlugin(iface)