#!/usr/buppn/env python
# vim: ai ts=4 sts=4 et sw=4

from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ObjectDoesNotExist 
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from apps.form.models import Domain
from datetime import date
import re

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
    code = models.CharField(max_length=20, blank=True, null=True,\
        help_text="Abbreviation")

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
    domain = models.ForeignKey(Domain)
    balance = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply at warehouse")
        
    def __unicode__(self):
        return "%s (%s units)" % (self.domain, self.balance)
        
class Shipment(models.Model):
    origin = models.ForeignKey(Location)
    destination = models.ForeignKey(Location, related_name='destination')
    sent = models.DateTimeField()
    received = models.DateTimeField()
    shipment_id = models.PositiveIntegerField(blank=True, null=True, help_text="Waybill number")

class Transaction(models.Model):
    domain = models.ForeignKey(Domain)
    amount_sent  = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply being shipped")
    amount_received = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply being shipped")
    shipment = models.ForeignKey(Shipment)  

class Notification(models.Model):
    reporter = models.ForeignKey(Reporter)
    notice = models.CharField(max_length=160)
    received = models.DateTimeField(auto_now_add=True)
    resolved = models.DateTimeField(blank=True, null=True)
    # do we want to save a resolver?

