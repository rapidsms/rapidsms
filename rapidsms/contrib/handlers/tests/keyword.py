#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.tests.harness import EchoKeywordHandler
from rapidsms.messages import IncomingMessage
from rapidsms.tests.harness import RapidTest


__all__ = ['TestKeywordHandler']


class TestKeywordHandler(RapidTest):
    """Tests for rapidsms.contrib.handlers.handlers.keyword"""

    def setUp(self):
        self.connection = self.create_connection()

    def _check_dispatch(self, text, correct_response):
        msg = IncomingMessage(self.connection, text)
        retVal = EchoKeywordHandler.dispatch(self.router, msg)
        if correct_response is not None:
            self.assertEqual(retVal, True)
            self.assertEqual(len(msg.responses), 1)
            self.assertEqual(msg.responses[0].text, correct_response)
        else:
            self.assertEqual(retVal, False)
            self.assertEqual(len(msg.responses), 0)

    def test_no_match(self):
        """Handler should return nothing if there is no match."""
        self._check_dispatch('no match', None)

    def test_keyword_only(self):
        """Handler should call help() if only keyword is sent."""
        self._check_dispatch('hello', EchoKeywordHandler.HELP_TEXT)

    def test_keyword_and_whitespace(self):
        """Handler should call help() if only whitespace is after keyword."""
        self._check_dispatch('hello      ', EchoKeywordHandler.HELP_TEXT)

    def test_match(self):
        """
        Handler should call handle() if there is non-whitespace text after
        keyword.
        """
        self._check_dispatch('hello world', 'world')

    def test_case_insensitive_match(self):
        """Handler should use case-insensitive match."""
        self._check_dispatch('HeLlO World', 'World')

    def test_trailing_whitespace(self):
        """
        Trailing whitespace should be passed to handler, but prepended
        whitespace should not.
        """
        self._check_dispatch('hello world     ', 'world     ')
