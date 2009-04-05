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
	reporter = models.ForeignKey(Reporter)
	time = models.DateTimeField(auto_now_add=True)
	text = models.CharField(max_length=160)

	def __unicode__(self):
		return self.text

class Supply(models.Model):
	name = models.CharField(max_length=160, help_text="Name of supply")
	code = models.CharField(max_length=20, blank=True, null=True, help_text="Abbreviatiation")
	
class LocationType(models.Model):
	name = models.CharField(max_length=160, help_text="Name of location type")

class Location(models.Model):
	name = models.CharField(max_length=160, help_text="Name of location")
	type = models.ForeignKey(LocationType, blank=True, null=True, help_text="Type of location")
	latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True, help_text="The physical latitude of this location")
	longitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True, help_text="The physical longitude of this location")
	stock = models.ManyToManyField("Stock", help_text="Supplies at inventory location")

class Stock(models.Model):
	supply = models.ForeignKey(Supply)
	balance = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply at warehouse")

class Shipment(models.Model):
	#origin = models.ForeignKey(Location)
	#destination = models.ForeignKey(Location)
	sent = models.DateTimeField()
	received = models.DateTimeField()
	shipment_id = models.PositiveIntegerField(blank=True, null=True)

class Transaction(models.Model):
	supply = models.ForeignKey(Supply)
	amount = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply being shipped")
	shipment = models.ForeignKey(Shipment)	

class Notification(models.Model):
	reporter = models.ForeignKey(Reporter)
	notice = models.CharField(max_length=160)
	received = models.DateTimeField(auto_now_add=True)
	resolved = models.BooleanField()
