#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
from rapidsms.webui.utils import render_to_response
from django.views.decorators.cache import cache_page

from django.contrib.auth.decorators import login_required

def check_availability(req):
    return HttpResponse("OK")

#TODO cache in the template, so logged-in username is not cached
@cache_page(60 * 15)
def dashboard(req):
	return render_to_response(req, "dashboard.html")
