#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.messages import IncomingMessage
from rapidsms.tests.harness import RapidTest

from rapidsms.contrib.echo.handlers.echo import EchoHandler
from rapidsms.contrib.echo.handlers.ping import PingHandler


class TestEchoHandler(RapidTest):

    def setUp(self):
        self.connection = self.create_connection()

    def _test_handle(self, text, correct_response):
        msg = IncomingMessage(self.connection, text)
        retVal = EchoHandler.dispatch(self.connection, msg)
        if correct_response is not None:
            self.assertTrue(retVal)
            self.assertEqual(len(msg.responses), 1)
            self.assertEqual(msg.responses[0]['text'], correct_response)
        else:
            self.assertFalse(retVal)
            self.assertEqual(len(msg.responses), 0)

    def test_no_match(self):
        self._test_handle('no match', None)

    def test_only_keyword(self):
        self._test_handle('echo', 'To echo some text, send: ECHO <ANYTHING>')

    def test_keyword_and_whitespace(self):
        self._test_handle('echo  ', 'To echo some text, send: ECHO <ANYTHING>')

    def test_match(self):
        self._test_handle('echo hello', 'hello')

    def test_case_insensitive_match(self):
        self._test_handle('EcHo hello', 'hello')

    def test_leading_whitespace(self):
        self._test_handle('  echo hello', 'hello')

    def test_trailing_whitespace(self):
        self._test_handle('echo hello  ', 'hello  ')

    def test_whitespace_after_keyword(self):
        self._test_handle('echo     hello', 'hello')


class TestPingHandler(RapidTest):

    def setUp(self):
        self.connection = self.create_connection()

    def _test_handle(self, text, correct_response):
        msg = IncomingMessage(self.connection, text)
        retVal = PingHandler.dispatch(self.connection, msg)
        if correct_response is not None:
            self.assertTrue(retVal)
            self.assertEqual(len(msg.responses), 1)
            self.assertEqual(msg.responses[0]['text'], correct_response)
        else:
            self.assertFalse(retVal)
            self.assertEqual(len(msg.responses), 0)

    def test_no_match(self):
        self._test_handle('no match', None)

    def test_match(self):
        self._test_handle('ping', 'pong')

    def test_leading_whitespace(self):
        self._test_handle('   ping', None)

    def test_trailing_whitespace(self):
        self._test_handle('ping   ', None)

    def test_case_sensitivity(self):
        self._test_handle('PiNg', None)
