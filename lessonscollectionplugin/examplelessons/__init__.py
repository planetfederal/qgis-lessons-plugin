# -*- coding: utf-8 -*-

def classFactory(iface):
    from plugin import LessonsCollection
    return LessonsCollection(iface)
