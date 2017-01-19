# -*- coding: utf-8 -*-
from __future__ import absolute_import
import site
import os
site.addsitedir(os.path.abspath(os.path.dirname(__file__) + '/ext-libs'))
import imp
import glob
import zipfile
from lessons.lesson import lessonFromYamlFile
from qgis.PyQt.QtCore import QDir
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


def lessonsFolder():
    folder = os.path.join(os.path.dirname(__file__), '_lessons')
    if not QDir(folder).exists():
        QDir().mkpath(folder)

    return folder

def addLessonFolderFromLessonPluginFolder(group, lesson):
    try:
        f = os.path.join(lessonsFolder(), group, lesson, "__init__.py")
        if os.path.exists(f):
            m = imp.load_source("%s.%s" % (group, lesson), f)
            addLessonModule(m)
    except:
        pass

    if isYamlLessonFolder(os.path.join(lessonsFolder(), group), lesson):
        lesson = lessonFromYamlFile(os.path.join(lessonsFolder(), group, lesson, "lesson.yaml"))
        if lesson:
            _addLesson(lesson)


def installLessonsFromZipFile(path):
    group = os.path.basename(path).split(".")[0]
    with zipfile.ZipFile(path, "r") as z:
        folder = os.path.join(lessonsFolder(), group)
        if not QDir(folder).exists():
            QDir().mkpath(folder)
        z.extractall(folder)
        lessons = list(set([os.path.split(os.path.dirname(x))[0] for x in z.namelist()]))
        for lesson in lessons:
            addLessonFolderFromLessonPluginFolder(group, lesson)


def loadLessons():
    for folder in os.listdir(lessonsFolder()):
        if os.path.isdir(os.path.join(lessonsFolder(), folder)):
            for subfolder in os.listdir(os.path.join(lessonsFolder(), folder)):
                if os.path.isdir(os.path.join(lessonsFolder(), folder, subfolder)):
                    addLessonFolderFromLessonPluginFolder(folder, subfolder)

def classFactory(iface):
    from .plugin import LessonsPlugin
    return LessonsPlugin(iface)
