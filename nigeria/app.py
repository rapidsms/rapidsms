#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re
from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import rapidsms
from rapidsms.parsers.keyworder import * 

from models import *
from formslogic import *
import apps.form.app as forms_app

class App(rapidsms.app.App):

    # lets use the Keyworder parser!
    kw = Keyworder()
    
    def start(self):
        # initialize the forms app for nigeria
        self.forms_app = forms_app.App("Nigeria Forms", self.router, self)
        self.forms_app.register("nigeria", NigeriaFormsLogic())
        

    def parse(self, message):
        self.handled = False

    def handle(self, message):
        try:
            if hasattr(self, "kw"):
                try:
                    self.debug("HANDLE")
                    # attempt to match tokens in this message
                    # using the keyworder parser
                    func, captures = self.kw.match(self, message.text)
                    func(self, message, *captures)
                    # short-circuit handler calls because 
                    # we are responding to this message
                    return self.handled 
                except TypeError:
                    # TODO only except NoneType error
                    # nothing was found, use default handler
                    self.debug("NO MATCH")
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

    # HELP ----------------------------------------------------------
    @kw("help")
    def help(self, message):
        message.respond("HELP!")
        self.handled = True
    

    # ALERT <NOTICE> ----------------------------------------------------------
    kw.prefix = "alert"

    @kw("(whatever)")
    def alert(self, message, notice):
        ''' todo 
        reporter = self.__identify(message.connection, "alerting")
        Notification.objects.create(reporter=reporter, notice=notice)
        message.respond("Thanks, %s. Your supervisor has been alerted." % (reporter.first_name))
        self.handled = True
        '''
        pass
    
    def register(self, regex, function):
        '''Registers a function with the keyworder'''
        self.info("Registering regex: %s for function %s, %s" %(regex, function.im_class, function.im_func.func_name))
        self.kw.regexen.append((re.compile(regex, re.IGNORECASE), function))
        
