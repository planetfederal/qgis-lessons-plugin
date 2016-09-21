# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
from lessons.test.unit_tests import suite

# Tests for the QGIS Tester plugin. To know more see
# https://github.com/boundlessgeo/qgis-tester-plugin

####################################################
# support function for functional tests
def function1Step1():
    ''' step1 of the function1 '''
    pass

def function1Step2():
    ''' step2 of the function1 '''
    pass

def function2Step1():
    ''' step1 of the function2 '''
    pass

def function2Step2():
    ''' step2 of the function2 '''
    pass

def cleanUpFunction1():
    ''' do text context cleanup '''
    pass

def cleanUpFunction2():
    ''' do text context cleanup '''
    pass

####################################################

def functionalTests():
    ''' functional tests. e.g. intergration test or all tests that require user interacion '''
    try:
        from qgistester.test import Test
    except:
        return []
    
    _tests = []
    
    function1Test = Test("Function 1 description")
    function1Test.addStep("do preparation step 1", function1Step1)
    function1Test.addStep("Message to user to do some action => press 'next step'")
    function1Test.addStep("do previous step check", function1Step2)
    function1Test.setCleanup(cleanUpFunction1)
    _tests.append(function1Test)
    
    function2Test = Test("Function 2 description")
    function2Test.addStep("do preparation step 1", function2Step1)
    function2Test.addStep("Message to user to do some action => press 'next step'")
    function2Test.addStep("do previous step check", function2Step2)
    function2Test.setCleanup(cleanUpFunction2)
    _tests.append(function2Test)

    return _tests

def unitTests():
    ''' unit test suites '''
    _tests = []
    _tests.extend(suite())
    # add more suites if available
    #_tests.extend(suite2())
    return _tests