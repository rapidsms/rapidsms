<<<<<<< HEAD:reporters/tests.py
from rapidsms.tests.scripted import TestScript
from reporters.models import *
import reporters.app as reporter_app
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
    
 
=======
#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.tests.scripted import TestScript
#from apps.persistance.app import App as Papp
from app import App


class TestApp (TestScript):
    apps = (App,)

    _testJoining = """
        1111 > JOIN 1234567890
        1111 < blah blah
    """
>>>>>>> 3a291e6ffc5e5fe7e6fc7384863976597343b474:reporters/tests.py
