#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from .base import BaseHandler


class KeywordHandler(BaseHandler):

    """
    This handler type can be subclassed to create simple keyword-based
    handlers. When a message is received, it is checked against the
    mandatory ``keyword`` attribute (a regular expression) for a prefix
    match. For example::

        >>> class AbcHandler(KeywordHandler):
        ...    keyword = "abc"
        ...
        ...    def help(self):
        ...        self.respond("Here is some help.")
        ...
        ...    def handle(self, text):
        ...        self.respond("You said: %s." % text)

    If the keyword is matched and followed by some text, the ``handle``
    method is called::

        >>> AbcHandler.test("abc")
        ['Here is some help.']

    If *just* the keyword is matched, the ``help`` method is called::

        >>> AbcHandler.test("abc waffles")
        ['You said: waffles.']

    All other messages are silently ignored (as usual), to allow other
    apps or handlers to catch them.
    """

    @classmethod
    def _keyword(cls):
        if hasattr(cls, "keyword"):
            prefix = r"^\s*(?:%s)(?:[\s,;:]+(.+))?$" % (cls.keyword)
            return re.compile(prefix, re.IGNORECASE)

    @classmethod
    def dispatch(cls, router, msg):

        keyword = cls._keyword()
        if keyword is None:
            return False

        match = keyword.match(msg.text)
        if match is None:
            return False

        # spawn an instance of this handler, and stash
        # the low(er)-level router and message object
        inst = cls(router, msg)

        # if any non-whitespace content was send after the keyword, send it
        # along to the handle method. the instance can always get hold of the
        # original text via self.msg, if it really needs it
        text = match.group(1)
        if text is not None and text.strip() != "":
            inst.handle(text)

        # if we received _just_ the keyword, with
        # no content, some help should be sent back
        else:
            inst.help()

        return True
