#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

def dashboard(req):
    return render_to_response("dashboard.html", { },
        context_instance=RequestContext(req))
