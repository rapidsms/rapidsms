#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re
from datetime import datetime

from rapidsms.tests.harness import TestRouterMixin


class TestScriptMixin(TestRouterMixin):
    """
    The scripted.TestScript class subclasses unittest.TestCase
    and allows you to define unit tests for your RapidSMS apps
    in the form of a 'conversational' script::

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

    Inherits from :py:class:`~rapidsms.tests.harness.router.TestRouterMixin`.
    """

    def assertInteraction(self, script):
        self.runParsedScript(self.parseScript(script))

    @classmethod
    def parseScript(cls, script):
        cmds = []
        for line in [x.strip() for x in script.split("\n")]:
            if not line or line.startswith("#"):
                continue
            tokens = re.split(r'([<>])', line, 1)
            num, dir, txt = [x.strip() for x in tokens]
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
        self.receive(text=txt, connection=self.lookup_connections([num])[0])

    def receiveAllMessages(self):
        messages = self.outbound
        self.router.outbound = []
        return messages

    def _checkAgainstMessage(self, num, txt, last_msg, msg):
        peer = msg.connections[0].identity
        self.assertEqual(peer, num,
                         "Expected to respond to "
                         "%s, but message was sent to %s.\n"
                         "\nMessage: %s\nReceived "
                         "text: %s\nExpected text: %s\n" % (num, peer,
                                                            last_msg, msg.text, txt))

        self.assertEqual(msg.text, txt, "\nMessage: %s\nReceived "
                         "text: %s\nExpected text: %s\n" %
                         (last_msg, msg.text, txt))

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
                if i == len(msgs) - 1:
                    raise

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
        """Run a test script.

        :param str script: A multi-line test script. See
            :py:class:`~rapidsms.tests.harness.scripted.TestScriptMixin`.
        """
        self.clear_sent_messages()  # make sure the outbox is empty
        self.runParsedScript(self.parseScript(script))
