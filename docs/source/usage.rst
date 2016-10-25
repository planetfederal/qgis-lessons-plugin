.. _usage:

Usage
=====

Start lessons
-------------

#. To open a lesson, go to :menuselection:`Plugins --> Lessons --> Start Lesson`. The :guilabel:`Lesson selector` will show up.

   .. figure:: img/lesson_selector.png

#. The lessons are organized in groups. If necessary, click the cross next to the group's name to expand its lessons list.

#. Click one of the lessons. On the right side of the dialog, a description of the lesson will show its purpose and objectives, the estimated time for completions and the lesson's author.

   .. figure:: img/lesson_selected.png

#. Click :guilabel:`OK` to start the selected lesson.

Lessons Panel
-------------

When a lesson starts, the :guilabel:`Lessons Panel` will be on the right side of the QGIS's window. The :guilabel:`Lessons Panel` includes: a Lesson's steps index (1) to track the lesson's progress, a description window (2) to show the current step's instructions, and a button bar (3).

.. figure:: img/lesson_panel.png

The following buttons compose the button bar:

* **Move to next step** - To go to the next lesson's step.
* **Run step** - Helps performing the steps instructions (not always available).
* **Restart lesson** - Resets the project and cleans all the lesson's progress made so far.
* **Quit lesson** - Cleans the lesson's progress and closes the :guilabel:`Lessons Panel`, but keeps the project loaded.

Following a lesson
------------------

Generally, the lessons will open a prepared project with all the necessary data already prepared. Unless the lesson is about loading data, you should never need to add data yourself.

For each lesson's step, follow the instructions in the description window. When you have finished executing those instructions, click :guilabel:`Move to next step`.

Some lessons' steps won't let you move to the next step if you haven't finished the current step's instructions correctly. In those cases a message will pop up, asking you to review and execute the instructions.

.. figure:: img/warning_message.png

Some steps will move to the next step automatically as soon as you complete the instructions. The step’s description will inform you of that. Typically, this is used in steps that ask you to click a menu item.

.. figure:: img/click_menu.png

In some lessons' steps, if you get stuck while following the instructions, you can click :guilabel:`Run step`. This functionality will help you perform the step instructions, either by executing it for you or by showing how to do it.

When you have finished all steps of the lesson, a dialog will show up congratulating you for the achievement. In that dialog, you can either start the following suggested lesson or close the dialog and the lessons panel.

.. figure:: img/congratulations_message.png

