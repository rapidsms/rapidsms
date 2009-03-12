#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from datetime import date, datetime
from strings import ENGLISH as STR

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import rapidsms
from rapidsms.message import Message
from rapidsms.parsers.keyworder import * 

import models as p
import graph
import utils

class App(rapidsms.app.App):

    kw = Keyworder()

    def parse(self, message):
        pass 


    def handle(self, message):
        try:
            if hasattr(self, "kw"):
                try:
                    func, captures = self.kw.match(self, message.text)
                    func(self, message, *captures)
                except Exception, e:
                    print 'kw try'
                    print e             
                    # nothing was found, use default handler
                    self.incoming_entry(message)
            else:
                print 'no KW'
        except Exception, e:
            print 'handle try'
            print e 


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
        # make a poll.Message from the rapidsms.models.Message
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
        parsed = utils.parse_message(mess, ques, message.backend)

        # send an appropriate response to the caller
        if parsed:  
            #graph.graph_entries(ques)
            message.respond(STR["thanks"])

        else:       message.respond(STR["thanks_unparseable"])

    # TODO port broadcast and broadcast_question functions
