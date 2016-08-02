# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import os

class LessonsCollection:

	def __init__(self, iface):
		try:
			from lessons import addLessonsFolder
		except:
			return

		folder = os.path.join(os.path.dirname(__file__), "_lessons")
		addLessonsFolder(folder)

	def unload(self):
		pass

	def initGui(self):
		pass






