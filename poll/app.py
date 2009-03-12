#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from datetime import date, datetime
from strings import ENGLISH as STR

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import rapidsms
from rapidsms.message import Message
from rapidsms.parsers.keyworder import * 

# import poll-specific models as p because
# poll has a Message class of its own...
import models as p
import graph
import utils

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
                    self.incoming_entry(message)
                    return True
            else:
                self.debug("App does not instantiate Keyworder as 'kw'")
        except Exception, e:
            self.error(e) 


    def outgoing(self, message):
        pass 

    # HELP
    @kw("help")
    def help(self, message):
        message.respond([
            "subscribe",
            "unsubscribe"])
    
    
    def __get(self, model, **kwargs):
        try:
            # attempt to fetch the object
            return model.objects.get(**kwargs)
        
        # no objects or multiple objects found (in the latter case,
        # something is probably broken, so perhaps we should warn)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return None

    # SUBSCRIBE ---------------------------------------------------------------
    
    kw.prefix = ["subscribe", "join"]

    @kw.blank()
    @kw("(whatever)")
    def subscribe(self, message, blah=None):
        r, created = p.Respondant.subscribe(message.caller, message.backend)
        
        # acknowledge with an appropriate message
        if created: message.respond(STR["subscribe"])
        else: message.respond(STR["resubscribe"])
    
    
    # UNSUBSCRIBE -------------------------------------------------------------
    
    kw.prefix = ["unsubscribe", "leave", "stop", "exit"]

    @kw.blank()
    @kw("(whatever)")
    def unsubscribe(self, message, blah=None):
        r, created = p.Respondant.unsubscribe(message.caller, message.backend)
        message.respond(STR["unsubscribe"])

    # SUBMIT AN ANSWER --------------------------------------------------------

    def incoming_entry(self, message):
        # make a poll.Message out of the rapidsms.models.Message
        # because utils.parse_message expects a poll.Message
        mess = p.Message.objects.create(is_outgoing=False,\
            phone=message.caller, text=message.text)

        # ensure that the caller is subscribed
        r, created = p.Respondant.subscribe(message.caller, message.backend)
        # if no question is currently running, then
        # we can effectively ignore the incoming sms,
        # but should notify the caller anyway
        ques = p.Question.current()
        if ques is None: message.respond(STR["no_question"])
        
        # try to parse the message
        # pass along the rapidsms.models.Message.backend with the
        # poll.Message object so that parse_message can check that
        # the respondant is subscribed
        # yes this is strange but is a result of porting existing
        # poll code into rapidsms 
        parsed = utils.parse_message(mess, ques, message.backend)

        # send an appropriate response to the caller
        if parsed:  
            #graph.graph_entries(ques)
            message.respond(STR["thanks"])

        else:       message.respond(STR["thanks_unparseable"])

    # TODO port broadcast and broadcast_question functions
