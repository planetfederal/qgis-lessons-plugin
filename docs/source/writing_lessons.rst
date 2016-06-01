.. _writing_lessons:
Writing Lessons
================

Instructions to write new lessons are described in this document.

The recommended procedure for adding new lessons is as follows:

1) First, create a new plugin. This plugin will be responsible for registering the lessons, so they will appear when the lessons list is shown.

2) For each lesson, create a separate folder with the structure shown below:

- ```__init__.py```
- [html files describing the lesson and each step in it]
- [data used for this lessons]
- ```project.qgs```

All these elements are explained in a later section in this document.

3) In the init method of your plugin, register your plugin adding the following snippet

::

	try:
        from lessons import addLessonModule
        addLessonModule(lesson_module)
    except:
        pass

Replace *lesson_module* with the reference to your lesson module (which you should have imported), and add as many entries as modules you have created in your set of lessons.


An example of a plugin that adds a collection of lessons can be found in the ```examplelessons``` folder of this repository. Use is as a template for you own collections. If using it, you do not have to manually call the ```addLessonModule``` method. The plugin will automatically discover all available lessons. The only thing you have to do is to add your lessons under the ```_lessons``` subfolder, each of them in its corresponding subfolder, as described above.


Creating a lesson
-----------------

If you have created a folder for each lesson as described above, the steps of the lesson and the content of each step should be defined in the ```__init__.py``` file.

Create a ```Lesson``` object, specifying its name, the group it belongs to (lessons can be grouped) and a detailed description.

::

	lesson = Lesson ("Interpolating from a points layer", "Analysis lessons",
					"This lessons shows how to use the interpolation capabilities of QGIS")

Instead of a string with the description, you can pass the name of an HTML file containing a richer description. For instance:


::

	lesson = Lesson ("Interpolating from a points layer", "Analysis lessons",
					"lesson.html")

There is no need to add the full path to the file, as long as the file is in the same folder as the ```__init__.py``` file. The full path will be correctly resolved at runtime.


If your lesson requires loading data into QGIS, you can prepare a project with that data. Name the project ``project.qgs```and put it in the lesson folder as well, as indicated. This will cause the lesson to automatically have a first step that loads the data before starting with the rest of step. If you want your data to be loaded from a different project in another folder, or to load it not at the beginning of the lesson, you will have to manually add that step.

Now you can add steps to your lesson using the ```addStep``` method, which has the following signature:

::
	
	addStep(self, name, description, function=None, prestep=None, endsignal=None,
                endsignalcheck=None, endcheck=lambda:True, steptype=1):

Here is a description of its arguments:

- **name**: the name of the step, to be shown in the lesson explorer when running the lesson.
- **description**: a longer description of the step. As in the case of the leson description, it can be a string containing the description, or a string containing the name of an HTML file with the description itself.
- **function**: The function that execute this step. Even in the case of steps that are supposed to be performed manually by the user, a function can be supplied which performs the same action. In this case, the *Run step* button will be available, so the user can have the step automatically executed, instead of having to do it manually. If the step is a manual step and there is no function to perform the task, None can be passed
- **prestep**: a function to be executed before starting the step, for preparing the necessary context. Should be None if no preparation is needed
- **endsignal**: a signal that indicates that the step has been finished. If not None, the plugin will listen to the passed signal, and when it is emitted, it will automatically move to the next step.
- **endsignalcheck**: In case it is needed to check that the *endsignal* signal should actually cause moving to the next step, pass a function to do the checking using this parameters. Should be used if the signal might be emmited in cases that do not represent the end of the step. Should be None if no check has to be performed.
- **endcheck**: a function to check that the step has been correctly executed. This function will be run when the lesson moves to the next step. If should return true if the user has correctly performed the task for this step, or false otherwise. In this last case, the plugin will show a warning message and won't let the user move to the next step until the step is correctly completed.
- **steptype**: ```Step.MANUALSTEP``` if the step is to be performed manually by the user, or ```Step.AUTOMATEDSTEP``` if it's an automated one. In this last case, the step will not be shown in the list of them in the lesson explorer, and it is required to pass a function using the ```function``` argument.

Convenience methods and utils
------------------------------

To make it easier to create new lessons, you will find some convenience methods in the ```Lesson``` class and functions for performing common tasks in the lessons.utils module.

The addMenuClickStep() method in the ```Lesson```class will add step that involves clicking on a menu item. Its only argument is the name of the menu to click. This method will add a step that unfold the specified menu and highlights the corresponding menu item, and that will automatically move to the next step once that menu item is clicked.

Capturing QGIS interaction to create a lesson
----------------------------------------------

The help files associated with a lesson contain text and usually screenshots. These have to be created manually, by creating the corresponding html and image files.

An additional plugin is included in this repository, in the ```lessonscreator``` folder, aimed at users that plan to create their own lessons. It simplifies both writing text and creating screenshots, by capturing actions performed in QGIS. That is, the user performs the steps in the lesson to create, and the plugin tries to automatically create the corresponding lesson files.

To create a new lesson, select the *Plugins/Lessons/Capture lesson steps* menu. Select a folder to store the lessons data. 

From that moment, the plugin will be listening to your actions and documenting them according to the following ideas:

- Whenever the focus changes to a new window, a screenshot of the window will be taken. An entry in the html file describing the current step will be added, which will include the screenshot.

- Whenever the focus changes between two elements (but both of them having the same parent window/dialog), and the one that receives the focus is an input widget (text box, dropdown list, etc), a screenshot of the new element that receives the focus will be taken. The element that receives the focus will be highlighted in the screenshot using a red dashed rectangle, as shown in the image below

	.. figure:: rectangle.png

	The image will be added to the html corresponding to the current step, along with a text entry in the form "Click on [widget_name]"

- When edit widgets lose focus or are modified, the plugin will try to capture the user action. For instance, for a dropdown list, when the current value is changed, the text "Select [new_value_text] in the [dropdown_name] dropdown list" is added. In the case of text boxes, the text "Enter [text] in the [textbox_name] textbox" is added.

- When a menu item is clicked, the text "Select the [menu_text] menu" will be added.

All texts snippets and screenshots are added to the html file that describes the current step. A lesson might contain several steps. To start a new step and add text and screenshots to another file, press CTRL-W at anytime, and a new step will be started.

When you have captured all elements of you lesson, select the *Plugins/Lessons/Stop capturing lesson steps* menu.

In the folder that you selected, you will find all html files and image files. You will also find a ```___init.py___``` file that describe the lesson. The folder as it is generated can be added to your lessons plugin (created based on the ```examplelessons``` template) and will be recognised as a valid lesson.

