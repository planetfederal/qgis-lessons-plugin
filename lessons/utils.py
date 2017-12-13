# -*- coding: utf-8 -*-

from builtins import str

import os
import re
import time
import shutil
import threading

from qgis.PyQt.QtCore import QDir, QSettings, Qt, QLocale, QTimer
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtWidgets import QMenu, QApplication, QDialog

from qgis.core import (QgsMapLayer,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsApplication,
                       QgsProject)
from qgis.utils import iface, plugins

from qgiscommons2.settings import pluginSetting, setPluginSetting

try:
    QgsProject.instance().mapLayers()
    mapRegistry = QgsProject.instance()
except: 
    from qgis.core import QgsMapLayerRegistry
    mapRegistry = QgsMapLayerRegistry.instance()
    
def layerFromName(name):
    """ Returns the layer from the current project with the passed name
    Returns None if no layer with that name is found
    If several layers with that name exist, only the first one is returned
    """
    layers = list(mapRegistry.mapLayers().values())
    for layer in layers:
        if layer.name() == name:
            return layer


def loadLayer(filename, name = None):
    """ Tries to load a layer from the given file

    :param filename: the path to the file to load.
    :param name: the name to use for adding the layer to the current project.
           If not passed or None, it will use the filename basename
    """
    name = name or os.path.splitext(os.path.basename(filename))[0]
    qgslayer = QgsVectorLayer(filename, name, "ogr")
    if not qgslayer.isValid():
        qgslayer = QgsRasterLayer(filename, name)
        if not qgslayer.isValid():
            raise RuntimeError("Could not load layer: {}".format(filename))

    return qgslayer


def loadLayerNoCrsDialog(filename, name=None):
    """ Tries to load a layer from the given file
    Same as the loadLayer method, but it does not ask for CRS, regardless of
    the current configuration in QGIS settings

    :param filename: the path to the file to load.
    :param name: the name to use for adding the layer to the current project.
           If not passed or None, it will use the filename basename
    """
    settings = QSettings()
    prjSetting = settings.value("/Projections/defaultBehaviour")
    settings.setValue("/Projections/defaultBehaviour", "")
    layer = loadLayer(filename, name)
    settings.setValue("/Projections/defaultBehaviour", prjSetting)
    return layer


def getMenuPath(menu):
    path = []
    while isinstance(menu, QMenu):
        path.append(menu.title().replace("&", ""))
        menu = menu.parent()
    return "/".join(path[::-1])


def getAllMenus():
    def getActions(action, menu):
        menuActions = []
        submenu = action.menu()
        if submenu is None:
            menuActions.append((action, menu))
            return menuActions
        else:
            actions = submenu.actions()
            for subaction in actions:
                if subaction.menu() is not None:
                    menuActions.extend(getActions(subaction, subaction.menu()))
                elif not subaction.isSeparator():
                    menuActions.append((subaction, submenu))

        return menuActions

    menuActions = []
    actions = iface.mainWindow().menuBar().actions()
    for action in actions:
        menuActions.extend(getActions(action, None))

    return menuActions


def menuFromName(menuName):
    menuActions = getAllMenus()
    shortMenuName = re.match(r"(.*\/)?(.*\/.*)$", menuName).group(2)
    for action, menu in menuActions:
        name = getMenuPath(menu) + "/" + action.text().replace("&", "")
        if re.match(r"(.*\/)?(.*\/.*)$", name).group(2) == shortMenuName:
            return menu, action


def getMenuPaths():
    menuActions = getAllMenus()
    return [getMenuPath(menu) + "/" + action.text().replace("&", "") for action, menu in menuActions]


def lessonDataFolder(lessonFolderName):
    """ Returns the folder where to store lessons data. It is created
    inside the lessonPluginBaseFolder().
    """
    folder = os.path.join(lessonPluginBaseFolder(), "data", lessonFolderName)
    if not QDir(folder).exists():
        QDir().mkpath(folder)

    return QDir.toNativeSeparators(folder)


def lessonsBaseFolder():
    """Returns the folder where to store lessons. It is created
    inside the lessonPluginBaseFolder().
    """
    folder = os.path.join(lessonPluginBaseFolder(), "lessons")
    if not QDir(folder).exists():
        QDir().mkpath(folder)

    return QDir.toNativeSeparators(folder)


