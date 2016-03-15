# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import glob
import os

class LessonsCollection:

	def __init__(self, iface):
		try:
			from lessons import addLessonModule
		except:
			return

		folder = os.path.join(os.path.dirname(__file__), "_lessons")
		def isPackage(d):
			d = os.path.join(folder, d)
			return os.path.isdir(d) and glob.glob(os.path.join(d, '__init__.py*'))
		packages = filter(isPackage, os.listdir(folder))
		for p in packages:
			m = __import__(__name__.split(".")[0] + "._lessons." + p, fromlist="dummy")
			addLessonModule(m)
		
		# add tests to test plugin
		try:
			from qgistester.tests import addTestModule
			from examplelessons.test import testplugin
			addTestModule(testplugin, "Example lessons")
		except Exception as ex:
			pass

	def unload(self):
		pass

	def initGui(self):
		pass






