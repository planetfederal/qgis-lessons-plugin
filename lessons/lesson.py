import os
from utils import openProject, unfoldMenu, menuFromName
import traceback

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

    def __init__(self, name, group, description):
        self.folder = os.path.dirname(traceback.extract_stack()[-2][0])
        self.steps = []
        self.name = name
        self.group = group
        self.cleanup = lambda: None
        self.description = self.resolveFile(description)
        path = os.path.join(self.folder, "project.qgs")
        if os.path.exists(path):
            self.addStep("Open project", "Open project", lambda: openProject(path))

    def setCleanup(self,function):
        self.cleanup = function

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
        step = Step(name, description, function, prestep, endsignal, endsignalcheck, endcheck, steptype)
        self.steps.append(step)

    def addMenuClickStep(self, menuName):
        menu, action = menuFromName(menuName)
        name = "Click on '%s' menu item" % menuName
        def checkMenu(triggeredAction):
            return triggeredAction.text() == action.text()
        self.addStep(name, name, None, None, menu.triggered, checkMenu, None, Step.MANUALSTEP)
