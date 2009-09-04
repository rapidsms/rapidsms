# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from rapidsms.webui.utils import render_to_response
from django.core.urlresolvers import reverse
from rapidsms.webui import settings
import datetime
import urllib2
import random

def index(req):
    template_name="http/ajaxified.html"
    return render_to_response(req, template_name, {
    })

def proxy(req, number, message):
    # build the url to the http server running
    # in ajax.app.App via conf hackery
    conf = settings.RAPIDSMS_APPS["httptester"]
    url = "http://%s:%s/%s/%s" % (
        conf["host"], 
        conf["port"],
        urllib2.quote(number), 
        urllib2.quote(message))
    
    f = urllib2.urlopen(url)
    return HttpResponse(f.read())
