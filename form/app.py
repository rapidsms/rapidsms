#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re
from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import rapidsms
from rapidsms.parsers.keyworder import * 

from models import *
from utils import *

class App(rapidsms.app.App):
    
    def __init__(self, title, router):
        super(App, self).__init__(title, router) 
        self.separator = "[,\.\s]*"
        self.leading_pattern = "[\"'\s]*"
        self.trailing_pattern = "[\.,\"'\s]*"
        self.form_pattern = None 
        self.domains_forms_tokens = []
        self.setup()
        # allow apps to register to be a part of the message handling control flow
        self.form_handlers = {}
        

    def start(self):
        pass
    
        
    def parse(self, message):
        pass

    def handle(self, message):
        # right now the forms app assumes it'll be called by someone else
        pass  
        
    def outgoing(self, message):
        pass 
    
    def add_form_handler(self, name, app):
        self.form_handlers[name] = app 

    def add_message_handler_to(self, dispatcher):
        dispatcher.add_message_handler(self.form_pattern, self.form)
    
    def setup(self):
        # create a list of dictionaries mapping domains to lists of their
        # forms, which are dictionaries mapping form types to a list
        # of their tokens, as tuples of token.abbr, token.regex
        # e.g.,
        # [    
        #      {domain_code : 
        #          [
        #          {form_type : [(token.abbr, token.regex),...]},
        #          ...
        #          ]
        #       },
        #       ...
        # ]
        # 
        domains = Domain.objects.all()
        for d in domains:
            # gather forms for this domain
            forms = d.forms.all()
            forms_tokens = []
            for f in forms:
                # gather tokens for this form as a list of tuples
                tokens = f.tokens.order_by('sequence').\
                            values_list('abbreviation', 'regex')
                # make a dictionary mapping this form type to its token list
                # and add the dict to the running form_tokens list
                forms_tokens.append(dict([(f.type.upper(), tokens)]))
            # make a dictionary mapping this domain code to its form list
            # and add the dict to the running domain_form_tokens list
            self.domains_forms_tokens.append(dict([(d.code.upper(), forms_tokens)]))

        # lists for keeping track of domain codes, form types, and 
        # number of tokens for use generating ranges
        domain_code_lengths = []
        form_type_lengths = []
        number_of_tokens = []
        # list for keeping track token sequences
        sequence_tokens = []
        if not self.domains_forms_tokens:
            return
        for domain_forms_tokens in self.domains_forms_tokens:
            for domain_code, forms in domain_forms_tokens.iteritems():
                # add the length of the domain code to our list
                domain_code_lengths.append(len(domain_code))
                for form in forms:
                    for form_type, tokens in form.iteritems():
                        # add the length of the form type to our list
                        form_type_lengths.append(len(form_type))
                        # add the number of tokens for this form to our list
                        number_of_tokens.append(len(tokens))
                        for i, token in enumerate(tokens):
                            # add a tuple of token's sequence and pattern to our list
                            sequence_tokens.append((i, token[1]))

        # list for final patterns for each sequence
        pattern_for_sequences = []
        # iterate up to the maximum number of tokens (longest form)
        number_of_tokens.sort()
        for n in range(number_of_tokens[ - 1]):
            # gather all tokens that are at this sequence
            # (all tokens that are the third token in a report, for example)
            def tokens_at_sequence(t): return t[0] == n
            patterns_at_sequence = filter(tokens_at_sequence, sequence_tokens)
            # gather the unique patterns out of these tokens and create a
            # regex for all of them (by adding an or between them all)
            #
            # let me break it down, starting from the inside:
            # do a list comprehension to get the pattern from the second 
            # position in the tuple, then limit to unique patterns, then
            # join the patterns together with a pipe between each one, and
            # finally add the resulting pattern to the list
            unique_patterns = '|'.join(unique(map((lambda t: t[1]), patterns_at_sequence)))
            self.debug("UNIQUE PATTERN " + str(n))
            self.debug(unique_patterns)
            # fix any patterns we just or-ed together so they are the kind of or we want
            # e.g., (\w+)|(\d+) => (\w+|\d+)
            # TODO figure out how to handle non-captured matches
            # e.g., (?:\w+)|(\d+) => (?:\w+)|(\d+) and then zip up tokens correctly
            pattern_for_sequences.append(unique_patterns.replace(')|(', '|'))
        self.debug("PATTERN FOR SEQUENCES")
        self.debug(pattern_for_sequences)

        # create a pattern for domain_code that matches any word as long as
        # the shortest code and no longer than the longest code
        domain_code_lengths.sort()
        #TODO oops. this only captures the last character if the range is {4,4}
        #domain_code_pattern = '(\w){%s,%s}' % (domain_code_lengths[0], domain_code_lengths[-1])
        #domain_code_pattern = '(letters)'
        domain_code_pattern = '([a-z]+)'
        # create a pattern for form type that matches any word as long as
        # the shortest code and no longer than the longest code
        form_type_lengths.sort()
        # TODO ditto
        #form_type_pattern = '(\w){%s,%s}' % (form_type_lengths[0], form_type_lengths[-1])
        #form_type_pattern = '(letters)'
        form_type_pattern = '([a-z]+)'

        # wrap all of the sequence patterns (except for the first one) 
        # with separators and make them optional.
        # this way all possible forms (that have at least one token)
        # will be matched, but we are able to capture n tokens
        #
        # i wonder whether doing a list comprehension or 
        # mapping a lambda is faster here
        #wrapped_patterns = ['(?:[,\.\s]*%s)?' % (p) for p in pattern_for_sequences]
        wrapped_patterns = map((lambda p: '(?:[,\.\s]*%s)?' % (p)), pattern_for_sequences[1:]) 
        # put all the patterns together!
        self.form_pattern = self.leading_pattern + domain_code_pattern + \
            self.separator + form_type_pattern + self.separator + pattern_for_sequences[0] + ''.join(wrapped_patterns) + self.trailing_pattern
        
        
        self.debug("FORM PATTERN")
        self.debug(self.form_pattern)

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
            self.handled = True
        return reporter 

    # SUBMIT A FORM --------------------------------------------------------

    def form(self, app, message, code, type, *data): 
        self.debug("FORM")
        #reporter = self.__identify(message.peer, "reporting")
        self.handled = False
        for domain in self.domains_forms_tokens:
            if code.upper() in domain:
                # gather list of form dicts for this domain code
                forms = domain[code.upper()]
                self.debug("DOMAIN MATCH")

                for form in forms:
                    if type.upper() in form:
                        this_domain = Domain.objects.get(code=code.upper())
                        this_form = Form.objects.get(type=type)
                        
                        form_entry = FormEntry.objects.create(domain=this_domain, \
                            form=this_form, date=datetime.now())
                        # gather list of token tuples for this form type
                        tokens = form[type.upper()]

                        self.debug("FORM MATCH")
                        info = []
                        for t, d in zip(tokens, data):
                            if not d:
                                self.debug("Empty data for token: %s.  This is not allowed." % t[0])
                                message.respond("Empty data for token: %s.  This is not allowed." % t[0])
                                return
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
                            self.handled = True
                            
                            # if the action(s) didn't send any responses,
                            # then send the default confirmation. this is
                            # just for backwards compatibility, really...
                            # actions SHOULD send their own confirmation
                            if(after <= before):
                                message.respond("Received report for %s %s: %s.\nIf this is not correct, reply with CANCEL" % \
                                    (code.upper(), type.upper(), ", ".join(info)))                        
                        # oh no! there were validation errors!
                        # since we've already matched the domain
                        # and form, we can be pretty sure that
                        # this was a valid attempt at submitting
                        # this form - so send back the errors,
                        # and note that we've handled this one
                        else:
                            self.debug("Invalid form.  %s", ". ".join(validation_errors))
                            message.respond("Invalid form.  %s" % ". ".join(validation_errors))
                            return
                        self.handled = True
                        
                        
                        # stop processing forms, move
                        # on to the next domain (!?)
                        break

                    else:
                        continue        

                if not self.handled:
                    # TODO ditto
                    message.respond("Oops. Cannot find a report called %s for %s. Available reports for %s are %s" % \
                        (type.upper(), code.upper(), code.upper(), ", ".join([f.keys().pop().upper() for f in forms]))) 
                    self.handled = True
                    break

            else:
                continue
                # TODO ditto
                #if not handled:
                #    message.respond("Oops. Cannot find a supply called %s. Available supplies are %s" %\
                #        (code.upper(), ", ".join([s.keys().pop().upper() for s in self.supplies_reports_tokens]))) 


    def _get_validation_errors(self, message, form, form_entry):
        validation_errors = []
        
        # do form level validation
        form_errors = form.get_validation_errors(form_entry)
        if form_errors: validation_errors.extend(form_errors)
        
        # also forward to any apps that have registered with this
        for app_name in form.apps.all():
            if self.form_handlers.has_key(app_name.name):
                app = self.form_handlers[app_name.name]
                errors = getattr(app,'validate')(message, form_entry)
                if errors: validation_errors.extend(errors)
        print "VALIDATION ERRORS: %r" % validation_errors
        return validation_errors
        
    def _do_actions(self, message, form, form_entry):
        for app_name in form.apps.all():
            if self.form_handlers.has_key(app_name.name):
                app = self.form_handlers[app_name.name]
                getattr(app,'actions')(message, form_entry)
                            
