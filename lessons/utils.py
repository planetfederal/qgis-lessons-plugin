from PyQt4 import QtCore, QtGui
from qgis.utils import iface
from qgis.core import *
import os




def layerFromName(name):
    '''
    Returns the layer from the current project with the passed name
    Returns None if no layer with that name is found
    If several layers with that name exist, only the first one is returned
    '''
    layers = QgsMapLayerRegistry.instance().mapLayers().values()
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
            raise RuntimeError('Could not load layer: ' + unicode(filename))

    return qgslayer

def loadLayerNoCrsDialog(filename, name=None):
    '''
    Tries to load a layer from the given file
    Same as the loadLayer method, but it does not ask for CRS, regardless of current
    configuration in QGIS settings
    '''
    settings = QtCore.QSettings()
    prjSetting = settings.value('/Projections/defaultBehaviour')
    settings.setValue('/Projections/defaultBehaviour', '')
    layer = loadLayer(filename, name)
    settings.setValue('/Projections/defaultBehaviour', prjSetting)
    return layer

def menuFromName(menuName):
    def getMenuPath(menu):
        path = []
        while isinstance(menu, QtGui.QMenu):
            path.append(menu.title().replace("&",""))
            menu = menu.parent()
        return "/".join(path[::-1])

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

    for action, menu in menuActions:
        name = getMenuPath(menu) + "/" + action.text().replace("&","")
        if name == menuName:
            return menu, action

def unfoldMenu(menu, action):
    menus = []
    while isinstance(menu, QtGui.QMenu):
        menus.append(menu)
        menu = menu.parent()
    for m in menus[::-1]:
        m.setVisible(True)
    m.setActiveAction(action)

def openProject(projectFile):
    if projectFile != QgsProject.instance().fileName():
        iface.addProject(projectFile)

_dialog = None

class ExecutorThread(QtCore.QThread):

    finished = QtCore.pyqtSignal()

    def __init__(self, func):
        QtCore.QThread.__init__(self, iface.mainWindow())
        self.func = func
        self.returnValue = None
        self.exception = None

    def run (self):
        try:
            self.returnValue = self.func()
        except Exception, e:
            self.exception = e
        finally:
            self.finished.emit()

def execute(func, message = None):
    '''
    Executes a lengthy tasks in a separate thread and displays a waiting dialog if needed.
    Sets the cursor to wait cursor while the task is running.

    This function does not provide any support for progress indication

    :param func: The function to execute.

    :param message: The message to display in the wait dialog. If not passed, the dialog won't be shown
    '''
    global _dialog
    cursor = QtGui.QApplication.overrideCursor()
    waitCursor = (cursor is not None and cursor.shape() == QtCore.Qt.WaitCursor)
    dialogCreated = False
    try:
        QtCore.QCoreApplication.processEvents()
        if not waitCursor:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        if message is not None:
            t = ExecutorThread(func)
            loop = QtCore.QEventLoop()
            t.finished.connect(loop.exit, QtCore.Qt.QueuedConnection)
            if _dialog is None:
                dialogCreated = True
                _dialog = QtGui.QProgressDialog(message, "Running", 0, 0, iface.mainWindow())
                _dialog.setWindowTitle("Running")
                _dialog.setWindowModality(QtCore.Qt.WindowModal);
                _dialog.setMinimumDuration(1000)
                _dialog.setMaximum(100)
                _dialog.setValue(0)
                _dialog.setMaximum(0)
                _dialog.setCancelButton(None)
            else:
                oldText = _dialog.labelText()
                _dialog.setLabelText(message)
            QtGui.QApplication.processEvents()
            t.start()
            loop.exec_(flags = QtCore.QEventLoop.ExcludeUserInputEvents)
            if t.exception is not None:
                raise t.exception
            return t.returnValue
        else:
            return func()
    finally:
        if message is not None:
            if dialogCreated:
                _dialog.reset()
                _dialog = None
            else:
                _dialog.setLabelText(oldText)
        if not waitCursor:
            QtGui.QApplication.restoreOverrideCursor()
        QtCore.QCoreApplication.processEvents()