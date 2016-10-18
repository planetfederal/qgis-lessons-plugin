import os
from utils import openProject, menuFromName, execute, getMenuPaths
import traceback
import yaml
import difflib
from qgis.core import QgsMessageLog

class Step():

    MANUALSTEP, AUTOMATEDSTEP = range(2)

    def __init__(self, name, description, function=None, prestep=None, endsignal=None,
                 endsignalcheck=None, endcheck=lambda:True, steptype=1):
        self.name = name
        self.description = description or ""
        self.function = function
        self.prestep = prestep
        self.endcheck = endcheck
        self.endsignal = endsignal
        self.endsignalcheck = endsignalcheck
        self.steptype = steptype

class Lesson():

    def __init__(self, name, group, description, folder = None):
        if folder is None:
            folder = os.path.dirname(traceback.extract_stack()[-2][0])
        self.folder = folder
        self.steps = []
        self.name = name
        self.group = group
        self.cleanup = lambda: None
        self.nextLessons = []
        self.description = self.resolveFile(description)
        path = os.path.join(self.folder, "project.qgs")
        if os.path.exists(path):
            self.addStep("Open project", "Open project", lambda: openProject(path))

    def setCleanup(self,function):
        self.cleanup = function

    def addNextLesson(self, group, name):
        self.nextLessons.append((group,name))

    def resolveFile(self, f):
        if f is None:
            f = ""
        elif not os.path.exists(f):
            path = os.path.join(self.folder, f)
            if os.path.exists(path):
                f = path
        return f

    def addStep(self, name, description, function=None, prestep=None, endsignal=None,
                endsignalcheck=None, endcheck=lambda:True, steptype=1):
        description = self.resolveFile(description)
        if function is not None:
            _function = lambda: execute(function)
        else:
            _function = None
        step = Step(name, description, _function, prestep, endsignal, endsignalcheck, endcheck, steptype)
        self.steps.append(step)

    def addMenuClickStep(self, menuName, description=None):
        menu, action = menuFromName(menuName)
        name = "Click on '%s' menu item." % action.text().replace("&","")
        if description is None:
            description = "<p>Click on <b>%s</b> menu item.</p>" \
                          "<p>Once you click, the lesson will automatically move to the next step.</p>"\
                          % menuName.replace("/"," > ")
        def checkMenu(triggeredAction):
            return triggeredAction.text() == action.text()
        self.addStep(name, description, None, None, menu.triggered, checkMenu, None, Step.MANUALSTEP)

def lessonFromYamlFile(f):
    with open(f) as stream:
        lessonDict = yaml.load(stream)
    lesson = Lesson(lessonDict["name"], lessonDict["group"], lessonDict["description"],
                    os.path.dirname(f))
    for step in lessonDict["steps"]:
        if "menu" in step:
            if "description" in step:
                description = step["description"]
            else:
                description = None

            try:
                lesson.addMenuClickStep(step["menu"], description)

            except:
                closest = difflib.get_close_matches(step["menu"], getMenuPaths())
                if closest:
                    lesson.addMenuClickStep(closest[0], description)
                else:
                    QgsMessageLog.logMessage("Lesson contains a wrong menu name: %s" % step['menu'],
                                             level=QgsMessageLog.WARNING)
                    return None
        else:
            lesson.addStep(step["name"], step["description"], steptype=Step.MANUALSTEP)

    if "nextLessons" in lessonDict:
        for nextLesson in lessonDict["nextLessons"]:
            lesson.addNextLesson(nextLesson["group"], nextLesson["name"])
    return lesson

