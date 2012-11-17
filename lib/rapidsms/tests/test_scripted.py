from rapidsms.tests.harness import EchoApp
from rapidsms.tests.scripted import TestScript


class EchoTest(TestScript):
    apps = (EchoApp,)

    def testRunScript(self):
        self.runScript("""
            2345678901 > echo?
            2345678901 < 2345678901: echo?
        """)
