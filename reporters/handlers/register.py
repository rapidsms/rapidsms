#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from rapidsms.contrib.apps.handlers import KeywordHandler
from rapidsms.contrib.apps.search.utils import extract_objects
from reporters.models import Reporter
from locations.models import Location
from i18n.models import Language


class RegisterHandler(KeywordHandler):
    """
        Allows callers to register themselves, which creates a Reporter object.
        Examples:
        
        >>> what
    """

    keyword = "register|reg|join"

    def help(self):
        self.respond("To register, send JOIN <NATIONAL-ID>")

    def handle(self, text):

        # extract the optional fields early, if they were
        # provided, to avoid them ending up in the name
        languages, text = extract_objects(text, [Language])
        locations, text = extract_objects(text, [Location])

        resp = "Thank you for registering"

        # REMOVE THE VILLAGE NAME! :O
        text = re.sub("\s+\S+$", "", text, re.I)

        # create the new reporter
        alias, fn, ln = Reporter.parse_name(text)
        rep = Reporter.objects.create(
            alias=alias,
            first_name=fn,
            last_name=ln,
            registered_self=True)

        # set the optional fields, if they were provided
        if languages:
            rep.language = languages[0]
            resp += " in %s" % (rep.language)

        if locations:
            rep.location = locations[0]
            resp += " at %s" % (rep.location)

        rep.save()

        # attach the reporter to the current connection
        self.msg.persistant_connection.reporter = rep
        self.msg.persistant_connection.save()

        self.respond("%s." % resp)
