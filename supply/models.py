#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ObjectDoesNotExist 
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
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
        


class Reporter(models.Model):
        first_name = models.CharField(max_length=100, blank=True, null=True)
        last_name = models.CharField(max_length=100, blank=True, null=True)
        nickname = models.CharField(max_length=100, blank=True, null=True)
        connection = models.CharField(max_length=100, blank=True, null=True)
        location = models.ForeignKey("Location")
        role = models.ForeignKey("Role")

        def __unicode__(self):
                return self.connection.identity
        
class Role(models.Model):
        name = models.CharField(max_length=160)

class Report(models.Model, Validatable, Alertable):
    type = models.CharField(max_length=160)
    supply = models.ForeignKey("Supply")

    def __init__ (self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs) 
        self.validator = FormValidator(self)
        self.alerter = FormAlerter(self)
        
    def __unicode__(self):
        return "%s %s" % (self.supply.code, self.type)

class Token(models.Model):
        name = models.CharField(max_length=160)
        abbreviation = models.CharField(max_length=20)
        regex = models.CharField(max_length=160)
        sequence = models.IntegerField()
        report = models.ForeignKey(Report)

        def __unicode__(self):
            return "%s %s" % (self.report.type, self.abbreviation)

class Supply(models.Model):
        name = models.CharField(max_length=160, help_text="Name of supply")
        code = models.CharField(max_length=20, blank=True, null=True,\
            help_text="Abbreviation")
        
        def __unicode__(self):
                return self.name
    
class LocationType(models.Model):
        name = models.CharField(max_length=160,\
            help_text="Name of location type")
        
        def __unicode__(self):
                return self.name
    

class Location(models.Model):
        name = models.CharField(max_length=160, help_text="Name of location")
        type = models.ForeignKey(LocationType, blank=True, null=True, help_text="Type of location")
        latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True, help_text="The physical latitude of this location")
        longitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True, help_text="The physical longitude of this location")

        def __unicode__(self):
                return self.name
    
class Stock(models.Model):
        location = models.ForeignKey(Location)
        supply = models.ForeignKey(Supply)
        balance = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply at warehouse")
        
        def __unicode__(self):
                return "%s (%s units)" % (self.supply, self.balance)
        
class Shipment(models.Model):
        origin = models.ForeignKey(Location)
        destination = models.ForeignKey(Location, related_name='destination')
        sent = models.DateTimeField()
        received = models.DateTimeField()
        shipment_id = models.PositiveIntegerField(blank=True, null=True)

class Transaction(models.Model):
        supply = models.ForeignKey(Supply)
        amount_sent  = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply being shipped")
        amount_received = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply being shipped")
        shipment = models.ForeignKey(Shipment)  

class Notification(models.Model):
    reporter = models.ForeignKey(Reporter)
    notice = models.CharField(max_length=160)
    received = models.DateTimeField(auto_now_add=True)
    resolved = models.DateTimeField(blank=True, null=True)
    # do we want to save a resolver?


class FormValidator(Validator):
    '''Validator for forms, by passing off validation for each token'''
    def __init__ (self, form):
        self._form = form
        
        tokens = Token.objects.all().filter(report=self._form)
        self._validators = {}
        for token in tokens:
            validators = TokenExistanceValidator.objects.all().filter(token=token) 
            if validators:
                self._validators[token.abbreviation] = validators
        
    def get_validation_errors(self, form):
        validation_errors = []
        #print self._validators
        for token, validators in self._validators.items():
            print "token: %s" % token
            if form.has_key(token):
                for validator in validators:
                    errors = validator.get_validation_errors(form[token])
                    print "got back errors: %s" % errors
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
    lookup_type = models.ForeignKey(ContentType, verbose_name='type to check against')
    field_name = models.CharField(max_length = 100)
    
    def __unicode__(self):
        return "%s %s %s" % (self.token, self.lookup_type.name, self.field_name)
    
    def get_validation_errors(self, token):
        model_class = ContentType.model_class(self.lookup_type)
        vals = model_class.objects.values_list(self.field_name, flat=True)
        print "validating %s with %s" % (token, str(self))
        if token not in vals:
            return "%s not in list of %s %s" % (token, self.lookup_type.name, self.field_name) 
        return None
        
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
    form = models.ForeignKey(Report)
    regex = models.CharField(max_length=100)
    response = models.CharField(max_length=160)
        
    def get_alerts(self, msg):
        if re.match(self.regex, msg):
            return self.response
