#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import rapidsms
from rapidsms.message import Message
from rapidsms.connection import Connection
from rapidsms.parsers.keyworder import * 

import models

class App(rapidsms.app.App):

    # lets use the Keyworder parser!
    kw = Keyworder()

    def parse(self, message):
        pass 


    def handle(self, message):
        try:
            if hasattr(self, "kw"):
                try:
                    # attempt to match tokens in this message
                    # using the keyworder parser
                    func, captures = self.kw.match(self, message.text)
                    func(self, message, *captures)
                    # short-circuit handler calls because 
                    # we are responding to this message
                    return True
                except Exception, e:
                    # TODO only except NoneType error
                    # nothing was found, use default handler
                    self.incoming_report(message)
                    return True
            else:
                self.debug("App does not instantiate Keyworder as 'kw'")
        except Exception, e:
            self.error(e) 


    def outgoing(self, message):
        pass 

    def __get(self, model, **kwargs):
	    try:
		    # attempt to fetch the object
		    return model.objects.get(**kwargs)
	    
	    # no objects or multiple objects found (in the latter case,
	    # something is probably broken, so perhaps we should warn)
	    except (ObjectDoesNotExist, MultipleObjectsReturned):
		    return None

    def __identify(self, message, task=None):
	    reporter = self.__get(Reporter, connection=message.connection)
	    
	    # if the caller is not identified, then send
	    # them a message asking them to do so, and
	    # stop further processing
	    if not reporter:
		    msg = "Please register your mobile number"
		    if task: msg += " before %s" % (task)
		    msg += ", by replying: I AM <USERNAME>"
		    message.respond(msg)
	    
	    return reporter 

    # HELP----------------------------------------------------------
    @kw("help")
    def help(self, message):
        message.respond("HELP!")
    

    # ALERT <NOTICE> ----------------------------------------------------------
    kw.prefix = "alert"

    @kw("(whatever)")
    def alert(self, message):
	    reporter = self.__identify(message.connection, "alerting")
	    Notification.objects.create(reporter=reporter, resolved=0, notice=notice)
	    message.respond("Thanks, %s. Your supervisor has been alerted." % (reporter.first_name))

    # SUBMIT A REPORT--------------------------------------------------------

    def incoming_report(self, message):
	reporter = self.__identify(message.connection, "reporting")
    	message.respond("Thanks for reporting, %s." % (reporter.first_name))
