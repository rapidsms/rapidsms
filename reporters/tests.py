from rapidsms.tests.scripted import TestScript
from app import App
import apps.reporters.app as reporters_app
from models import *
from apps.reporters.models import Reporter, PersistantConnection, PersistantBackend
    
class TestApp (TestScript):
    apps = (App, reporters_app.App)
    # the test_backend script does the loading of the dummy backend that allows reporters
    # to work properly in tests
    fixtures = ['test_backend', 'test_tree']
    
    testTrigger = """
           8005551212 > test
           8005551212 < hello
         """        
    
    testPin = """
           8005551211 > pin
           8005551211 < Please enter your 4-digit PIN
           8005551211 > 1234
           8005551211 < Thanks for entering.
         """
         
    testPinFailure = """
           8005551213 > pin
           8005551213 < Please enter your 4-digit PIN
           8005551213 > abcd
           8005551213 < "abcd" is not a valid answer. You must enter a 4-digit decimal number
           8005551213 > 123
           8005551213 < "123" is not a valid answer. You must enter a 4-digit decimal number
           8005551213 > 123d
           8005551213 < "123d" is not a valid answer. You must enter a 4-digit decimal number
           8005551213 > 12345
           8005551213 < "12345" is not a valid answer. You must enter a 4-digit decimal number
           8005551213 > 
           8005551213 < "" is not a valid answer. You must enter a 4-digit decimal number
           8005551213 > 0000
           8005551213 < Thanks for entering.
         """
         
    
        
#More tests
    def TestReports(self):
	backend = PersistantBackend.objects.get(title="TestScript")
        reporter = Reporter.objects.create(alias='0004', language='en')
        connection = PersistantConnection.objects.create(backend=backend,identity="loc_en",reporter=reporter)
        script = """
              8005551214 > join Ivan kavuma fr
              8005551213 < " "
            """        
        self.runScript(script) 
        
        
         
