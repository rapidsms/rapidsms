#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import time
import logging
from rapidsms.router import router as globalrouter
from harness import EchoApp
import unittest, re, threading
from django.test import TransactionTestCase
from django.conf import settings
from datetime import datetime
from rapidsms.log.mixin import LoggerMixin

class TestScript (TransactionTestCase, LoggerMixin):
    # we use the TransactionTestCase so that the router thread has access
    # to the DB objects used outside and vice versa.
    # see: http://docs.djangoproject.com/en/dev/releases/1.1/#releases-1-1

    """
    The scripted.TestScript class subclasses unittest.TestCase
    and allows you to define unit tests for your RapidSMS apps
    in the form of a 'conversational' script:
    
        from myapp.app import App as MyApp
        from rapidsms.tests.scripted import TestScript

        class TestMyApp (TestScript):
            apps = (MyApp,)
            testRegister = \"""
               8005551212 > register as someuser
               8005551212 < Registered new user 'someuser' for 8005551212!
            \"""

            testDirectMessage = \"""
               8005551212 > tell anotheruser what's up??
               8005550000 < someuser said "what's up??"
            \"""

    This TestMyApp class would then work exactly as any other
    unittest.TestCase subclass (so you could, for example, call
    unittest.main()).
    """
    apps = None

    def assertInteraction(self, script):
        self.runParsedScript(self.parseScript(script))

    def setUp (self):
        self.router = globalrouter
        
        self._init_log(logging.WARNING)
        
        if self.router.backends or self.router.apps:
            self.error("Found existing backends or apps in the test router! "
                       "Did you override tearDown and forget to call the base "
                       "class?  Test behavior may not be as expected.")
                       
        # setup the mock backend
        self.router.add_backend("mockbackend", "rapidsms.tests.harness", {})
        self.backend = self.router.backends["mockbackend"]
        
        # add each application from conf
        for name in [app_name for app_name in settings.INSTALLED_APPS \
                     if not app_name in settings.TEST_EXCLUDED_APPS]:
            self.router.add_app(name)

    def tearDown (self):
        if self.router.running:
            self.router.stop(True) 

        # clear backends, apps
        self.router.backends = {}
        self.router.apps = []
        

    def _init_log(self, level):
        # Enable debug logging to screen during tests.  This should be 
        # configurable better.
        if not self.router.logger:
            self.router.logger = logging.getLogger()
        if not self.router.logger.handlers:
            handler = logging.StreamHandler()
            self.router.logger.addHandler(handler)
        self.router.logger.setLevel(level)
    
        
    @classmethod
    def parseScript (cls, script):
        cmds  = []
        for line in map(lambda(x): x.strip(), script.split("\n")):
            if not line or line.startswith("#"): continue
            tokens = re.split(r'([<>])', line, 1)
            num, dir, txt = map(lambda (x):x.strip(), tokens)
            # allow users to optionally put dates in the number
            # 19232922@200804150730
            if "@" in num:
                num, datestr = num.split("@")
                date = datetime.strptime(datestr, "%Y%m%d%H%M")
            else:
                date = datetime.now()
            cmds.append((num, date, dir, txt))
        return cmds

    def startRouter (self):
        if not hasattr(self, "router") or not self.router:
            raise Exception("Can't start router -- it doesn't exist!  "
                            "Did you override setUp and forget to call "
                            "the base class?")
        # Router.start blocks until Router.stop is called, so start it in a
        # separate thread so it can process our mock messages asynchronously
        threading.Thread(target=self.router.start).start()

        # HACK: wait for the router to be ready
        # to accept our incoming messages
        while not self.router.accepting:
            time.sleep(0.2)

    def stopRouter (self):
        self.router.stop()

        # HACK: wait for the router to stop
        while self.router.accepting:
            time.sleep(0.1)

    def sendMessage (self, num, txt, date=None):
        if date is None:
            date = datetime.now()
        msg = self.backend.message(num, txt)
        msg.received_at = date
        self.backend.route(msg)

        # wait until the router has finished
        # processing this incoming message
        self.router.join()

    def receiveMessage (self):
        return self.backend.next_outgoing_message()

    def receiveAllMessages (self):
        messages = []
        msg = self.receiveMessage()
        while msg is not None:
            messages.append(msg)
            msg = self.receiveMessage()
        return messages
    
    def _checkAgainstMessage(self, num, txt, last_msg, msg):
        self.assertEquals(msg.peer, num, "Expected to respond to "
                          "%s, but message was sent to %s.\n"
                          "Message: '%s'" % (num, msg.peer,
                                             last_msg))
        self.assertEquals(msg.text, txt, "\nMessage: %s\nReceived "
                          "text: %s\nExpected text: %s\n" %
                          (last_msg, msg.text,txt))
        
    
    def _checkAgainstMessages(self, num, txt, last_msg, msgs):
        self.assertTrue(len(msgs) != 0, "Message was ignored.\n"
                        "Message: '%s'\nExpecting: '%s'" %
                        (last_msg, txt))
        for i, msg in enumerate(msgs):
            try:
                self._checkAgainstMessage(num, txt, last_msg, msg)
                return i
            except AssertionError:
                # only raise this up if we've exhausted all our candidates
                if i == len(msgs) - 1: raise 
                    
    def runParsedScript (self, cmds):
        self.startRouter()
        try:
            last_msg = ''
            msgs = []
            for num, date, dir, txt in cmds:
                if dir == ">":
                    self.sendMessage(num, txt, date)
                elif dir == "<":
                    if len(msgs) == 0:
                        # only reload when we've exhausted our cache of messages
                        msgs = self.receiveAllMessages()
                    match = self._checkAgainstMessages(num, txt, last_msg, msgs)
                    msgs.pop(match)

                last_msg = txt
        finally:
            self.stopRouter()

    def runScript (self, script):
        self.runParsedScript(self.parseScript(script))

class MockTestScript (TestScript):
    apps = (EchoApp,)

    testScript = """
        8005551212 > hello
        8005551212 < 8005551212: hello
    """
    testScript2 = """
        1234567890 > echo this!
        1234567890 < 1234567890: echo this!
    """
    
    def testClosure (self):
        self.assertEquals(type(self.testScript.func_defaults), tuple)
        self.assertEquals(type(self.testScript.func_defaults[0]), list)
        self.assertNotEquals(self.testScript.func_defaults,
                             self.testScript2.func_defaults)

    def testRunScript (self):
        self.runScript("""
            2345678901 > echo?
            2345678901 < 2345678901: echo?
        """)

if __name__ == "__main__":
    unittest.main()
