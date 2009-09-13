#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re
from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import rapidsms
from rapidsms.parsers.keyworder import * 

from models import *
from formslogic import *
import form.app as form_app
import supply.app as supply_app

from form.models import Domain


class App(rapidsms.app.App):

    # lets use the Keyworder parser!
    kw = Keyworder()
    
    def start(self):
        # initialize the forms app for nigeria
        self._form_app = form_app.App(self.router)
        # this tells the form app to add itself as a message handler 
        # which registers the regex and function that this will dispatch to 
        self._form_app.add_message_handler_to(self)
        # this tells the form app that this is also a form handler 
        self._form_app.add_form_handler("nigeria", NigeriaFormsLogic())
        # initialize the supply app
        self._supply_app = supply_app.App("Nigeria Supplies", self.router)
        # this tells the supply app to register with the forms app as a form handler
        self._supply_app.add_form_handler_to(self._form_app)

    def parse(self, message):
        self.handled = False

    def handle(self, message):
        self.handled = False
        try:
            if hasattr(self, "kw"):
                self.debug("HANDLE")
                
                # attempt to match tokens in this message
                # using the keyworder parser
                results = self.kw.match(self, message.text)
                if results:
                    func, captures = results
                    # if a function was returned, then a this message
                    # matches the handler _func_. call it, and short-
                    # circuit further handler calls
                    func(self, message, *captures)
                    return self.handled
                else:
                    self.debug("NO MATCH FOR %s" % message.text)
            else:
                self.debug("App does not instantiate Keyworder as 'kw'")
        except Exception, e:
            self.log_last_exception()


    def cleanup(self, message):
        # this will add a generic response based 
        # on the available forms
        if not message.responses:
            message.respond("Sorry we didn't understand that. %s" % self.form_app.get_helper_message())
        

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
    
    
    
    
    # <DOMAIN> REGISTER <LOCATION> <ROLE> <PASSWORD> <NAME> ---------
    
    # since we want to capture all messages starting with "<DOMAIN> REGISTER"
    # but not "(SLUG) REGISTER",  we must build this keyworder prefx dynamically.
    # unfortunately, this means that rapidsms must be restarted when Domain changes
#    domain_codes = Domain.objects.values_list("code", flat=True)
#    kw.prefix = "(%s) register" % ("|".join(domain_codes))
#    
#    @kw.invalid()
#    def register_fail(self, msg, domain, rest):
#        msg.respond("Domain=%s, Rest=%s" % (domain, rest))
    
    
    # ALERT <NOTICE> ------------------------------------------------
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
    
    def add_message_handler(self, regex, function):
        '''Registers a message handler with this app.  Incoming messages that match this 
           will call the function'''
        self.info("Registering regex: %s for function %s, %s" %(regex, function.im_class, function.im_func.func_name))
        self.kw.regexen.append((re.compile(regex, re.IGNORECASE), function))
        
    @property
    def form_app(self):
        if hasattr(self, "_form_app"):
            return self._form_app

    @property
    def supply_app(self):
        if hasattr(self, "_supply_app"):
            return self._supply_app

    
