#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers import KeywordHandler, PatternHandler


class EchoKeywordHandler(KeywordHandler):
    """A simple keyword handler for testing that echos the text it receives."""
    keyword = 'hello'
    HELP_TEXT = 'helpful text'

    def help(self):
        self.respond(self.HELP_TEXT)

    def handle(self, text):
        self.respond(text)


class AdditionPatternHandler(PatternHandler):
    """A simple pattern handler for testing that adds the values it receives."""
    pattern = r'^(\d+) plus (\d+)$'

    def handle(self, a, b):
        a, b = int(a), int(b)
        total = a + b
        self.respond('%d + %d = %d' % (a, b, total))
