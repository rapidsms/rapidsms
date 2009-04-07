#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from apps.httptester.models import Message
from apps.httptester.forms import MessageForm
import datetime
import urllib2

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
