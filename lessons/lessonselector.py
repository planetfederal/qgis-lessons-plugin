# -*- coding: utf-8 -*-

import os
from collections import defaultdict

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QIcon, QTextDocument
from qgis.PyQt.QtWidgets import QTreeWidgetItem, QDialogButtonBox

from lessons import lessons, _removeLesson, groups
import codecs
import markdown

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
            groupItem.description = groups.get(group, "")
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

        self.btnRunLesson.setDefault(True)
        self.btnRunLesson.clicked.connect(self.okPressed)
        self.btnRemove.clicked.connect(self.remove)
        self.btnClose.clicked.connect(self.close)

        self.btnRemove.setEnabled(False)

        self.lessonsTree.currentItemChanged.connect(self.currentItemChanged)

        self.lessonsTree.setCurrentItem(self.lessonsTree.invisibleRootItem().child(0).child(0))

    def itemDoubleClicked(self, item, i):
        if hasattr(item, "lesson"):
            self.lesson = item.lesson
            self.close()

    def currentItemChanged(self):
        item = self.lessonsTree.currentItem()
        if item:
            if hasattr(item, "lesson"):
                self.btnRemove.setText("Uninstall lesson")
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
                self.btnRemove.setText("Uninstall lessons group")
                self.btnRemove.setEnabled(True)
                if os.path.exists(item.description):
                    with codecs.open(item.description, encoding="utf-8") as f:
                        html = "".join(f.readlines())
                    if item.description.endswith(".md"):
                        html = markdown.markdown(html)
                    self.webView.document().setMetaInformation(QTextDocument.DocumentUrl,
                                                               QUrl.fromUserInput(item.description).toString())
                else:
                    html = item.description
                self.webView.setHtml(html)

        else:
            self.btnRemove.setEnabled(False)

    def remove(self):
        item = self.lessonsTree.currentItem()
        if hasattr(item, "lesson"):
            reply = QMessageBox.question(None,
                                     "Confirmation",
                                     'Are you sure you want to uninstall this lesson?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
            if reply == QMessageBox.Yes:
                _removeLesson(item.lesson)
                item = self.lessonsTree.currentItem()
                parent = item.parent()
                parent.takeChild(parent.indexOfChild(item))
                if parent.childCount() == 0:
                    self.lessonsTree.takeTopLevelItem(self.lessonsTree.indexOfTopLevelItem(parent))
                item.lesson.uninstall()
        else:
            reply = QMessageBox.question(None,
                         "Confirmation",
                         'Are you sure you want to uninstall this group of lessons?',
                         QMessageBox.Yes | QMessageBox.No,
                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                for i in range(item.childCount()):
                    child = item.child(i)
                    _removeLesson(child.lesson)
                    child.lesson.uninstall()
                self.lessonsTree.takeTopLevelItem(self.lessonsTree.indexOfTopLevelItem(item))

    def okPressed(self):
        self.lesson = self.lessonsTree.selectedItems()[0].lesson
        self.close()
