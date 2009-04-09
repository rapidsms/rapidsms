#!/usr/bin/env python
# vim: noet

from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ObjectDoesNotExist 
from datetime import date

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

class Report(models.Model):
	type = models.CharField(max_length=160)
	supply = models.ForeignKey("Supply")

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
