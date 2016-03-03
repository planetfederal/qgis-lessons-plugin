# -*- coding: utf-8 -*-

def classFactory(iface):
    from plugin import LessonsCreator
    return LessonsCreator(iface)
