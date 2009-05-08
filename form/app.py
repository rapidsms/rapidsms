#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re
from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import rapidsms
from rapidsms.parsers.keyworder import * 
from rapidsms.message import StatusCodes

from models import *
from utils import *

class App(rapidsms.app.App):
    
    def __init__(self, router):
        super(App, self).__init__(router) 
        self.separator = "[,\.\s]+"
        self.token_separator = "[,\.\s]*"
        self.leading_pattern = "[\"'\s]*"
        self.separator = "[,\.\s]+"
        self.token_separator = "[,\.\s]*"
        self.leading_pattern = "[\"'\s]*"
        self.trailing_pattern = "[\.,\"'\s]*"
        self.form_patterns = [] 
        self.domains_forms_tokens = []
        self.setup()
        # allow apps to register to be a part of the message handling control flow
        self.form_handlers = {}
        #self.handled = False

    def start(self):
        pass
    
        
    def parse(self, message):
        #self.handled = False
        pass

    def handle(self, message):
        # right now the forms app assumes it'll be called by someone else
        pass  
        
    def outgoing(self, message):
        pass 
    
    def add_form_handler(self, name, app):
        self.form_handlers[name] = app 

    def add_message_handler_to(self, dispatcher):
        if self.form_patterns:
            for form_pattern in self.form_patterns:
                dispatcher.add_message_handler(form_pattern, self.form)
            
        else:
            self.warning("add_message_handler_to was called with no form_patterns. Have you loaded your fixtures?")
            
    
    def setup(self):
        # create a list of dictionaries mapping domains to lists of their
        # forms, which are dictionaries mapping forms to a list
        # of their tokens, as tuples of token.abbr, token.regex
        # e.g.,
        # [    
        #      {(domain.code.abbreviation, domain.code.regex) : 
        #          [
        #          {(form.code.abbreviation, form.code.regex) : 
        #               [(token.abbr, token.regex),...]},
        #          ...
        #          ]
        #       },
        #       ...
        # ]
        # 
        domains = Domain.objects.all()
        for d in domains:
            # gather forms for this domain
            forms = d.domain_forms.all().order_by('sequence')
            forms_tokens = []
            for f in forms:
                # gather tokens for this form as a list of tuples
                form_tokens = f.form.form_tokens.order_by('sequence')
                tokens = []
                for ft in form_tokens:
                    tokens.append((ft.token.abbreviation, ft.token.regex))

                # make a dictionary mapping this form type to its token list
                # and add the dict to the running form_tokens list
                forms_tokens.append(dict([((f.form.code.abbreviation.upper(), f.form.code.regex), tokens)]))

                # put together domain pattern, form pattern, and token patterns
                # along with leading patterns, separators, etc
                form_pattern = self.leading_pattern + d.code.regex + \
                    self.separator + f.form.code.regex + self.separator + \
                    ''.join(['(?:%s%s)?' % (self.token_separator, t[1]) for t in tokens]) + \
                    self.trailing_pattern
                self.form_patterns.append(form_pattern)

            # make a dictionary mapping this domain code to its form list
            # and add the dict to the running domain_form_tokens list
            self.domains_forms_tokens.append(dict([((d.code.abbreviation.upper(), d.code.regex), forms_tokens)]))


    def __get(self, model, **kwargs):
        try:
            # attempt to fetch the object
            return model.objects.get(**kwargs)

        # no objects or multiple objects found (in the latter case,
        # something is probably broken, so perhaps we should warn)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return None


    # SUBMIT A FORM --------------------------------------------------------

    def form(self, app, message, code, type, *data): 
        self.debug("FORM")
        self.debug(data)
        for domain in self.domains_forms_tokens:
            domain_matched = self._get_code(code, domain)
            self.debug(domain_matched)

            if domain_matched:
                # gather list of form dicts for this domain code
                # forms = domain[code.upper()]
                self.debug("DOMAIN MATCH")
                forms = domain[domain_matched]
                for form in forms:
                    form_matched = self._get_code(type, form)
                    self.debug(form_matched)

                    if form_matched:
                        this_domain = Domain.objects.get(code__abbreviation__iexact=domain_matched[0])
                        this_form = Form.objects.get(code__abbreviation__iexact=form_matched[0])
                        if hasattr(message, "reporter") and message.reporter:
                            this_form.reporter = message.reporter
                        else:
                            # there was no reporter set.  We allow this
                            # currently, but we may want to create one or 
                            # respond here.
                            pass
                        form_entry = FormEntry.objects.create(domain=this_domain, \
                            form=this_form, date=message.date)
                        # gather list of token tuples for this form type
                        tokens = form[form_matched]

                        self.debug("FORM MATCH")
                        info = []
                        for t, d in zip(tokens, data):
                            if not d:
                                self.debug("Empty data for token: %s." % t[0])
                                d = ""
                            this_token = Token.objects.get(abbreviation=t[0])
                            token_entry = TokenEntry.objects.create(\
                                form_entry=form_entry, token=this_token, data=d)
                            # gather info for confirmation message, matching
                            # abbreviations from the token tuple to the received data
                            info.append("%s=%s" % (t[0], d or "??"))

                        # call the validator methods, which return False on
                        # success, or a list of error messages on failure
                        validation_errors = self._get_validation_errors(message, this_form, form_entry)

                        # if no errors were returned (from ANY
                        # registered app), call the actions
                        if not validation_errors:
                            before = len(message.responses)
                            self._do_actions(message, this_form, form_entry)
                            after = len(message.responses)
                            
                            # if the action(s) didn't send any responses,
                            # then send the default confirmation. this is
                            # just for backwards compatibility, really...
                            # actions SHOULD send their own confirmation
                            if(after <= before):
                                message.respond("Received report for %s %s: %s.\nIf this is not correct, reply with CANCEL" % \
                                    (domain_matched[0], form_matched[0], ", ".join(info)))                        

                        # oh no! there were validation errors!
                        # since we've already matched the domain
                        # and form, we can be pretty sure that
                        # this was a valid attempt at submitting
                        # this form - so send back the errors,
                        # and note that we've handled this one
                        else:
                            self.debug("Invalid form. %s", ". ".join(validation_errors))
                            message.respond("Invalid form. %s" % ". ".join(validation_errors), StatusCodes.APP_ERROR)
                            return
                        
                        # stop processing forms, move
                        # on to the next domain (!?)
                        break

                    else:
                        continue        
                
                # this is now handled at a higher level 
                # (e.g. by the nigeria app)
                # the new parsing logic calls this method
                # not to be called at all if none of the 
                # forms match so we can never reach this code
                #if not handled:
                #    message.respond("Oops. Cannot find a report called %s for %s. Available reports for %s are %s" % \
                #        (type.upper(), domain_matched[0], domain_matched[0], ", ".join([f.keys().pop().upper() for f in forms])), 
                #        StatusCodes.APP_ERROR) 
                #    handled = True
                #    break

            else:
                # this was probably just a message for another
                # app so don't bother sending a message
                pass
                #if not hasattr(self, "handled") or not self.handled:
                #    message.respond("Oops. Cannot find a supply called %s. Available supplies are %s" %\
                #        (code.upper(), ", ".join([d.keys().pop().upper() for d in self.domains_forms_tokens])))

    def get_helper_message(self):
        domains = Domain.objects.all()
        domain_helpers = []
        for d in domains:
            # gather forms for this domain
            forms = d.domain_forms.all().order_by('sequence')
            forms_names = [f.form.code.abbreviation.upper() for f in forms]
            this_domain_msg = "%s: %s" % (d.code.abbreviation.upper(), ", ".join(forms_names))
            domain_helpers.append(this_domain_msg)
        return "Available forms are %s" % " or ".join(domain_helpers)
    
    def _get_code(self, code, dict):
        '''Gets the code out of the code and dict.  This allows us to 
           try to match each token's regex'''
        for tuple in dict.keys():
            if re.match(tuple[1], code, re.IGNORECASE):
                return tuple
        return False

        
    def _get_validation_errors(self, message, form, form_entry):
        validation_errors = []
        
        # do form level validation
        form_errors = form.get_validation_errors(form_entry)
        if form_errors: 
            validation_errors.extend(form_errors)
        
        # also forward to any apps that have registered with this
        for app_name in form.apps.all():
            if self.form_handlers.has_key(app_name.name):
                app = self.form_handlers[app_name.name]
                errors = getattr(app,'validate')(message, form_entry)
                if errors: validation_errors.extend(errors)
        #print "VALIDATION ERRORS: %r" % validation_errors
        return validation_errors
        
    def _do_actions(self, message, form, form_entry):
        for app_name in form.apps.all():
            if self.form_handlers.has_key(app_name.name):
                app = self.form_handlers[app_name.name]
                getattr(app,'actions')(message, form_entry)
                            
