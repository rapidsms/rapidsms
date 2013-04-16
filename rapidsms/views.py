#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_GET


@login_required
@require_GET
def dashboard(req):
    return render_to_response(
        "dashboard.html",
        context_instance=RequestContext(req))


def login(req, template_name="rapidsms/login.html"):
    return django_login(req, **{"template_name": template_name})


def logout(req, template_name="rapidsms/loggedout.html"):
    return django_logout(req, **{"template_name": template_name})
