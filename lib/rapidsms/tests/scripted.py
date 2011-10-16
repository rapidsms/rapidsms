from django.test import TestCase
from rapidsms.tests.harness.scripted import TestScript as TestScriptMixin


class TestScript(TestScriptMixin, TestCase):
    
    def startRouter(self):
        pass
    
    def stopRouter(self):
        pass
