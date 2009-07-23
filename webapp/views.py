#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
from rapidsms.webui.utils import render_to_response
from django.views.decorators.cache import cache_page
from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import logout as django_logout
from django.contrib.auth.decorators import login_required

from rapidsms.webui import settings

def check_availability(req):
    return HttpResponse("OK")

def dashboard(req):
	return render_to_response(req, "dashboard.html")

def login(req, template_name="webapp/login.html"):
    '''Login to rapidsms'''
    # this view, and the one below, is overridden because 
    # we need to set the base template to use somewhere  
    # somewhere that the login page can access it.
    req.base_template = settings.BASE_TEMPLATE 
    return django_login(req, **{"template_name" : template_name})

def logout(req, template_name="webapp/loggedout.html"):
    '''Logout of rapidsms'''
    req.base_template = settings.BASE_TEMPLATE 
    return django_logout(req, **{"template_name" : template_name})