#!/usr/bin/env python
# vim: noet

from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.db import IntegrityError
from django.template import RequestContext

from poll.models import *
from poll.utils import *

@require_GET
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

	return render_to_response("poll/dashboard.html", {
		"question": ques,
		"previous": prev,
		"entries": entries,
		"tab": "dashboard"
	},
	   context_instance=RequestContext(req))


from django.utils import simplejson

@require_GET
def question_json(req, id):
	q = get_object_or_404(Question, pk=id)
	return HttpResponse(
		simplejson.dumps(q.results()),
		mimetype="text/plain")

@require_GET
def entries_json(req, id):
	q = get_object_or_404(Question, pk=id)
	entries = q.entry_set.filter(is_unparseable=False)
	
	# return a text/timestamp array 
	return HttpResponse(
		simplejson.dumps([
			(entry.text, entry.time.isoformat())
			for entry in entries
		]),
		mimetype="text/plain")

@require_GET
def manage_questions(req, id=None):
	
	# no argument = add a question
	# and list existing questions
	if id is None:
		ques = None
	
	# argument = edit an existing
	# question (although COMPLEX
	# LOGIC will apply here)
	else:
		ques = get_object_or_404(Question, pk=id)
		answers = ques.answers()
		# this is really dumb. django templates can't
		# deal with arrays, so we're forced to move
		# the answers into Q attributes, for now
		for n in range(0, len(answers)):
			setattr(ques, ("answer_%d" % (n+1)), answers[n])
	
	# otherwise, just render the ADD form
	return render_to_response("poll/questions.html", {
		"questions": Question.objects.all().order_by("start"),
		"question": ques,
		"tab": "questions"
	},
	   context_instance=RequestContext(req))


def extract_dates(qd):
	"""Extract a date range from a query dict, return as a (start,end) tuple of strings"""
	start = end = None
	
	# attempt to extract "start", or
	# fall back to the None
	try:
		start = "%4d-%02d-%02d" % (
			int(qd["start-year"]),
			int(qd["start-month"]),
			int(qd["start-day"]))
	except: pass
	
	# as above, for END
	try:
		end = "%4d-%02d-%02d" % (
			int(qd["end-year"]),
			int(qd["end-month"]),
			int(qd["end-day"]))
	except: pass
	
	return (start, end)

@require_POST
def add_question(req):
 	p = req.POST
 	
 	try:
 		
 		# before saving, check that the dates are
 		# available (although this should have already been
 		# done on the client side by ajax, we must check)
 		avail = is_available(None, *extract_dates(p))
 		if isinstance(avail, HttpResponseServerError):
 			return avail
 		
 		q = insert_via_querydict(Question, p)
 		q.save()
 		
 		# for multiple choice questions, also
 		# create the linked Answer objects
 		if q.type == "M":
 			for n in range(1, 5):
 				insert_via_querydict(
 					Answer,
 					req.POST,
 					{ "question": q },
 					("-%s" % n)
 				).save()
 		
		# TODO: proper ajax response
		return HttpResponse("Question %d added" % (q.pk),
			content_type="text/plain")
 	
 	# something went wrong during object creation.
 	# this should have been caught by javascript,
 	# so halt with a low-tech error
 	except IntegrityError, err:
 		return HttpResponseServerError(
 			"\n".join(list(e[1] for e in err)),
 			content_type="text/plain")
 
 
@require_POST
def edit_question(req, id):
 	ques = get_object_or_404(Question, pk=id)
 	p = req.POST
 	
 	try:
 		
		# check availability of new dates, if they were provided
		start, end = extract_dates(p) # not inline, for python 2.5
		avail = is_available(None, start, end, ignore=ques)
 		if isinstance(avail, HttpResponseServerError):
 			return avail
 		
 		# save the new fields
 		# not all key/values make sense to edit (such as
 		# changing the dates on a past question), but we'll
 		# check that on the client side, for the time being
 		# TODO: proper sanity checks here
 		q = update_via_querydict(ques, p)
 		q.save()
 		
 		# redirect to the dashboard
 		return HttpResponseRedirect("/poll/")
 		
 	# something went wrong, so blow up
 	# (which should be caught by ajax)
 	except IntegrityError, err:
 		return HttpResponseServerError(
 			"\n".join(list(e[1] for e in err)),
 			content_type="text/plain")

from datetime import datetime
from datetime import timedelta

def is_available(req, from_str, to_str, ignore=None):
	delta = timedelta(1)
	fmt = "%Y-%m-%d"
	out_fmt = "%d %B %Y"

	# parse into date objects
	day = datetime.strptime(from_str, fmt)
	last = datetime.strptime(to_str, fmt)
	
	taken = []
	while(day <= last):
		q = Question.on(day)
		if q is not None:
			# if we are not ignoring any questions,
			# or Q is NOT the one we're ignoring,
			# then add it to the list
			if (ignore is None) or (ignore!=q):
				taken.append((q, day))
		
		# next day
		day += delta
	
	# if any of the days we just iterated were
	# already taken by an existing question,
	# then compile and return a list of errors
	# to be displayed by ajax (or seen by a low-
	# tech or non-js browser)
	if len(taken):
		errs = ["<li><span>%s</span> by <em><a href=\"/question/%d\">%s</a></em></li>" % (day.strftime(out_fmt), q.pk, q) for q, day in taken]
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
	return render_to_response("poll/message-log.html", {
		"messages": Message.objects.all().order_by("-pk"),
		"tab": "log"
	},
	   context_instance=RequestContext(req))

