# vim: ai ts=4 sts=4 et sw=4

from harness import MockRouter, EchoApp
from rapidsms.backends.backend import Backend
from rapidsms.message import Message
import unittest, re

class MetaTestScript (type):
    def __new__(cls, name, bases, attrs):
        for key, obj in attrs.items():
            if key.startswith("test") and not callable(obj):
                cmds = TestScript.parseScript(obj)
                attrs[key] = lambda (self): self.runParsedScript(cmds)
        return type.__new__(cls, name, bases, attrs)

class TestScript (unittest.TestCase):
    __metaclass__ = MetaTestScript
    apps = []

    def setUp (self):
        self.router = MockRouter()
        self.backend = Backend("TestScript", self.router)
        self.router.add_backend(self.backend)
        for app_class in self.apps:
            app = app_class(app_class.__name__, self.router)
            self.router.add_app(app)

    def tearDown (self):
        if self.router.running:
            self.router.stop() 

    @classmethod
    def parseScript (cls, script):
        cmds  = []
        for line in map(lambda(x): x.strip(), script.split("\n")):
            if not line or line.startswith("#"): continue
            tokens = re.split(r'([<>])', line, 1)
            num, dir, txt = map(lambda (x):x.strip(), tokens)
            cmds.append((num, dir, txt))
        return cmds
     
    def runParsedScript (self, cmds):
        self.router.start()
        for num, dir, txt in cmds:
            if dir == '>':
                msg = self.backend.message(num, txt)
                self.backend.route(msg)  
                self.router.run()
            elif dir == '<':
                msg = self.backend.next_message()
                self.assertTrue(msg is not None, "message was returned")
                self.assertEquals(msg.peer, num, "message.peer is right")
                self.assertEquals(msg.text, txt, "message.text is right")
        self.router.stop()

    def runScript (self, script):
        self.runParsedScript(self.parseScript(script))

class MockTestScript (TestScript):
    apps = (EchoApp,)

    testScript = """
        8005551212 > hello
        8005551212 < 8005551212: hello
        1234567890 > echo this!
        1234567890 < 1234567890: echo this!
    """

    def testScriptInMethod (self):
        self.runScript("""
            2345678901 > echo?
            2345678901 < 2345678901: echo?
        """)

if __name__ == "__main__":
    unittest.main()
