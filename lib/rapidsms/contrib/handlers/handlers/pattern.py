#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from .base import BaseHandler


class PatternHandler(BaseHandler):

    """
    This handler type can be subclassed to create simple pattern-based
    handlers. This isn't usually a good idea -- it's cumbersome to write
    patterns with enough flexibility to be used in the real world -- but
    it's very handy for prototyping, and can easily be upgraded later.

    When a message is received, it is matched against the mandatory
    ``pattern`` attribute (a regular expression). If the pattern is
    matched, the ``handle`` method is called with the captures as
    arguments. For example::

        >>> class SumHandler(PatternHandler):
        ...    pattern = r'^(\d+) plus (\d+)$'
        ...
        ...    def handle(self, a, b):
        ...        a, b = int(a), int(b)
        ...        total = a + b
        ...
        ...        self.respond(
        ...            "%d+%d = %d" %
        ...            (a, b, total))

        >>> SumHandler.test("1 plus 2")
        ['1+2 = 3']

    Note that the pattern is not mangled for flexibility (as it was in
    previous versions of RapidSMS), so if you choose to deploy pattern
    handlers, your incoming messages must match *precisely*. Perhaps
    obviously, this won't work because of the trailing whitespace::

        >>> SumHandler.test("1 plus 2 ")
        False

    All non-matching messages are silently ignored (as usual), to allow
    other apps or handlers to catch them.
    """

    @classmethod
    def _pattern(cls):
        if hasattr(cls, "pattern"):
            return re.compile(cls.pattern, re.IGNORECASE)

    @classmethod
    def dispatch(cls, router, msg):

        pattern = cls._pattern()
        if pattern is None:
            return False

        match = pattern.match(msg.text)
        if match is None:
            return False

        cls(router, msg).handle(*match.groups())
        return True
