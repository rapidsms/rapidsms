#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ObjectDoesNotExist 
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from datetime import date


class Validator():
    
    def get_validation_errors(self, content):
        '''Returns any errors with this content'''
        # by default this implementation will do nothing
        pass

class Validatable():
    '''Class to extend to allow validaiton.  The validator property should 
    be overridden with a custom implementation''' 
    
    _validator = Validator()
    
    def _get_validator(self):
        return self._validator
    def _set_validator(self, validator):
        # todo: check the type of this and make sure it's a valid Validator
        self._validator = validator
    validator = property(_get_validator, _set_validator, None, None)
    
    def get_validation_errors(self, form):
        #print "in Validatable, next call will generate errors"
        return self._validator.get_validation_errors(form)

    def __unicode__(self):
        return "%s" % (self.type)


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

class Report(models.Model, Validatable):
    type = models.CharField(max_length=160)
    supply = models.ForeignKey("Supply")

    def __init__ (self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs) 
        self.validator = FormValidator(self)
        
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
        print self._validators
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
        
