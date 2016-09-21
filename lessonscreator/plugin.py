# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from functools import partial
from qgis.core import *

class LessonsCreator:

	def __init__(self, iface):
		self.iface = iface

		# add tests to tester plugin
		try:
			from qgistester.tests import addTestModule
			from lessonscreator.test import testerplugin
			addTestModule(testerplugin, "LessonsCreator")
		except Exception as e:
			pass

		self.capturing = False

	def unload(self):
		self.iface.removePluginMenu(u"Lessons", self.action)
		del self.action
		del self.newStepAction

		QgsApplication.instance().focusChanged.disconnect(self.processFocusChanged)

		try:
			from qgistester.tests import removeTestModule
			from lessonscreator.test import testerplugin
			removeTestModule(testerplugin, "LessonsCreator")
		except Exception as e:
			pass


	def initGui(self):
		lessonIcon = QIcon(os.path.dirname(__file__) + '/edit.png')
		self.action = QAction(lessonIcon, "Capture lesson steps", self.iface.mainWindow())
		self.action.triggered.connect(self.toggleCapture)
		self.iface.addPluginToMenu(u"Lessons", self.action)

		QgsApplication.instance().focusChanged.connect(self.processFocusChanged)

		self.newStepAction = QAction("New step", self.iface.mainWindow() );

		self.newStepAction.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_W));
		self.newStepAction.setShortcutContext(Qt.ApplicationShortcut);
		self.newStepAction.triggered.connect(self.startNewStep)
		self.iface.mainWindow().addAction(self.newStepAction)

	connections = []
	iScreenshot = 0
	iStep = 0
	outputHtmlFile = None
	outputPyFile = None

	def startNewStep(self):
		if self.outputHtmlFile:
			self.outputHtmlFile.close()
		self.iStep += 1
		path = os.path.join(self.folder, "step_%i.html" % self.iStep)
		self.outputHtmlFile = open(path, "w")
		self.outputPyFile.write('''lesson.addStep("Step_%i", "step_%i.html", steptype=Step.MANUALSTEP)\n''' % (self.iStep, self.iStep))


	def toggleCapture(self):
		if self.capturing:
			self.action.setText("Capture lesson steps")
			self.capturing = False
			self.outputHtmlFile.close()
			self.outputPyFile.close()
			self.outputHtmlFile = None
			self.outputPyFile = None
		else:
			self.folder = QFileDialog.getExistingDirectory(self.iface.mainWindow(), "Select folder to store lesson")
			if not self.folder:
				return
			path = os.path.join(self.folder, "__init__.py")
			self.outputPyFile = open(path, "w")

			template = ("from lessons.lesson import Lesson, Step\n"
						"from lessons.utils import *\n"
						"lesson = Lesson('Lesson', 'Basic lessons', 'lesson.html')\n\n")

			self.outputPyFile.write(template)

			self.iScreenshot = 0
			self.iStep = 0
			self.updateConnections()
			self.action.setText("Stop capturing lesson steps")
			self.capturing = True
			self.startNewStep()


	def processWidgetClick(self, obj):
		if self.capturing:
			try:
				text = "Click on '%s'" % obj.text()
			except Exception,e:
				print e
				text = "Click on " + str(obj)
			self.outputHtmlFile.write("<p>%s</p>\n" % text)
			self.updateConnections()

	lastComboText = None
	def processComboNewSelection(self, combo):
		if self.capturing:
			text = "Select '%s' in '%s'" % (combo.currentText(), combo.objectName())
			if text == self.lastComboText:
				return
			self.lastComboText = text
			self.outputHtmlFile.write("<p>%s</p>\n" % text)
			self.createScreenshot(combo.parent(), combo.frameGeometry())
			self.updateConnections()

	def processCheckBoxChange(self, check):
		if self.capturing:
			if check.isChecked():
				text = "Check the '%s' checkbox" % (check.text())
			else:
				text = "Uncheck the '%s' checkbox" % (check.text())
			self.outputHtmlFile.write("<p>%s</p>\n" % text)
			self.createScreenshot(check.parent(), check.frameGeometry())

	def processMenuClick(self, action):
		if self.capturing and action.text() != "Stop capturing lesson steps":
			text = "Click on menu '%s'" % action.text()
			self.outputHtmlFile.write("<p>%s</p>\n" % text)


	def getParentWindow(self, obj):
		window = None
		try:
			parent = obj.parent()
			while parent is not None:
				if isinstance(parent, QDialog):
					window = parent
					break
				parent = parent.parent()
		except:
			window = None

		return window or QgsApplication.instance().desktop()

	def processFocusChanged(self, old, new):
		if self.capturing:
			self.updateConnections()
			if isinstance(old, QLineEdit) and old.text().strip():
				text = "Enter '%s' in textbox '%s'" % (old.text(), old.objectName())
				self.outputHtmlFile.write("<p>%s</p>\n" % text)
				self.createScreenshot(old.parent(), old.frameGeometry())
			else:
				oldParent = self.getParentWindow(old)
				newParent = self.getParentWindow(new)
				print oldParent, newParent
				if oldParent != newParent:
					self.createScreenshot(newParent)
				elif isinstance(new, (QLineEdit, QTextEdit, QComboBox, QSpinBox, QRadioButton)):
					text = "Select the '%s' widget" % (old.objectName() or str(old))
					self.outputHtmlFile.write("<p>%s</p>\n" % text)
					self.createScreenshot(new.parent(), new.frameGeometry())

	timer = None
	def _createScreenshot(self, obj, rect):
		pixmap = QPixmap.grabWindow(obj.winId()).copy()
		if rect is not None:
			painter = QPainter()
			painter.begin(pixmap)
			painter.setPen(QPen(QBrush(Qt.red), 3, Qt.DashLine))
			painter.drawRect(rect)
			painter.end()

		pixmap.save(os.path.join(self.folder,'%i.jpg' % self.iScreenshot), 'jpg')

		self.outputHtmlFile.write("<img src='%i.jpg'/>\n" % self.iScreenshot)
		self.iScreenshot += 1
		self.timer = None

	def createScreenshot(self, obj, rect = None):
		if self.capturing and self.timer is None:
			self.timer = QTimer()
			self.timer.setInterval(1000)
			self.timer.setSingleShot(True)
			self.timer.timeout.connect(lambda: self._createScreenshot(obj, rect))
			self.timer.start()

	def updateConnections(self):
		widgets=QgsApplication.instance().allWidgets()
		for w in widgets:
			if w not in self.connections:
				if isinstance(w, (QPushButton, QToolButton)):
					f = partial(self.processWidgetClick, w)
					w.clicked.connect(f)
					self.connections.append(w)
				elif isinstance(w, QComboBox):
					f = partial(self.processComboNewSelection, w)
					w.currentIndexChanged.connect(f)
					self.connections.append(w)
				elif isinstance(w, QCheckBox):
					f = partial(self.processCheckBoxChange, w)
					w.stateChanged.connect(f)
					self.connections.append(w)

		menuActions = []
		actions = self.iface.mainWindow().menuBar().actions()
		for action in actions:
			menuActions.extend(self.getActions(action, None))

		for action, menu in menuActions:
			if menu not in self.connections:
				menu.triggered.connect(self.processMenuClick)
				self.connections.append(menu)

	def getActions(self, action, menu):
		menuActions = []
		submenu = action.menu()
		if submenu is None:
			menuActions.append((action, menu))
			return menuActions
		else:
			actions = submenu.actions()
			for subaction in actions:
				if subaction.menu() is not None:
					menuActions.extend(self.getActions(subaction, subaction.menu()))
				elif not subaction.isSeparator():
					menuActions.append((subaction, submenu))

		return menuActions








