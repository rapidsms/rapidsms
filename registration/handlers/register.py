#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.contrib.handlers import KeywordHandler
from rapidsms.models import Contact


class RegisterHandler(KeywordHandler):
    """
    """

    keyword = "register|reg|join"

    def help(self):
        self.respond("To register, send JOIN <NAME>")

    def handle(self, text):
        contact = Contact.objects.create(name=text)
        self.msg.connection.contact = contact
        self.msg.connection.save()

        self.respond(
            "Thank you for registering, %(name)s!",
            name=contact.name)