def lessonPluginBaseFolder():
    """Returns the base folder where to store lessons and data.
    If only folder name specified instead of full path, the folder
    will be created in the $HOME
    """
    folder = pluginSetting("BaseFolder")
    # check if the value is only a basename and create directory in $HOME
    if not QDir(folder).exists():
        if folder == os.path.basename(folder):
            folder = os.path.join(os.path.expanduser("~"), folder)
            setPluginSetting("BaseFolder", folder)

    if not QDir(folder).exists():
        QDir().mkpath(folder)

    return QDir.toNativeSeparators(folder)


def copyLessonData(filename, lessonFolderName):
    """
    Copies file to the user qgislessons/data folder to be used in the lesson

    :param filename: name of the data file to copy
    :param lessonFolderName: folder where the data file is stored (relative to
           the lessons group)
    """
    dest = os.path.join(lessonDataFolder(lessonFolderName), os.path.basename(filename))
    shutil.copy2(filename, dest)


def unfoldMenu(menu, action):
    """Unfolds a menu and all parent menus, and highlights an entry
    in that menu
    """
    menus = []
    while isinstance(menu, QMenu):
        menus.append(menu)
        menu = menu.parent()
    for m in menus[::-1]:
        m.setVisible(True)
    m.setActiveAction(action)


def openProject(projectFile):
    folder = os.path.dirname(projectFile)
    projectName = os.path.basename(projectFile)
    tempDir = os.path.join(QDir.tempPath(), "lessons", "lesson{}".format(str(time.time())))
    dest = os.path.abspath(tempDir)
    shutil.copytree(folder, dest)
    tempProjectFile = os.path.join(dest, projectName)
    iface.addProject(tempProjectFile)


def execute(func):
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    try:
        return func()
    finally:
        QApplication.restoreOverrideCursor()


def qgisLocale():
    settings = QSettings();
    overrideLocale = settings.value("locale/overrideFlag", False, bool)
    if overrideLocale:
        return settings.value("locale/userLocale", "")
    else:
        return QLocale.system().name()[:2]


def layerActive(*args):
    """Returns True if layer with the given name is active.
    """
    layer = iface.activeLayer()
    return layer is not None and layer.name() == args[0]


def setActiveLayer(*args):
    """Makes layer with the given name active.
    NOTE: layer should be loaded into project.
    """
    layer = layerFromName(args[0])
    iface.setActiveLayer(layer)


def layerExists(layerName, typeName):
    """Returns True if layer with the given name exists and
    has specified type ("vector", "raster" or "plugin")
    """
    layers = mapRegistry.mapLayersByName(layerName)
    if len(layers) == 0:
        return False

    if typeName.lower() == "raster":
        layerType = QgsMapLayer.RasterLayer
    elif typeName.lower() == "vector":
        layerType = QgsMapLayer.VectorLayer
    else:
        layerType = QgsMapLayer.PluginLayer

    for lay in layers:
        if lay.name().lower() == layerName.lower() and lay.type() == layerType:
            return True

    return False


def checkLayerCrs(layerName, crs):
    """Returns True if CRS of the given layer matches to the given
    CRS, defined by authid.
    """
    layers = mapRegistry.mapLayersByName(layerName)
    if len(layers) == 0:
        return False

    for lay in layers:
        if lay.name().lower() == layerName.lower() and lay.crs().authid().lower() == crs.lower():
            return True

    return False


def unmodalWidget(objectName, repeatTimes=10, repeatInterval=500, step=0):
    """Look for a widget in the QGIS hierarchy to set it as
    not modal.
    If the widget is not found try agail after a "repeatInterval"
    and repeat no more that "repeatTimes"
    """

    if not objectName:
        return

    l = QgsApplication.instance().topLevelWidgets()

    for d in l:
        for dd in d.findChildren(QDialog):
            if dd.objectName() != objectName:
                continue

            dd.setWindowModality(False)
            return

    if repeatTimes == step:
        return

    # if here => not found
    QTimer.singleShot(repeatInterval,
                      lambda: unmodalWidget(objectName, repeatTimes, repeatInterval,
                                            step + 1))
