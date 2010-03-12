#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.contrib import handlers


class EchoHandler(handlers.KeywordHandler):
    """
    Handle any message prefixed ECHO, responding with the remainder of
    the text. Useful for remotely checking that the router is running.
    """

    keyword = "echo"

    def help(self):
        self.respond("To echo some text, send: ECHO <ANYTHING>")

    def handle(self, text):
        self.respond(text)
