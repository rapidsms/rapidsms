#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.messages import IncomingMessage
from rapidsms.tests.harness import RapidTest

from rapidsms.contrib.handlers import BaseHandler
from rapidsms.contrib.handlers.exceptions import HandlerError
from rapidsms.contrib.handlers.tests.harness import EchoKeywordHandler
from rapidsms.contrib.handlers.tests.harness import AdditionPatternHandler


__all__ = ['TestBaseHandler', 'TestKeywordHandler', 'TestPatternHandler']


class TestBaseHandler(RapidTest):
    """Tests for rapidsms.contrib.handlers.handlers.base"""

    def setUp(self):
        self.connection = self.create_connection()

    def test_dispatch(self):
        """BaseHandler dispatch should always return False."""
        msg = IncomingMessage(self.connection, 'hello')
        retVal = BaseHandler.dispatch(self.router, msg)
        self.assertFalse(retVal)
        self.assertEqual(len(msg.responses), 0)


class TestKeywordHandler(RapidTest):
    """Tests for rapidsms.contrib.handlers.handlers.keyword"""

    def setUp(self):
        self.connection = self.create_connection()

    def _check_dispatch(self, text, correct_response):
        msg = IncomingMessage(self.connection, text)
        retVal = EchoKeywordHandler.dispatch(self.router, msg)
        if correct_response is not None:
            self.assertTrue(retVal)
            self.assertEqual(len(msg.responses), 1)
            self.assertEqual(msg.responses[0]['text'], correct_response)
        else:
            self.assertFalse(retVal)
            self.assertEqual(len(msg.responses), 0)

    def test_no_keyword(self):
        """Handler should raise an exception if there is no keyword."""
        keyword = getattr(EchoKeywordHandler, 'keyword')
        delattr(EchoKeywordHandler, 'keyword')
        try:
            with self.assertRaises(HandlerError):
                msg = IncomingMessage(self.connection, 'hello')
                EchoKeywordHandler.dispatch(self.router, msg)
        finally:
            setattr(EchoKeywordHandler, 'keyword', keyword)

    def test_no_match(self):
        """Handler should return nothing if there is no match."""
        self._check_dispatch('no match', None)

    def test_keyword_only(self):
        """Handler should call help() if only keyword is sent."""
        self._check_dispatch('hello', EchoKeywordHandler.HELP_TEXT)

    def test_keyword_and_whitespace(self):
        """Handler should call help() if only whitespace is after keyword."""
        self._check_dispatch('hello      ', EchoKeywordHandler.HELP_TEXT)

    def test_keyword_and_one_space(self):
        """Handler should call help() if only one space is after keyword."""
        self._check_dispatch('hello ', EchoKeywordHandler.HELP_TEXT)

    def test_punctuation(self):
        """Handler treats comma colon and semicolon same as whitespace
         between keyword and rest of line"""
        self._check_dispatch('hello,', EchoKeywordHandler.HELP_TEXT)
        self._check_dispatch('hello,,', EchoKeywordHandler.HELP_TEXT)
        self._check_dispatch('hello,world', 'world')
        self._check_dispatch('hello:', EchoKeywordHandler.HELP_TEXT)
        self._check_dispatch('hello::', EchoKeywordHandler.HELP_TEXT)
        self._check_dispatch('hello:world', 'world')
        self._check_dispatch('hello;', EchoKeywordHandler.HELP_TEXT)
        self._check_dispatch('hello;;', EchoKeywordHandler.HELP_TEXT)
        self._check_dispatch('hello;world', 'world')
        self._check_dispatch('hello,;:', EchoKeywordHandler.HELP_TEXT)
        self._check_dispatch('hello,;,;:', EchoKeywordHandler.HELP_TEXT)
        self._check_dispatch('hello;,:,:world', 'world')

    def test_match(self):
        """
        Handler should call handle() if there is non-whitespace text after
        keyword.
        """
        self._check_dispatch('hello world', 'world')

    def test_case_insensitive_match(self):
        """Handler should use case-insensitive match."""
        self._check_dispatch('HeLlO World', 'World')

    def test_intermediate_whitespace(self):
        """All whitespace between keyword and text is ignored"""
        self._check_dispatch('hello            world', 'world')

    def test_trailing_whitespace(self):
        """Trailing whitespace should be passed to handler."""
        self._check_dispatch('hello world     ', 'world     ')

    def test_leading_whitespace(self):
        """Prepended whitespace should not be passed to the handler."""
        self._check_dispatch('    hello world', 'world')

    def test_rest_of_line(self):
        """Everything from the first char that's not space comma colon
        or semicolon is passed to the handler"""
        self._check_dispatch('hello x , : ; sdf    ,:   ',
                             'x , : ; sdf    ,:   ')

    def test_intermediate_newline(self):
        """A newline in the middle of the text"""
        self._check_dispatch('hello x \n y \n z', 'x \n y \n z')

    def test_newline_just_after_keyword(self):
        """A newline just after the keyword and before the text is ignored"""
        self._check_dispatch('hello \n x y z', 'x y z')


class TestPatternHandler(RapidTest):
    """Tests for rapidsms.contrib.handlers.handlers.pattern"""

    def setUp(self):
        self.connection = self.create_connection()

    def _check_dispatch(self, text, correct_response):
        msg = IncomingMessage(self.connection, text)
        retVal = AdditionPatternHandler.dispatch(self.router, msg)
        if correct_response is not None:
            self.assertTrue(retVal)
            self.assertEqual(len(msg.responses), 1)
            self.assertEqual(msg.responses[0]['text'], correct_response)
        else:
            self.assertFalse(retVal)
            self.assertEqual(len(msg.responses), 0)

    def test_no_pattern(self):
        """Handler should not operate if it does not have a pattern."""
        pattern = getattr(AdditionPatternHandler, 'pattern')
        delattr(AdditionPatternHandler, 'pattern')
        try:
            with self.assertRaises(HandlerError):
                msg = IncomingMessage(self.connection, '1 plus 2')
                AdditionPatternHandler.dispatch(self.router, msg)
        finally:
            setattr(AdditionPatternHandler, 'pattern', pattern)

    def test_no_match(self):
        """Handler should return False if there is no match."""
        self._check_dispatch('no match', None)

    def test_match(self):
        """Handler should return response if there is a match."""
        self._check_dispatch('1 plus 2', '1 + 2 = 3')

    def test_case_insensitive_match(self):
        """Handler pattern is not case sensitive."""
        self._check_dispatch('1 PLUS 2', '1 + 2 = 3')

    def test_leading_whitespace(self):
        """Handler pattern is sensitive to leading whitespace."""
        self._check_dispatch('  1 plus 2', None)

    def test_trailing_whitespace(self):
        """Handler pattern is sensitive to trailing whitespace."""
        self._check_dispatch('1 plus 2  ', None)

    def test_extra_whitespace(self):
        """Handler pattern is sensitive to extra whitespace."""
        self._check_dispatch('1    plus 2', None)
