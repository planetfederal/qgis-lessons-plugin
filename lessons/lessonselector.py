# -*- coding: utf-8 -*-

import os
from collections import defaultdict

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QIcon, QTextDocument
from qgis.PyQt.QtWidgets import QTreeWidgetItem, QDialogButtonBox

from lessons import lessons, _removeLesson

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


        self.lessonsTree.itemDoubleClicked.connect(self.itemDoubleClicked)

        self.btnRunLesson.clicked.connect(self.okPressed)
        self.btnRemove.clicked.connect(self.remove)

        self.btnRemove.setEnabled(False)

        self.lessonsTree.currentItemChanged.connect(self.currentItemChanged)

    def itemDoubleClicked(self, item, i):
        if hasattr(item, "lesson"):
            self.lesson = item.lesson
            self.close()

    def currentItemChanged(self):
        item = self.lessonsTree.currentItem()
        print item
        if item:
            if hasattr(item, "lesson"):
                self.btnRemove.setEnabled(True)
                self.btnRunLesson.setEnabled(True)
                if os.path.exists(item.lesson.description):
                    with open(item.lesson.description) as f:
                        html = "".join(f.readlines())
                    self.webView.document().setMetaInformation(QTextDocument.DocumentUrl,
                                                               QUrl.fromUserInput(item.lesson.description).toString())
                    self.webView.setHtml(html)
                else:
                    self.webView.setHtml("<p>%s</p>" % item.lesson.description)
            else:
                self.btnRunLesson.setEnabled(False)
                self.btnRemove.setEnabled(False)
                self.webView.setHtml("")
        else:
            self.btnRemove.setEnabled(False)

    def remove(self):
        lesson = self.lessonsTree.selectedItems()[0].lesson
        _removeLesson(lesson)
        item = self.lessonsTree.currentItem()
        parent = item.parent()
        parent.takeChild(parent.indexOfChild(item))
        if parent.childCount() == 0:
            self.lessonsTree.takeTopLevelItem(self.lessonsTree.indexOfChild(parent))
        lesson.uninstall()

    def okPressed(self):
        self.lesson = self.lessonsTree.selectedItems()[0].lesson
        self.close()
