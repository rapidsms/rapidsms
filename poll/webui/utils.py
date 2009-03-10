#!/usr/bin/env python
# vim: noet


def querydict_to_dict(qd):
	return dict((str(k), v) for k, v in qd.iteritems())


from django.db.models.fields import DateField

def object_from_querydict(model, qd, other=None, suffix=""):
	dict = querydict_to_dict(qd)
	obj_dict = {}
	
	# if applicable, merge the 'other' dict,
	# which contains pre-filled values, not
	# from a query dict
	if other is not None:
		for k, v in other.iteritems():
			dict[str(k) + suffix] = v
	
	# iterate the fields in the model, building
	# a dict of matching POSTed values as we go
	for field in model._meta.fields:
		fn = field.name
		fns = fn + suffix
		
		# if an exact match was
		# POSTed, then use that
		if fns in dict:
			obj_dict[fn] = dict[fns]
		
		# date fields can be provided as three
		# separate values, so D/M/Y <select>
		# elements can easily be used
		elif isinstance(field, DateField):
			try:
				obj_dict[fn] = "%4d-%02d-%02d" % (
					int(dict[fns+"-year"]),
					int(dict[fns+"-month"]),
					int(dict[fns+"-day"]))
			
			# choo choooo...
			# all aboard the fail train
			except KeyError:
				pass
	
	# create the instance based upon
	# the fields we just extracted
	return model(**obj_dict)

def extract_date(qd, prefix):
	pass


def parse_message(msg_or_entry, question):
	'''This function takes an incoming message and
	a question and tries to parse the message as
	an answer to the question.  If it succeeds it
	creates a new entry as an answer to the
	question and returns True, otherwise it returns
	False and creates a new unparseable entry if
	there was not already one.'''

	from webui.poll.models import Entry, Message, Respondant
	import re

	# regexes for matching boolean anwsers
	B_REGEX_TRUE  = re.compile(r'^yes$', re.I)
	B_REGEX_FALSE = re.compile(r'^no$', re.I)

	# regexes for matching multiple choice answers
	M_REGEX_1 = re.compile(r'^1$', re.I)
	M_REGEX_2 = re.compile(r'^2$', re.I)
	M_REGEX_3 = re.compile(r'^3$', re.I)
	M_REGEX_4 = re.compile(r'^4$', re.I)
	
	# assume we are parsing a new message,
	# since this will be the vast majority
	correction = False
	message, entry, respondant, text = None, None, None, None

	# get the values we need depending on whether
	# we are creating a new entry or correcting
	# an existing unparseable one
	if isinstance(msg_or_entry, Message):
		message             = msg_or_entry
		respondant, created = Respondant.subscribe(message.phone)
		text                = message.text
	elif isinstance(msg_or_entry, Entry):
		correction = True
		entry      = msg_or_entry
		message    = entry.message
		respondant = entry.respondant
		text       = entry.message.text
	else: return False

	# whew, now we have:
	#
	# correction (whether or not we are correcting
	#             an unparseable entry)
	# entry      (either an Entry to correct or None)
	# msg        (the Message we are dealing with)
	# respondant (the respondant we are dealing with)
	# text       (the text to parse)
	#
	# let's do this!

	# CASE 1 - FREE TEXT
	# if we are logging free text answers,
	# just move the message straight into
	# the entries (unmoderated!)
	if question.type == "F":
		
		# always create free text entries
		# as parseable so this is OK
		Entry.objects.create(
			respondant=respondant,
			question=question,
			message=message,
			is_unparseable=False,
			moderated=False,
			text=text
		)
		return True

	# CASE 2 - BOOLEAN
	# if we are logging boolean answers,
	# then we need to parse them based
	# on yes/no regexes
	if question.type == "B":
		# assume the message is unparseable
		unparseable = True
		
		# if yes matches, make a '1' entry
		if B_REGEX_TRUE.match(text):
			text = '1'
			unparseable = False
	
		# if no matches, make a '0' entry
		elif B_REGEX_FALSE.match(text):
			text = '0'
			unparseable = False
	
	# CASE 3 - MULTIPLE CHOICE
	# if we are logging multiple choice,
	# answers, then we need to parse
	# them based on our mc regexes
	if question.type == "M":
		# assume the message is unparseable
		unparseable = True
		
		# if 1 matches, make the entry
		if M_REGEX_1.match(text):
			text = '1'
			unparseable = False

		# 2 matches...
		elif M_REGEX_2.match(text):
			text = '2'
			unparseable = False

		# 3 matches...
		elif M_REGEX_3.match(text):
			text = '3'
			unparseable = False

		# 4 matches...
		elif M_REGEX_4.match(text):
			text = '4'
			unparseable = False

	# now set the moderated flag as the inverse of 
	# the unparseable one (unparseable entries are
	# by default not moderated)
	moderated = not unparseable

	# at this point we have figured out whether or
	# not the message was parsed successfully so we
	# can either update our existing Entry or make
	# a new one...
	if correction:
	
		# update the entry
		entry.text = text
		entry.is_unparseable = unparseable
		entry.moderated = moderated
		entry.save()
		
	else:
		# make a new entry
		Entry.objects.create(
			respondant=respondant,
			question=question,
			message=message,
			is_unparseable=unparseable,
			moderated=moderated,
			text=text)

	# now return the result of the parse
	if unparseable: return False
	else:           return True
