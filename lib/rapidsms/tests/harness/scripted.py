#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re
from datetime import datetime

from rapidsms.router.test import BlockingRouter
from rapidsms.tests.harness import MockBackendRouter
from rapidsms.models import Backend, Contact, Connection
from rapidsms.messages.incoming import IncomingMessage


class TestScriptMixin(MockBackendRouter):
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

    def setUp(self):
        kwargs = {}
        if self.apps:
            kwargs['apps'] = self.apps
        self.backend = self.create_backend({'name': 'mockbackend'})
        self.router = BlockingRouter(**kwargs)
        self.router.start()

    def tearDown(self):
        self.router.stop()

    def assertInteraction(self, script):
        self.runParsedScript(self.parseScript(script))

    @classmethod
    def parseScript(cls, script):
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

    def sendMessage(self, num, txt, date=None):
        if date is None:
            date = datetime.now()
        connection, _ = Connection.objects.get_or_create(backend=self.backend,
                                                         identity=num)
        msg = IncomingMessage(connection, txt, date)
        self.router.receive_incoming(msg)

    def receiveMessage(self):
        try:
            return self.outbox.pop(0)
        except IndexError:
            return None

    def receiveAllMessages(self):
        messages = []
        msg = self.receiveMessage()
        while msg is not None:
            messages.append(msg)
            msg = self.receiveMessage()
        return messages

    def _checkAgainstMessage(self, num, txt, last_msg, msg):
        self.assertEquals(msg.peer, num, "Expected to respond to "
                          "%s, but message was sent to %s.\n"
                          "\nMessage: %s\nReceived "
                          "text: %s\nExpected text: %s\n" % (num, msg.peer,
                                             last_msg, msg.text, txt))
                                             
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

    def runParsedScript(self, cmds):
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

    def runScript(self, script):
        self.clear() # make sure the outbox is empty
        self.runParsedScript(self.parseScript(script))
