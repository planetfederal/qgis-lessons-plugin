# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QTextBrowser
from qgis.utils import iface
from lessons import lessonFromName


class LessonFinishedDialog(QDialog):

    def __init__(self, lesson):
        super(LessonFinishedDialog, self).__init__(iface.mainWindow())
        self.lesson = lesson
        self.setWindowTitle("Lesson finished")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setMargin(10)
        txt = "<p>Congratulations! You have correctly finished this lesson.</p>"

        if lesson.nextLessons:
            txt += "<p>We recommend you the following lessons to continue:</p><ul>"
            for i, nextLesson in enumerate(lesson.nextLessons):
                txt+="<li><a href='%i'>%s</a>" % (i, nextLesson[1])
            txt += "</ul><p>If you don't want to run more lessons, just <a href='exit'>close this dialog.</a></p>"

        self.text = QTextBrowser()
        self.text.anchorClicked.connect(self.linkClicked)
        self.text.setHtml(txt)
        self.text.setOpenLinks(False)
        self.verticalLayout.addWidget(self.text)
        self.setLayout(self.verticalLayout)
        self.resize(400, 300)
        self.nextLesson = None

    def linkClicked(self, url):
        if url.path() != "exit":
            self.nextLesson = lessonFromName(*self.lesson.nextLessons[int(url.path())])
        self.close()
