#!/usr/bin/env python
# vim: noet

from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ObjectDoesNotExist 
from datetime import date

class Respondant(models.Model):
	phone = models.CharField(max_length=30, blank=True, null=True)
	is_active = models.BooleanField()

	def __unicode__(self):
		return self.phone
	
	@classmethod
	def subscribe(klass, caller, active=True):
		created = False
		
		try:
			# attempt to reactivate an
			# unsubscribed respondant
			r = klass.objects.get(phone=caller)
			r.is_active = active
			r.save()
		
		# no existing respondant, so create
		# a new, pre-activated, respondant
		except ObjectDoesNotExist:
			r = klass.objects.create(phone=caller, is_active=active)
			created = True
		
		# always return the object, with a bool
		# "created" flat like get_or_create
		return (r, created)
	
	@classmethod
	def unsubscribe(klass, caller):
		
		# recycle the "subscribe" function to
		# create and deactivate the respondant
		return klass.subscribe(caller, False)
		

class Message(models.Model):
	phone = models.CharField(max_length=30, blank=True, null=True)
	time = models.DateTimeField(auto_now_add=True)
	text = models.CharField(max_length=160)
	is_outgoing = models.BooleanField()

	def __unicode__(self):
		return self.text

class Question(models.Model):
	QUESTION_TYPES = (
		('F', 'Free text'),
		('B', 'Boolean'),
		('M', 'Multiple choice'),
	)

	start = models.DateField()
	end = models.DateField()
	text = models.CharField(max_length=160)
	type = models.CharField(max_length=1, choices=QUESTION_TYPES)
	sent_to = models.IntegerField(blank=True, null=True)

	def __unicode__(self):
		return self.text

	def is_current(self):
		'''returns True if this is the current question'''
		return (self == Question.current())

	@staticmethod
	def current():
		# delegate to the 'on' method, to find
		# the (single!) question active today
		return Question.on(date.today())
		
	@staticmethod
	def on(day):
		
		# fetch all of the questions with dates spanning 'date'. the
		# app should prevent there being more than one question active
		# on a single day, but since django 1.0 doesn't have model
		# validation, it's entirely possible
		active = Question.objects.filter(
			start__lte=day,
			end__gte=day
		).order_by('-end')
		
		# it's okay if nothing is active today
		# return None to prompt some other view
		if len(active) == 0: return None
		
		# othewise, return the first active question.
		# todo: warn or fix if multiple Qs are active
		else: return active[0]


class Answer(models.Model):
	question = models.ForeignKey(Question)
	text = models.CharField(max_length=30)
	choice = models.CharField(max_length=1)

	def __unicode__(self):
		return "(%s) %s" % (self.choice, self.text)


class Entry(models.Model):
	respondant = models.ForeignKey(Respondant, blank=True, null=True)
	question = models.ForeignKey(Question, blank=True, null=True)
	message = models.ForeignKey(Message, blank=True, null=True)
	time = models.DateTimeField(auto_now_add=True)
	text = models.CharField(max_length=160)
	is_unparseable = models.BooleanField()
	moderated = models.BooleanField()

	def __unicode__(self):
		return self.text
	
	def meta_data(self):
		return "%s - %s %s" % (
			self.respondant.phone,
			self.time.strftime("%a %b %e"),
			self.time.strftime("%I:%M %p"))
	
	def display_text(self):
		# assume that the display text is just the text,
		# since this is what it is for free text entries
		display_text = self.text
		# switch the text for boolean/multiple choice entries
		if self.question.type == "B":
			# TODO proper i18n for this!
			if self.text == "0":   display_text = "No"
			elif self.text == "1": display_text = "Yes"
		elif self.question.type == "M":
			# get the full answer text
			try:
				display_text = Answer.objects.get(
						question=self.question, 
						choice=self.text).text
			except: pass # TODO something here...

		return display_text

	class Meta:
		verbose_name_plural="Entries"
