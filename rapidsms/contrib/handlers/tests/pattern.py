#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers.tests.harness import AdditionPatternHandler
from rapidsms.messages import IncomingMessage
from rapidsms.tests.harness import RapidTest


__all__ = ['TestPatternHandler']


class TestPatternHandler(RapidTest):
    """Tests for rapidsms.contrib.handlers.handlers.pattern"""

    def setUp(self):
        self.connection = self.create_connection()

    def _check_dispatch(self, text, correct_response):
        msg = IncomingMessage(self.connection, text)
        retVal = AdditionPatternHandler.dispatch(self.router, msg)
        if correct_response is not None:
            self.assertEqual(retVal, True)
            self.assertEqual(len(msg.responses), 1)
            self.assertEqual(msg.responses[0].text, correct_response)
        else:
            self.assertEqual(retVal, False)
            self.assertEqual(len(msg.responses), 0)

    def test_no_pattern(self):
        """Handler should not operate if it does not have a pattern."""
        delattr(AdditionPatternHandler, 'pattern')
        self._check_dispatch('1 plus 2', None)

    def test_no_match(self):
        """Handler should return False if there is no match."""
        self._check_dispatch('no match', None)

    def test_match(self):
        """Handler should return response if there is a match."""
        self._check_dispatch('1 plus 2', '1 + 2 = 3')

    def test_case_insensitive_match(self):
        """Handler pattern is not case sensitive."""
        self._check_dispatch('1 PLUS 2', '1 + 2 = 3')

    def test_prepended_whitespace(self):
        """Handler pattern is sensitive to prepended whitespace."""
        self._check_dispatch('  1 plus 2', None)

    def test_trailing_whitespace(self):
        """Handler pattern is sensitive to trailing whitespace."""
        self._check_dispatch('1 plus 2  ', None)

    def test_extra_whitespace(self):
        """Handler pattern is sensitive to extra whitespace."""
        self._check_dispatch('1    plus 2', None)
