
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from qgis.core import QgsApplication
from lessonwidget import LessonWidget
from lessonselector import LessonSelector
import os
import lessons
from lessons.utils import execute
import webbrowser
from PyQt4.QtCore import QDir
import shutil

class LessonsPlugin:

	def __init__(self, iface):
		self.iface = iface

		# add tests to test plugin
		try:
			from qgistester.tests import addTestModule
			from lessons.test import testerplugin
			addTestModule(testerplugin, "Lessons")
		except Exception as e:
			pass

		self.lessonWidget = None

	def unload(self):
		self.iface.removePluginMenu(u"Lessons", self.action)
		del self.helpAction
		self.iface.removePluginMenu(u"Lessons", self.helpAction)
		del self.helpAction

		tempDir = os.path.join(QDir.tempPath(), 'lessons' , 'lesson')
		if QDir(tempDir).exists():
			shutil.rmtree(tempDir, True)

		try:
			from qgistester.tests import removeTestModule
			from lessons.test import testerplugin
			removeTestModule(testerplugin, "Lessons")
		except Exception as e:
			pass


	def initGui(self):
		lessonIcon = QtGui.QIcon(os.path.dirname(__file__) + '/lesson.gif')
		self.action = QtGui.QAction(lessonIcon, "Start lessons", self.iface.mainWindow())
		self.action.triggered.connect(self.start)
		self.iface.addPluginToMenu(u"Lessons", self.action)
		helpIcon = QgsApplication.getThemeIcon('/mActionHelpAPI.png')
		self.helpAction = QtGui.QAction(helpIcon, "Lessons Help", self.iface.mainWindow())
		self.helpAction.setObjectName("lessonsPluginHelp")
		self.helpAction.triggered.connect(lambda: webbrowser.open_new("file://" + os.path.join(os.path.dirname(__file__), "docs", "html", "index.html")))
		self.iface.addPluginToMenu("Lessons", self.helpAction)
		self.lessonwidget = None

		lessons.loadLessons()


	def start(self):
		if self.lessonWidget is not None:
			QtGui.QMessageBox.warning(self.iface.mainWindow(), "Lesson", "A lesson is currently being run")
			return
		dlg = LessonSelector()
		dlg.exec_()
		if dlg.lesson:
			self.lessonWidget = LessonWidget(dlg.lesson)
			self.iface.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.lessonWidget)
			def lessonFinished():
				self.lessonWidget = None
				execute(dlg.lesson.cleanup)
			self.lessonWidget.lessonFinished.connect(lessonFinished)



