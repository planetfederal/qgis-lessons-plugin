# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import os

class LessonsCollection:

	folder = os.path.join(os.path.dirname(__file__), "_lessons")

	def __init__(self, iface):
		try:
			from lessons import addLessonsFolder
		except:
			return

		addLessonsFolder(self.folder, "examplelessons")

	def unload(self):
		try:
			from lessons import removeLessonsFolder
		except:
			return

		removeLessonsFolder(self.folder, "examplelessons"))

	def initGui(self):
		pass






