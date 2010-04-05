#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.contrib.handlers import KeywordHandler
from rapidsms.models import Contact
from rapidsms.conf import settings


class LanguageHandler(KeywordHandler):
    """
    """

    keyword = "language|lang"

    def help(self):
        self.respond("To set your language, send LANGUAGE <CODE>")

    def handle(self, text):
        for code, name in settings.LANGUAGES:
            if text != code and text != name:
                continue

            self.msg.contact.language = code
            self.msg.contact.save()

            return self.respond(
                "I will speak to you in %(language)s.",
                language=name)

        self.error(
            "Sorry, I don't speak '%(language)s'.",
            language=text)
