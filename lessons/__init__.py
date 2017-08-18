# -*- coding: utf-8 -*-
from __future__ import absolute_import
import site
import os
site.addsitedir(os.path.abspath(os.path.dirname(__file__) + '/ext-libs'))
import imp
import glob
import zipfile
from lessons.lesson import lessonFromYamlFile
from lessons.utils import lessonsBaseFolder
from qgis.PyQt.QtCore import QDir
from qgis.core import QgsApplication

lessons = []
groups = {}

def addGroup(name, description):
    global groups
    groups[name] = description

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

def addLessonsFolder(folder, pluginName):
    packages = [x for x in os.listdir(folder) if os.path.isdir(os.path.join(folder, x))]
    for p in packages:
        try:
            tokens = folder.split(os.sep)
            moduleTokens = tokens[tokens.index(pluginName):] + [p]
            moduleName = ".".join(moduleTokens)
            m = __import__(moduleName, fromlist="dummy")
            addLessonModule(m)
        except:
            pass
    folders = [x for x in os.listdir(folder) if isYamlLessonFolder(folder, x)]
    for f in folders:
        lesson = lessonFromYamlFile(os.path.join(folder, f, "lesson.yaml"))
        if lesson:
            _addLesson(lesson)


def removeLessonsFolder(folder, pluginName):
    packages = [x for x in os.listdir(folder) if isPackage(folder, x)]
    for p in packages:
        try:
            tokens = folder.split(os.sep)
            moduleTokens = tokens[tokens.index(pluginName):] + [p]
            moduleName = ".".join(moduleTokens)
            m = __import__(moduleName, fromlist="dummy")
            removeLessonModule(m)
        except:
            pass
    folders = [x for x in os.listdir(folder) if isYamlLessonFolder(folder, x)]
    for f in folders:
        lesson = lessonFromYamlFile(os.path.join(folder, f, "lesson.yaml"))
        if lesson:
            _removeLesson(lesson)


def lessonFromName(group, name):
    for lesson in lessons:
        if lesson.group == group and lesson.name == name:
            return lesson

# maintained this fuction to does not change plugin api from external calls
# it can be substituted directly with lessonsBaseFolder()
def lessonsFolder():
    return lessonsBaseFolder()


def installLessonsFromZipFile(path):
    group = os.path.basename(path).split(".")[0]
    with zipfile.ZipFile(path, "r") as z:
        folder = os.path.join(lessonsFolder(), group)
        if not QDir(folder).exists():
            QDir().mkpath(folder)
        z.extractall(folder)

        loadLessons()


def loadLessons():
    for folder in os.listdir(lessonsFolder()):
        if os.path.isdir(os.path.join(lessonsFolder(), folder)):
            groupFiles = [os.path.join(lessonsFolder(), folder, f) for f in ["group.html", "group.md"]]
            for groupFile in groupFiles:
                if os.path.exists(groupFile):
                    groups[folder.replace("_", " ")] = groupFile
                    break
            for subfolder in os.listdir(os.path.join(lessonsFolder(), folder)):
                if os.path.isdir(os.path.join(lessonsFolder(), folder, subfolder)):
                    try:
                        f = os.path.join(lessonsFolder(), folder, subfolder, "__init__.py")
                        if os.path.exists(f):
                            m = imp.load_source("%s.%s" % (folder, subfolder), f)
                            addLessonModule(m)
                    except:
                        pass
                    if isYamlLessonFolder(os.path.join(lessonsFolder(), folder), subfolder):
                        lesson = lessonFromYamlFile(os.path.join(lessonsFolder(), folder, subfolder, "lesson.yaml"))
                        if lesson:
                            _addLesson(lesson)


def classFactory(iface):
    from .plugin import LessonsPlugin
    return LessonsPlugin(iface)
