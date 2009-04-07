#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from apps.httptester.models import Message
from apps.httptester.forms import MessageForm
from django.core.urlresolvers import reverse
import datetime
import urllib2
import random

def index(req, form_class=MessageForm):
    form_instance = form_class()
    template_name="http/demo.html"
    if req.method == 'POST':
       form_instance = form_class(req.POST)
       if form_instance.is_valid():
           msg = form_instance.save(commit=False)
           msg.date = datetime.datetime.now()
           msg.save();
           url = "http://localhost:8080/%s/%s" % (msg.phone_number, urllib2.quote(msg.body))
           urllib2.urlopen(url)
           #return render_to_response('shared/thanks.html')
       else:
           print "something bad happened"
    return render_to_response(template_name, {
        "form": form_instance,
        #"mootools_src": "/static/http/scripts/mootools-yui-compressed.js"
    }, context_instance=RequestContext(req))


	#return render_to_response("http/index.html",
	#{ },
	#    context_instance=RequestContext(req))

def index_basic(req):
    
    template_name="http/setphone.html"
    if req.method == 'POST':
        phone_number = '' 
        if req.POST.has_key("phone_number"):
            phone_number = req.POST["phone_number"]
        if (len(phone_number) == 0):
            phone_number = random.randint(100000, 999999) 
        return HttpResponseRedirect("/httpbasic/%s" % (phone_number))
        #return basic_ui(req, phone_number, True)
    return render_to_response(template_name, {}, context_instance=RequestContext(req))

   
def basic_ui(req, number, skip_post=False, form_class=MessageForm):
    form_instance = form_class()
    template_name="http/index.html"
    if req.method == 'POST' and req.POST.has_key("phone_number"):
        number = req.POST["phone_number"]
    msgs = Message.objects.all().filter(phone_number=number)
    if not skip_post and req.method == 'POST':
       form_instance = form_class(req.POST)
       if form_instance.is_valid():
           msg = form_instance.save(commit=False)
           msg.phone_number = number
           msg.date = datetime.datetime.now()
           msg.save();
           url = "http://localhost:8080/%s/%s" % (msg.phone_number, urllib2.quote(msg.body))
           urllib2.urlopen(url)
           #return render_to_response('shared/thanks.html')
           return basic_ui(req, msg.phone_number, True)
       else: 
           print "something bad happened"
    return render_to_response(template_name, {
        "form": form_instance,
        "msgs": msgs,
        "number": number
        #"mootools_src": "/static/http/scripts/mootools-yui-compressed.js"
    }, context_instance=RequestContext(req))


	#return render_to_response("http/index.html",
	#{ },
	#    context_instance=RequestContext(req))
