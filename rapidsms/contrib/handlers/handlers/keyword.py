#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re

from django.core.exceptions import ObjectDoesNotExist

from ..exceptions import HandlerError
from .base import BaseHandler


class KeywordHandler(BaseHandler):
    """
    This handler type can be subclassed to create simple keyword-based
    handlers. When a message is received, it is checked against the mandatory
    ``keyword`` attribute (a regular expression) for a prefix match. For
    example::

        >>> class AbcHandler(KeywordHandler):
        ...    keyword = "abc"
        ...
        ...    def help(self):
        ...        self.respond("Here is some help.")
        ...
        ...    def handle(self, text):
        ...        self.respond("You said: %s." % text)

    If the keyword is matched and followed by some text, the ``handle`` method
    is called::

        >>> AbcHandler.test("abc waffles")
        ['You said: waffles.']

    If *just* the keyword is matched, the ``help`` method is called::

        >>> AbcHandler.test("abc")
        ['Here is some help.']

    All other messages are silently ignored (as usual), to allow other apps or
    handlers to catch them.
    """

    #: A string specifying a regular expression matched against the
    #: beginning of the message. Not case sensitive.
    keyword = None

    def help(self):
        """Called when the keyword matches but no text follows"""
        raise NotImplementedError

    def handle(self, text):
        """Called when the keyword matches and text follows

        :param text: The text that follows the keyword.  Any whitespace
             between the keyword and the text is not included.
        """
        raise NotImplementedError

    @classmethod
    def _keyword(cls):
        if hasattr(cls, "keyword") and cls.keyword:
            # The 'keyword' is inside non-grouping parentheses so that a
            # user could set the keyword to a regex - e.g.
            # keyword = r'one|two|three'
            prefix = r"""
                ^\s*             # discard leading whitespace
                (?:{keyword})    # require the keyword or regex
                [\s,;:]*         # consume any whitespace , ; or :
                ([^\s,;:].*)?    # capture rest of line if any, starting
                                 # with the first non-whitespace
                $                # match all the way to the end
            """.format(keyword=cls.keyword)

            return re.compile(prefix, re.IGNORECASE | re.VERBOSE | re.DOTALL)
        raise HandlerError('KeywordHandler must define a keyword.')

    @classmethod
    def dispatch(cls, router, msg):
        keyword = cls._keyword()

        match = keyword.match(msg.text)
        if match is None:
            return False

        # spawn an instance of this handler, and stash
        # the low(er)-level router and message object
        inst = cls(router, msg)

        # if any non-whitespace content was send after the keyword, send
        # it along to the handle method. the instance can always find
        # the original text via self.msg if it really needs it.
        text = match.group(1)
        if text is not None and text.strip() != "":
            try:
                inst.handle(text)

            # special case: if an object was expected but not found,
            # return the (rather appropriate) "%s matching query does
            # not exist." message. this can, of course, be overridden by
            # catching the exception within the ``handle`` method.
            except ObjectDoesNotExist as err:
                return inst.respond_error(
                    str(err))

            # another special case: if something was miscast to an int
            # (it was probably a string from the ``text``), return a
            # more friendly (and internationalizable) error.
            except ValueError as err:
                p = r"^invalid literal for int\(\) with base (\d+?): '(.+?)'$"
                m = re.match(p, str(err))

                # allow other valueerrors to propagate.
                if m is None:
                    raise

                return inst.respond_error(
                    "Not a valid number: %(string)s" % dict(
                        string=m.group(2)))

        # if we received _just_ the keyword, with
        # no content, some help should be sent back
        else:
            inst.help()

        return True
