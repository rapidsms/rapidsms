#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

def coupons_daily(req, locid=0):
    return render_to_response("nigeria/coupons_daily.html", context_instance=RequestContext(req))

def coupons_weekly(req, locid):
    return render_to_response("nigeria/coupons_weekly.html", context_instance=RequestContext(req))
