#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.views.decorators.http import require_GET
from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import logout as django_logout
from rapidsms.utils import render_to_response

@require_GET
def dashboard(req):
    return render_to_response(req, "dashboard.html")

def login(req, template_name="rapidsms/login.html"):
    '''Login to rapidsms'''
    return django_login(req, **{"template_name" : template_name})

def logout(req, template_name="rapidsms/loggedout.html"):
    '''Logout of rapidsms'''
    return django_logout(req, **{"template_name" : template_name})
