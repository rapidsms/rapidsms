from rapidsms.tests.scripted import TestScript
from apps.reporters.models import *
import apps.reporters.app as reporter_app
from app import App

class TestApp (TestScript):
    apps = (reporter_app.App, App )

    # the test_backend script does the loading of the dummy backend that allows reporters
    # to work properly in tests
    def setUp(self):
        TestScript.setUp(self)
        
    testJoin = """
           8005551212 > echo village
           8005551212 > #join village
         """
    
 