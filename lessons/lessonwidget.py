from builtins import range
# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QCoreApplication, QUrl, pyqtSignal
from qgis.PyQt.QtGui import QIcon, QTextDocument
from qgis.PyQt.QtWidgets import QListWidgetItem, QMessageBox, QListWidget
from qgis.utils import iface

from lessons.utils import execute
from lessons.lesson import Step
from lessons.lessonfinisheddialog import LessonFinishedDialog

import markdown

WIDGET, BASE = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'lessonwidget.ui'))

class LessonWidget(BASE, WIDGET):

    lessonFinished = pyqtSignal()

    def __init__(self, lesson):
        super(LessonWidget, self).__init__()
        self.setupUi(self)
        self.btnFinish.clicked.connect(self.finishLesson)
        self.btnMove.clicked.connect(self.stepFinished)
        self.btnRestart.clicked.connect(self.restartLesson)
        self.btnRunStep.clicked.connect(self.runCurrentStepFunction)
        self.init(lesson)

    def init(self, lesson):
        self.listSteps.clear()
        self.lesson = lesson
        bulletIcon = QIcon(os.path.dirname(__file__) + '/bullet.png')
        for step in lesson.steps:
            item = QListWidgetItem(step.name)
            self.listSteps.addItem(item)
            item.setHidden(step.steptype == Step.AUTOMATEDSTEP)
            item.setIcon(bulletIcon)
        self.currentStep = 0
        self.lessonNameLabel.setText("<b>Current lesson:</b> %s" % lesson.name)
        self.moveToNextStep()

    def runCurrentStepFunction(self):
        QCoreApplication.processEvents()
        step = self.lesson.steps[self.currentStep]
        self.webView.setEnabled(False)
        step.function()
        self.webView.setEnabled(True)
        self.stepFinished()

    def stepFinished(self):
        step = self.lesson.steps[self.currentStep]
        if step.endcheck is not None and not step.endcheck():
            QMessageBox.warning(self, "Lesson", "It seems that the previous step was not correctly completed."
                                                "\nPlease review and complete the instructions before moving"
                                                "\nto the next step.")
            return
        item = self.listSteps.item(self.currentStep)
        item.setBackground(Qt.white)
        if step.endsignal is not None:
            step.endsignal.disconnect(self.endSignalEmitted )
        self.currentStep += 1
        self.moveToNextStep()

    def endSignalEmitted(self, *args):
        step = self.lesson.steps[self.currentStep]
        if step.endsignalcheck is None or step.endsignalcheck(*args):
            self.stepFinished()

    def restartLesson(self):
        for i in range(self.listSteps.count()):
            item = self.listSteps.item(i)
            item.setBackground(Qt.white)
        self.currentStep = 0
        self.moveToNextStep()

    def moveToNextStep(self):
        if self.currentStep == len(self.lesson.steps):
            dlg = LessonFinishedDialog(self.lesson)
            dlg.exec_()
            if dlg.nextLesson is not None:
                self.init(dlg.nextLesson)
            else:
                self.finishLesson()
        else:
            step = self.lesson.steps[self.currentStep]
            if step.endsignal is not None:
                step.endsignal.connect(self.endSignalEmitted)
            item = self.listSteps.item(self.currentStep)
            item.setBackground(Qt.green)
            if os.path.exists(step.description):
                with open(step.description) as f:
                    html = "".join(f.readlines())
                    if step.description.endswith(".md"):
                        html = markdown.markdown(html)
                self.webView.document().setMetaInformation(QTextDocument.DocumentUrl,
                                                           QUrl.fromUserInput(step.description).toString())
                self.webView.setHtml(html)
            else:
                self.webView.setHtml(step.description)
            QCoreApplication.processEvents()
            if step.prestep is not None:
                execute(step.prestep)
            if step.function is not None:
                self.btnRunStep.setEnabled(step.steptype != Step.AUTOMATEDSTEP)
                self.btnMove.setEnabled(step.steptype != Step.AUTOMATEDSTEP and step.endsignal is None)
                if step.steptype == Step.AUTOMATEDSTEP:
                    self.runCurrentStepFunction()
            else:
                self.btnRunStep.setEnabled(False)
                self.btnMove.setEnabled(step.endsignal is None)

    def finishLesson(self):
        self.setVisible(False)

        self.lessonFinished.emit()
