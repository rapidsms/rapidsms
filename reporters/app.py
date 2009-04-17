#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re
import rapidsms
from rapidsms.parsers import Matcher
from models import *

class App(rapidsms.app.App):
    MSG = {
        "en": {
            "bad-alias":   "Sorry, I don't know anyone by that name.",
            "first-login": "Hello, %(name)s! This is the first time I've met you.",
            "login":       "Hello, %(name)s! It has been %(days)d days since I last heard from you.",
            "reminder":    "I think you are are %(name)s.",
            "dont-know":   "Sorry, I don't know who you are.",
            "lang-set":    "I will now speak to you in English, where possible.",
            "denied":      "Sorry, you must identify yourself before you can do that." },
            
        # worst german translations _ever_
        # just an example. all of this stuff
        # should be moved to an i18n app!
        "de": {
            "bad-alias":   "Tut mir leit, ich weiss nicht diesen Namen",
            "first-login": "%(name)s hallo! Ich habe nicht gesehen, bevor Sie",
            "login":       "%(name)s hallo! Ich habe nicht gesehen, Sie sich fur %(days)d Tag",
            "reminder":    "Sie sind %(name)s.",
            "lang-set":    "Sie sind Deutsche." }}
    
    
    def __str(self, key, reporter=None, lang=None):
        
        # if no language was explicitly requested,
        # inherit it from the reporter, or fall
        # back to english. because everyone in the
        # world speaks english... right?
        if lang is None:
            if reporter is not None:
                lang = reporter.language
            
            # fall back
            if lang is None:
                lang = "en"

        # look for an exact match, in the language
        # that the reporter has chosen as preferred
        if lang is not None:
            if lang in self.MSG:
                if key in self.MSG[lang]:
                    return self.MSG[lang][key]
        
        # not found in localized language. try again in english
        # TODO: allow the default to be set in rapidsms.ini
        return self.__str(key, lang="en") if lang != "en" else None
        
    
    
    def __connection(self, msg):
        """Given a message, search for a PersistantConnection
           object for an matching the backend and identity,
           which indicates that it was created via the same
           device (not necessarily the same person, though!)."""
        try:
            ident = msg.connection.identity
            bck = PersistantBackend.from_message(msg)
            return PersistantConnection.objects.get(
                identity=ident, backend=bck)
        
        # the caller is unknown to us...
        except PersistantConnection.DoesNotExist:
            return None

    def __deny(self, msg):
        """Responds to an incoming message with a localizable
           error message to instruct the caller to identify."""
        return msg.respond(self.__str("denied", msg.reporter))
        
    
    def parse(self, msg):
        
        # fetch the persistantconnection object
        # for this message's sender, and abort
        # if we've never seen them before
        conn = self.__connection(msg)
        if conn is None:
            msg.persistant_backend = None
            msg.persistant_connection = None
            msg.reporter = None
            return False
            
        # stuff all that useful meta-data into
        # the message, for other apps to observe
        msg.persistant_backend = conn.backend
        msg.persistant_connection = conn
        msg.reporter = conn.reporter
        
        self.info("Identified %s as %r" % (conn.reporter, msg.reporter))
        
        # update last_seen, which automatically
        # populates the same property 
        conn.seen()
            
    
    
    def handle(self, msg):
        matcher = Matcher(msg)
        
        # TODO: this is sort of a lightweight implementation
        # of the keyworder. it wasn't supposed to be. maybe
        # replace it *with* the keyworder, or extract it
        # into a parser of its own
        map = {
            "identify": ["identify (slug)", "this is (slug)", "i am (slug)"],
            "register": ["register (slug) (slug) (slug) (whatever)"],
            "remind":   ["whoami", "who am i"],
            "lang":     ["lang (slug)"]
        }
        
        # search the map for a match, dispatch
        # the message to it, and return/stop
        for method, patterns in map.items():
            if matcher(*patterns) and hasattr(self, method):  
                return getattr(self, method)(msg, *matcher.groups)
        
        # no matches, so this message is not
        # for us; allow processing to continue
        return False
    
    
    def identify(self, msg, alias):
        try:
            
            # give me reporter.
            # if no alias will match,
            # exception must raise
            rep = Reporter.objects.get(alias=alias)
            
        # no such alias, but we can be pretty sure that the message
        # was for us, since it matched a pretty specific pattern
        # TODO: levenshtein spell-checking from rapidsms/ethiopia
        except Reporter.DoesNotExist:
            msg.respond(self.__str("bad-alias"))
            return True
        
        # find (or create) the PersistantConnection object for
        # this message's sender, or create a fresh one if this
        # is the first time we've heard from this device
        ident = msg.connection.identity
        bck = PersistantBackend.from_message(msg)
        conn, created = PersistantConnection.objects.get_or_create(
            identity=ident, backend=bck)
        
        # assign the reporter to it (it may have
        # already been linked to someone else!)
        conn.reporter = rep
        conn.save()
        
        # send a welcome message back to the now-registered reporter,
        # depending on how long it's been since their last visit
        ls = rep.last_seen()
        if ls is not None:
            msg.respond(
                self.__str("login", rep) % {
                    "name": unicode(rep),
                    "days": (datetime.now() - ls).days })
        
        # or a slightly different welcome message
        else:
            msg.respond(
                self.__str("first-login", rep) % {
                    "name": unicode(rep) })
        
        # re-call this app's prepare, so other apps can
        # get hold of the reporter's info right away
        self.parse(msg)
    
    
    def remind(self, msg):
        
        # if a reporter object was attached to the
        # message by self.parse, respond with a reminder
        if msg.reporter is not None:
            msg.respond(
                self.__str("reminder", msg.reporter) % {
                    "name": unicode(msg.reporter) })
        
        # if not, we have no idea
        # who the message was from
        else:
            msg.respond(self.__str("dont-know", msg.reporter))

    
    def lang(self, msg, code):
        
        # reqiure identification to continue
        # TODO: make this check a decorator, so other apps
        #  can easily indicate that methods need a valid login
        if msg.reporter is not None:
        
            # if the language code was valid, save it
            # TODO: obviously, this is not cross-app
            if code in self.MSG:
                msg.reporter.language = code
                msg.reporter.save()
                resp = "lang-set"
            
            # invalid language code. don't do
            # anything, just send an error message
            else: resp = "bad-lang"
        
        # if the caller isn't logged in, send
        # an error message, and halt processing
        else: resp = "denied"
        
        # always send *some*
        # kind of response
        msg.respond(
            self.__str(
                resp, msg.reporter))

    
    def register(self, msg, location_code, role, password, name):
        pass

