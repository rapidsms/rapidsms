#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from .base import BaseHandler


class PatternHandler(BaseHandler):

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
