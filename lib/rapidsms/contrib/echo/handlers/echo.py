#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from rapidsms.contrib import handlers


class EchoHandler(handlers.KeywordHandler):
    """
    Handles any message prefixed ECHO, responding with the remainder of
    the text. Useful for remotely (via SMS) checking that the router is
    running, and testing other apps that may alter outgoing messages.

    >>> EchoHandler.test('anything') is None
    True

    >>> EchoHandler.test('echo Yes')
    ['Yes']


    In addition, the language of the outgoing message can be explicitly
    set in parenthesis at the end of the incoming message. This is very
    handy for testing then internationalization of other apps.

    >>> EchoHandler.test('echo Yes (german)')
    ['Ja']

    >>> EchoHandler.test('echo Yes (fr)')
    ['Oui']


    If the language is invalid or unknown, the text is returned as-is.

    >>> EchoHandler.test('echo No (x)')
    ['No']
    """

    keyword = "echo"
    _suffix = re.compile(
        r"\s*?\((?P<lang>.+?)\)$")

    def help(self):
        self.respond("To echo some text, send: ECHO <ANYTHING>")

    def handle(self, text):

        # extract and crop the language code, if present.
        mat = self._suffix.search(text)
        text = self._suffix.sub("", text)

        # send back the (remaining) text.
        response = self.respond(text)

        # if a language code was found, override the language of the
        # response, to resolve it inline. obviously, this will only
        # work where *text* has already been localized.
        if mat is not None:
            response.language =\
                mat.group("lang")
