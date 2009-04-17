#!/usr/buppn/env python
# vim: ai ts=4 sts=4 et sw=4

from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ObjectDoesNotExist 
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from apps.form.models import Domain
from apps.reporters.models import Location, Reporter
from datetime import date
import re

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
    amount_sent  = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply shipped from origin")
    amount_received = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply received by destination")
    shipment = models.ForeignKey(Shipment)  
    issue = models.ForeignKey('PartialTransaction')
    receipt = models.ForeignKey('PartialTransaction', related_name='receipt')

class PartialTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('I', 'Issue'),
        ('R', 'Receipt'),
    )
    STATUS_TYPES = (
        ('P', 'Pending'),
        ('C', 'Confirmed'),
        ('A', 'Amended'),
    )
    
    reporter = models.ForeignKey(Reporter)
    domain = models.ForeignKey(Domain)
    origin = models.ForeignKey(Location)
    destination = models.ForeignKey(Location, related_name='pending destination')
    shipment_id = models.PositiveIntegerField(blank=True, null=True, help_text="Waybill number")
    amount = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply shipped")
    stock = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of stock present at location.")
    date = models.DateTimeField()
    # this could be a boolean, but is more readable this way
    type = models.CharField(max_length=1, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=1, choices=STATUS_TYPES)
    
    def __unicode__(self):
        return "%s reported %s of %s %s from %s to %s. (waybill: %s)" %(self.reporter, 
                                                                        self.type, 
                                                                        self.amount, 
                                                                        self.domain, 
                                                                        self.origin, 
                                                                        self.destination, 
                                                                        self.shipment_id) 
            
    
class Notification(models.Model):
    reporter = models.ForeignKey(Reporter)
    notice = models.CharField(max_length=160)
    received = models.DateTimeField(auto_now_add=True)
    resolved = models.DateTimeField(blank=True, null=True)
    # do we want to save a resolver?

