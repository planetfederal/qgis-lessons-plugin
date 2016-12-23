# -*- coding: utf-8 -*-

import os
from collections import defaultdict

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QIcon, QTextDocument
from qgis.PyQt.QtWidgets import QTreeWidgetItem, QDialogButtonBox

from lessons import lessons

WIDGET, BASE = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'lessonselector.ui'))


class LessonSelector(BASE, WIDGET):

    def __init__(self):
        super(LessonSelector, self).__init__()
        self.setupUi(self)

        self.lesson = None

        allLessons = defaultdict(list)
        for lesson in lessons:
            allLessons[lesson.group].append(lesson)

        lessonIcon = QIcon(os.path.dirname(__file__) + '/lesson.gif')
        for group, groupLessons in allLessons.items():
            groupItem = QTreeWidgetItem()
            groupItem.setText(0, group)
            for lesson in groupLessons:
                lessonItem = QTreeWidgetItem()
                lessonItem.lesson = lesson
                lessonItem.setText(0, lesson.name)
                lessonItem.setIcon(0, lessonIcon)
                groupItem.addChild(lessonItem)
            self.lessonsTree.addTopLevelItem(groupItem)

        self.lessonsTree.sortItems(0, 0)

        self.lessonsTree.expandAll()

        self.lessonsTree.currentItemChanged.connect(self.currentItemChanged)
        self.lessonsTree.itemDoubleClicked.connect(self.itemDoubleClicked)

        self.buttonBox.accepted.connect(self.okPressed)
        self.buttonBox.rejected.connect(self.cancelPressed)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def itemDoubleClicked(self, item, i):
        if hasattr(item, "lesson"):
            self.lesson = item.lesson
            self.close()

    def currentItemChanged(self):
        item = self.lessonsTree.currentItem()
        if item:
            if hasattr(item, "lesson"):
                self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
                if os.path.exists(item.lesson.description):
                    with open(item.lesson.description) as f:
                        html = "".join(f.readlines())
                    self.webView.document().setMetaInformation(QTextDocument.DocumentUrl,
                                                               QUrl.fromUserInput(item.lesson.description).toString())
                    self.webView.setHtml(html)
                else:
                    self.webView.setHtml("<p>%s</p>" % item.lesson.description)
            else:
                self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
                self.webView.setHtml("")

    def cancelPressed(self):
        self.close()

    def okPressed(self):
        self.lesson = self.lessonsTree.selectedItems()[0].lesson
        self.close()
