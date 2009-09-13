#!/usr/buppn/env python
# vim: ai ts=4 sts=4 et sw=4

from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ObjectDoesNotExist 
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from reporters.models import Reporter
from patterns.models import Pattern
from datetime import date
import re

class Validator():
    '''An interface that does validation.  The default implementation does nothing'''
    def get_validation_errors(self, content):
        '''Returns any errors with this content'''
        # by default this implementation will do nothing
        pass

class Validatable():
    '''Class to extend to allow validation.  The validator property should 
    be overridden with a custom implementation''' 
    
    _validator = Validator()
    
    def _get_validator(self):
        return self._validator
    def _set_validator(self, validator):
        self._validator = validator
    validator = property(_get_validator, _set_validator, None, None)
    
    def get_validation_errors(self, form):
        #print "in Validatable, next call will generate errors"
        return self._validator.get_validation_errors(form)
        

class Alerter():
    '''An interface that does alerts.  The default implementation does nothing'''
    def get_alerts(self, content):
        '''Returns any alerts generated from this content'''
        # by default this implementation will do nothing
        pass

class Alertable():
    '''Class to extend to allow alerts.  The alerter property should 
    be overridden with a custom implementation''' 
    
    _alerter = Alerter()
    
    def _get_alerter(self):
        return self._alerter
    def _set_alerter(self, alerter):
        self._alerter = alerter
    alerter = property(_get_alerter, _set_alerter, None, None)
    
    def get_alerts(self, form):
        #print "in Alertable, next call will generate alerts"
        return self._alerter.get_alerts(form)
        


class App(models.Model):
    name = models.CharField(max_length = 100)

    def __unicode__(self):
        return "%s" % (self.name)

class Form(models.Model, Validatable, Alertable):
    name = models.CharField(max_length=160)
    code = models.ForeignKey("Token")
    form_tokens = models.ManyToManyField("FormToken")
    apps = models.ManyToManyField(App)

    def __init__ (self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs) 
        self.validator = FormValidator(self)
        self.alerter = FormAlerter(self)
        
    def __unicode__(self):
        return "%s" % (self.code.abbreviation)

class Token(models.Model):
    name = models.CharField(max_length=160)
    abbreviation = models.CharField(max_length=20, unique=True)
    patterns = models.ManyToManyField(Pattern)

    def __unicode__(self):
        return "%s" % (self.abbreviation)

    def _get_regex(self):
        # convenience accessor for joining patterns
        return Pattern.join(self.patterns)
        
    regex = property(_get_regex)

class FormToken(models.Model):
    token = models.ForeignKey(Token)
    sequence = models.IntegerField()
    required = models.BooleanField(blank=True, null=True)

    def __unicode__(self):
        return "%s: %s" % (str(self.sequence), self.token) 

class DomainForm(models.Model):
    form = models.ForeignKey(Form)
    sequence = models.IntegerField()

    def __unicode__(self):
        return "%s: %s" % (str(self.sequence), self.form)

class Domain(models.Model):
    name = models.CharField(max_length=160, help_text="Name of form domain")
    code = models.ForeignKey(Token)
    domain_forms = models.ManyToManyField(DomainForm)
        
    def __unicode__(self):
        return self.name
    
class FormEntry(models.Model):
    # blank for now until we have real users and groups.
    # we do have users and groups, but still blank
    reporter = models.ForeignKey(Reporter, blank=True, null=True)
    domain = models.ForeignKey(Domain)
    form = models.ForeignKey(Form)
    date = models.DateTimeField()
    
    def __unicode__(self):
        return "%s %s" % (self.domain.code.abbreviation, self.form.code.abbreviation)
    
    def to_dict(self):
        return dict([
            (str(t.token.abbreviation), t.data)
            for t in self.tokenentry_set.all()
        ])

class TokenEntry(models.Model):
    form_entry = models.ForeignKey(FormEntry)
    token = models.ForeignKey(Token)
    data = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return "%s %r" % (self.token.abbreviation, self.data)

class FormValidator(Validator):
    '''Validator for forms, by passing off validation for each token'''
    def __init__ (self, form):
        self._form = form
        
        form_tokens = FormToken.objects.all().filter(form=self._form)
        self._validators = {}
        for ft in form_tokens:
            validators = TokenExistanceValidator.objects.all().filter(token=ft.token) 
            if validators:
                self._validators[ft.token] = validators
        
    def get_validation_errors(self, form_entry):
        validation_errors = []
        #print self._validators
        for token_value in form_entry.tokenentry_set.all():
            #print "token: %s" % token_value.token
            if self._validators.has_key(token_value.token):
                for validator in self._validators[token_value.token]:
                    errors = validator.get_validation_errors(token_value)
                    #print "got back errors: %s" % errors
                    if errors:
                        validation_errors.append(errors)
        return validation_errors
        

class TokenValidator(models.Model):
    # to integrate with form/token model - these could be looked up and defined generically through the UI
    # due to subclassing not working as ideally as i'd like it's possible we want to scrap this class
    token = models.ForeignKey(Token, unique=True)
    
    def get_validation_errors(self, token):
        pass

    def __unicode__(self):
        return "%s" % self.token

        
class TokenExistanceValidator(TokenValidator):
    '''Validator that can ensure a token exists in some other model.name db column'''
    lookup_type = models.ForeignKey(ContentType, "model", verbose_name='type to check against')
    field_name = models.CharField(max_length = 100)
    
    def __unicode__(self):
        return "%s %s %s" % (self.token, self.lookup_type.name, self.field_name)
    
    def get_validation_errors(self, token_value):
        model_class = ContentType.model_class(self.lookup_type)
        lookup = { str(self.field_name + "__iexact") : token_value.data } 
        try: 
            val = model_class.objects.get(**lookup)
            return None
        except model_class.DoesNotExist: 
            return "%s not in list of %s %ss" % (token_value.data, self.lookup_type.name, self.field_name) 
        
        
class FormAlerter(Alerter):
    '''Alerter for forms, by passing off alerts to a contained list'''
    def __init__ (self, form):
        self._form =form
        self._alerters = RegexAlerter.objects.all().filter(form = self._form)

    def get_alerts(self, msg):
        alerts = []
        for alerter in self._alerters:
            alert = alerter.get_alerts(msg)
            if (alert):
                alerts.append(alert)
        return alerts

class RegexAlerter(models.Model, Alerter):
    '''Alerter that raises an error any time a particular regex matches'''
    form = models.ForeignKey(Form)
    regex = models.CharField(max_length=100)
    response = models.CharField(max_length=160)
        
    def get_alerts(self, msg):
        if re.match(self.regex, msg):
            return self.response
