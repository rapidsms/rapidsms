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
           8005551212 > #join unassociated
           8005551212 > #lang eng
           8005551212 > #lang fre
           8005551212 > #lang wol
           8005551212 > #lang yul
           8005551212 > #lang dyu
         """
    
 