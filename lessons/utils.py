from builtins import str
# -*- coding: utf-8 -*-

import os
import re
import time
import shutil

from qgis.PyQt.QtCore import QDir, QSettings, QThread, pyqtSignal, Qt
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtWidgets import QMenu, QApplication

from qgis.core import QgsMapLayerRegistry, QgsVectorLayer, QgsRasterLayer
from qgis.utils import iface

def layerFromName(name):
    '''
    Returns the layer from the current project with the passed name
    Returns None if no layer with that name is found
    If several layers with that name exist, only the first one is returned
    '''
    layers = list(QgsMapLayerRegistry.instance().mapLayers().values())
    for layer in layers:
        if layer.name() == name:
            return layer

def loadLayer(filename, name = None):
    '''
    Tries to load a layer from the given file

    :param filename: the path to the file to load.

    :param name: the name to use for adding the layer to the current project.
    If not passed or None, it will use the filename basename
    '''
    name = name or os.path.splitext(os.path.basename(filename))[0]
    qgslayer = QgsVectorLayer(filename, name, 'ogr')
    if not qgslayer.isValid():
        qgslayer = QgsRasterLayer(filename, name)
        if not qgslayer.isValid():
            raise RuntimeError('Could not load layer: ' + str(filename))

    return qgslayer

def loadLayerNoCrsDialog(filename, name=None):
    '''
    Tries to load a layer from the given file
    Same as the loadLayer method, but it does not ask for CRS, regardless of current
    configuration in QGIS settings
    '''
    settings = QSettings()
    prjSetting = settings.value('/Projections/defaultBehaviour')
    settings.setValue('/Projections/defaultBehaviour', '')
    layer = loadLayer(filename, name)
    settings.setValue('/Projections/defaultBehaviour', prjSetting)
    return layer

def getMenuPath(menu):
    path = []
    while isinstance(menu, QMenu):
        path.append(menu.title().replace("&",""))
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
    shortMenuName = re.match(r"(.*\/)?(.*\/.*)$",menuName).group(2)
    for action, menu in menuActions:
        name = getMenuPath(menu) + "/" + action.text().replace("&","")
        if re.match(r"(.*\/)?(.*\/.*)$",name).group(2) == shortMenuName:
            return menu, action

def getMenuPaths():
    menuActions = getAllMenus()
    return [getMenuPath(menu) + "/" + action.text().replace("&","") for action,menu in menuActions]

def lessonDataFolder(lessonFolderName):
    folder = os.path.join(os.path.expanduser("~"), "qgislessonsdata", lessonFolderName)
    if not QDir(folder).exists():
        QDir().mkpath(folder)

    return QDir.toNativeSeparators(folder)

def copyLessonData(filename, lessonFolderName):
    dest = os.path.join(lessonDataFolder(lessonFolderName), os.path.basename(filename))
    shutil.copy2(filename, dest)

def unfoldMenu(menu, action):
    '''Unfolds a menu and all parent menus, and highlights an entry in that menu'''
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
    tempDir = os.path.join(QDir.tempPath(), 'lessons' , 'lesson' + str(time.time()))
    dest = os.path.abspath(tempDir)
    shutil.copytree(folder, dest)
    tempProjectFile = os.path.join(dest, projectName)
    iface.addProject(tempProjectFile)

_dialog = None

class ExecutorThread(QThread):

    finished = pyqtSignal()

    def __init__(self, func):
        QThread.__init__(self, iface.mainWindow())
        self.func = func
        self.returnValue = None
        self.exception = None

    def run (self):
        try:
            self.returnValue = self.func()
        except Exception as e:
            self.exception = e
        finally:
            self.finished.emit()

def execute(func):
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    try:
        return func()
    finally:
        QApplication.restoreOverrideCursor()
