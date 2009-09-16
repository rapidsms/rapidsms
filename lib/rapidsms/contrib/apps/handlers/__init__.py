#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re


class BaseHandler(object):

    @classmethod
    def dispatch(cls, router, msg):
        return False

    def __init__(self, router, msg):
        self.router = router
        self.msg = msg

    def respond(self, text):
        self.msg.respond(text)


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


class KeywordHandler(BaseHandler):

    @classmethod
    def _keyword(cls):
        if hasattr(cls, "keyword"):
            prefix = r"^(?:%s)(?:\s+(.+))?$" % (cls.keyword)
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
