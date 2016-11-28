# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#

def classFactory(iface):
    from examplelessons.plugin import LessonsCollection
    return LessonsCollection(iface)
