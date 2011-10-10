from django.test import TestCase

from rapidsms.tests.harness import EchoApp
from rapidsms.tests.harness.scripted import TestScript


class EchoTest(TestScript, TestCase):
    apps = (EchoApp,)

    def testRunScript (self):
        self.runScript("""
            2345678901 > echo?
            2345678901 < 2345678901: echo?
        """)
