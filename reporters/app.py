#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
import rapidsms
from rapidsms.parsers import Matcher
from persistance.models import *
from locations.models import *
from models import *


from i18n.app import InternationalApp


class App(rapidsms.App, InternationalApp):
    #kw = Keyworder()


    def _deny(self, msg):
        return msg.respond(
            self._str(msg, "must-identify"))


    #def configure(self, allow_join, allow_list, **kwargs):
    #    self.allow_join = allow_join
    #    self.allow_list = allow_list
    def configure(self, **kwargs):
        self.allow_join = True
        self.allow_list = False


    def parse(self, msg):

        # fetch the persistantconnection object
        # for this message's sender (or create
        # one if this is the first time we've
        # seen the sender), and stuff the meta-
        # dta into the message for other apps
        conn = PersistantConnection.from_message(msg)
        msg.persistant_connection = conn
        msg.reporter = conn.reporter

        # store a handy dictionary containing the most personal persistance
        # information that we have about this connection, for other apps to
        # easily link back to it. See PersistantConnection for more docs.
        msg.persistance_dict = conn.dict

        # log, whether we know who the sender is or not
        if msg.reporter: self.info("Identified: %s as %r" % (conn, msg.reporter))
        else:            self.info("Unidentified: %s" % (conn))

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
            "register":  ["(?:join|register|reg) (whatever)"],
            "identify":  ["identify (slug)", "this is (slug)", "i am (slug)"],
            "reporters": ["list reporters", "reporters\\?"]
        }

        # search the map for a match, dispatch
        # the message to it, and return/stop
        for method, patterns in map.items():
            if matcher(*patterns) and hasattr(self, method):  
                getattr(self, method)(msg, *matcher.groups)
                return True

        # no matches, so this message is not
        # for us; allow processing to continue
        return False



    #kw.prefix = ["join", "register", "reg"]


    def register(self, msg, name):

        # abort if self-registration isn't allowed
        if not self.allow_join:
            msg.respond(self._str("function-disabled"))
            return True

        try:
        
            langfield = "en"
            
            # use language codes from internalization model. e.g Internalization.object.get().valuelist(codes);
            langcodes = ["en","fr","ki","de"]
            allwords = name.split()
              
             # find the language code in the list of codes is not there then its not a language code ignone it.
             #if International.objects.filter(allWords[allWords.length]).count():
            if allwords[-1] in langcodes:
	            langfield = allwords.pop(-1)
	            name = " ".join(allwords)

            alias = None
            IsNumber = False
            
            # Determine if name is a First,Last Name OR a code (number, national id in Rwanda)
            m = re.match("^(\d+)$", name.replace(" ", ""), re.IGNORECASE)
            if m is not None:
                MatchCode = m.groups()
                IsNumber = True
                alias = MatchCode[0] #Reporter.parse_code(name)  
            else:
                # parse the name, and create a reporter
                alias, fn, ln = Reporter.parse_name(name)
               
            if not IsNumber:
                rep = Reporter(
                    first_name=fn, last_name=ln,
                    alias=alias, registered_self=True)
                rep.save()                
                
            if IsNumber:
                if Reporter.IsCodeUnique(alias):
                    rep = Reporter(alias=alias, registered_self=True)
                    rep.save()
                else:
                    rep = Reporter.objects.get(alias__iexact=alias) #not sure about syntax.
                    rep.language = langfield 
                    rep.save()
                    
            if hasattr(msg, "location"):
               repln = ReporterLocation( reporter = rep, location = msg.location)
               repln.save()      

            # attach the reporter to the current connection
            msg.persistant_connection.reporter = rep
            msg.persistant_connection.save()

            msg.respond(
                self._str("first-login", rep,
                    rep.full_name(),
                    rep.alias))

        # something went wrong - at the
        # moment, we don't care what
        except:
            msg.respond("Sorry, I couldn't register you.")
            raise

    def identify(self, msg, alias):
        try:
            rep = Reporter.objects.get(
                alias=alias)

        # no such alias, but we can be pretty sure that the message
        # was for us, since it matched a pretty specific pattern
        # TODO: levenshtein spell-checking from rapidsms/ethiopia
        except Reporter.DoesNotExist:
            msg.respond(self._str("bad-alias"))
            return True


        # before updating the connection, take note
        # of the last time that we saw this reporter
        ls = rep.last_seen()

        # assign the reporter to this message's connection
        # (it may currently be assigned to someone else)
        msg.persistant_connection.reporter = rep
        msg.persistant_connection.save()
        msg.reporter = rep


        # send a welcome message back to the now-registered reporter,
        # depending on how long it's been since their last visit
        if ls is not None:
            msg.respond(
                self._str(
                    "login", rep,
                    unicode(rep)))

        # or a slightly different welcome message
        else:
            msg.respond(
                self._str("first-login", rep,
                    unicode(rep),
                    rep.alias))

        # re-call this app's prepare, so other apps can
        # get hold of the reporter's info right away
        self.parse(msg)


    def reporters(self, msg):

        # abort if listing reporters isn't allowed
        # (it can get rather long and expensive)
        if not self.allow_join:
            msg.respond(self._str("function-disabled"))
            return True

        # not identified yet; reject, so
        # we don't allow random people to
        # query our reporters list
        if msg.reporter is None:
            msg.respond(self._str("must-identify"))
            return True

        # collate all reporters, with their full name,
        # username, and current connection.
        items = [
            "%s (%s) %s" % (
                rep.full_name(),
                rep.alias,
                rep.connection().identity)
            for rep in Reporter.objects.all()
            if rep.connection()]

        # respond with the concatenated list.
        # no need to check for empty _items_. there will
        # always be at least one reporter, because only
        # identified reporters can trigger this handler
        msg.respond(
            self._str("list", msg.reporter,
                items=", ".join(items),
                noun="reporters",
                num=len(items)))
