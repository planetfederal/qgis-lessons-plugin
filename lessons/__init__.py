# -*- coding: utf-8 -*-

lessons = []

def addLessonModule(module):
    if "lesson" in dir(module):
        lessons.append(module.lesson)

def classFactory(iface):
    from plugin import LessonsPlugin
    return LessonsPlugin(iface)