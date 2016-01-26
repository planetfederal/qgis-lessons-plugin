
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from lessonwidget import LessonWidget
from lessonselector import LessonSelector
import os
import lessons
from examplelessons import exporttogeojson

class LessonsPlugin:

	def __init__(self, iface):
		self.iface = iface
		self.lessonWidget = None

		lessons.addLessonModule(exporttogeojson)

	def unload(self):
		self.iface.removePluginMenu(u"Lessons", self.action)
		del self.action
		if self.toolbar:
			self.toolbar.setVisible(False)
			del self.toolbar

	def initGui(self):
		lessonIcon = QtGui.QIcon(os.path.dirname(__file__) + '/lesson.gif')
		self.action = QtGui.QAction(lessonIcon, "Start lessons", self.iface.mainWindow())
		self.action.triggered.connect(self.start)
		self.iface.addPluginToMenu(u"Lessons", self.action)
		self.lessonwidget = None


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
			self.lessonWidget.lessonFinished.connect(lessonFinished)



