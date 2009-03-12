#!/usr/bin/env python
# vim: noet

from django.views.decorators.http import require_POST
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.db import IntegrityError

from models import *
from utils import *

def dashboard(req, id=None):

	# if a pk was passed in the url, then
	# load that; otherwise, attempt to load
	# the currently-active question (or None)
	if id is None: ques = Question.current()
	else: ques = get_object_or_404(Question, pk=id)
	
	# the previous questions are always the same (for
	# now); TODO: show those adjacent to 'ques'
	prev = Question.objects.all()[:12]
	
	# show all of the answers related to this
	# question. these have already been filtered
	# by the backend, but not moderated or parsed
	if ques: entries = ques.entry_set.all()
	else: entries = []

	return render_to_response("dashboard.html", {
		"question": ques,
		"previous": prev,
		"entries": entries,
		"tab": "dashboard"
	})


def add_question(req):
	
	# if we are POSTing, create the object
	# (and children) before redirecting
	if req.method == "POST":
		p = req.POST
		try:
			# extract the date range from the query dict
			start_str = "%4d-%02d-%02d" % (int(p["start-year"]), int(p["start-month"]), int(p["start-day"]))
			end_str   = "%4d-%02d-%02d" % (int(p["end-year"]), int(p["end-month"]), int(p["end-day"]))
			
			# before saving, check that the dates are
			# available (although this should have already been
			# done on the client side by ajax, we must check)
			avail = is_available(None, start_str, end_str)
			if isinstance(avail, HttpResponseServerError):
				return avail
			
			q = object_from_querydict(Question, req.POST)
			q.save()
			
			# for multiple choice questions, also
			# create the linked Answer objects
			if q.type == "M":
				for n in range(1, 5):
					object_from_querydict(
						Answer,
						req.POST,
						{ "question": q },
						("-%s" % n)
					).save()
			
			# redirect to the dashboard
			return HttpResponseRedirect("/")
		
		# something went wrong during object creation.
		# this should have been caught by javascript,
		# so halt with a low-tech error
		except IntegrityError, err:
			return HttpResponseServerError(
				"\n".join(list(e[1] for e in err)),
				content_type="text/plain")
	
	# otherwise, just render the ADD form
	return render_to_response("add-question.html", {
		"tab": "add-question"
	})


from datetime import datetime
from datetime import timedelta

def is_available(req, from_str, to_str):
	delta = timedelta(1)
	fmt = "%Y-%m-%d"

	# parse into date objects
	day = datetime.strptime(from_str, fmt)
	last = datetime.strptime(to_str, fmt)
	
	taken = []
	while(day <= last):
		q = Question.on(day)
		if q is not None:
			taken.append((q, day))
		
		# next day
		day += delta
	
	# if any of the days we just iterated were
	# already taken by an existing question,
	# then compile and return a list of errors
	# to be displayed by ajax (or seen by a low-
	# tech or non-js browser)
	if len(taken):
		errs = ["<li>%s by %s</li>" % (day.strftime(fmt), q) for q, day in taken]
		return HttpResponseServerError(
			"The following dates are already reserved:\n<ul>\n" + "\n".join(errs) + "\n</ul>",
			content_type="text/plain")
	
	# no dates were taken, so this range is fine
	return HttpResponse("OK", content_type="text/plain")


@require_POST
def moderate(req, id, status):
	ent = get_object_or_404(Entry, pk=id)
	
	# update the "moderated" status,
	# which makes this a regular entry
	if (status == "win"):
		ent.moderated = True
		ent.save()
	
	# remove bad entries from the db
	# altogether. we'll still have the
	# Message object to refer to
	elif (status == "fail"):
		ent.delete()
	
	# a really boring response. the HTTP code
	# is all we really need on the client side
	return HttpResponse("OK", content_type="text/plain")


@require_POST
def correction(req, id):

	# update the Entry and Message objects
	ent = get_object_or_404(Entry, pk=id)
	text = req.POST["text"]
	
	# a special string can be passed
	# to drop the entry altogether
	if text == "REJECT":
		ent.message.delete()
		
	else:
		ent.message.text = text
		ent.save()
	
		# run the correction back through the parser,
		# and throw an http500 (mostly to be caught
		# by ajax) if it failed again
		if not parse_message(ent, ent.question):
			return HttpResponseServerError(
				"Entry was still unparseable",
				content_type="text/plain")
	
	# no fail = success!
	return HttpResponse("OK", content_type="text/plain")


def message_log(req):
	return render_to_response("message-log.html", {
		"messages": Message.objects.all().order_by("-pk"),
		"tab": "log"
	})

