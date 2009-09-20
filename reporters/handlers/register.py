#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4


import re
from rapidsms.contrib.apps.handlers import KeywordHandler
from rapidsms.contrib.apps.search.utils import extract_objects
from reporters.models import Reporter
from locations.models import Location


class RegisterHandler(KeywordHandler):
    """
        Allows callers to register themselves, which creates a Reporter object.
        Examples:
        
        >>> what
    """

    keyword = "register|reg|j[oô0][iî1l]n"

    def help(self):
        self.respond("To register, send JOIN <NATIONAL-ID> <LANGUAGE>")

    def handle(self, text):

        # extract the optional fields early, if they were
        # provided, to avoid them ending up in the name
        #languages, text = extract_objects(text, [Language])
        locations, text = extract_objects(text, [Location])

        languages = {
            "en": "English",
            "fr": "French",
            "rw": "Kinyarwandan"
        }

        # check for the HARD CODED
        # LANGUAGE STRING whoops
        lang_code = None
        for l in languages.keys():
            regex = re.compile(r"\b(%s)\b" % l, re.I)
            m = re.search(regex, text)
            if m is not None:
                lang_code = m.group(0)
                text = regex.sub("", text, re.I)

        # REMOVE THE VILLAGE NAME! :O
        #text = re.sub("\s+\S+$", "", text, re.I)

        # create the new reporter
        #alias, fn, ln = Reporter.parse_name(text)
        alias = self._national_id()
        rep, created = Reporter.objects.get_or_create(
            alias=alias,
            #first_name=fn,
            #last_name=ln,
            registered_self=True)
        
        # set the optional fields, if they were provided
        if lang_code:
            rep.language = lang_code.lower()
            #resp += " in %s" % (languages[rep.language])

        if locations:
            rep.location = locations[0]
            resp = "Thank you for registering at %(fosa)s FOSA."
            fosa = rep.location
            #resp += " at %s" % (rep.location)
        else:
            resp = "Thank you for registering." % (rep)
            fosa = None

        rep.save()

        # attach the reporter to the current connection
        self.msg.persistant_connection.reporter = rep
        self.msg.persistant_connection.save()
        self.respond(resp, fosa=fosa)
