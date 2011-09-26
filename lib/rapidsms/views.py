#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.http import require_GET
from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import logout as django_logout
from rapidsms.messages import IncomingMessage
from rapidsms.models import Backend, Connection
from rapidsms.router import get_router

@require_GET
def dashboard(req):
    return render_to_response(
        "dashboard.html",
        context_instance=RequestContext(req))


def login(req, template_name="rapidsms/login.html"):
    return django_login(req, **{"template_name" : template_name})


def logout(req, template_name="rapidsms/loggedout.html"):
    return django_logout(req, **{"template_name" : template_name})


def receive(req, receive_form=None, params=['msisdn', 'text'], backend='default', method='GET'):
    """
    The idea here is to have one view that can handle any HTTP based incoming communication.
    That way you can, at the project level, configure URLs like:

    url(r'^receive/clickatell', receive, {'params':['number','message'],'backend':'clickatell','method':'post'})
    """

    if receive_form is None:
        pass
        # TODO dynamically create a form class with the appropriate parameters
    if method == 'GET' and req.GET:
        form = receive_form(req.GET)
    elif method == 'POST' and req.POST:
        form = receive_form(req.POST)
    if form.is_valid():
        backend, created = Backend.objects.get_or_create(backend)
        conn, created = Connection.objects.get_or_create(identity=receive_form.cleaned_data['msisdn'], \
                                                        backend=backend)
        message = IncomingMessage(conn, receive_form.cleaned_data['text'])
        get_router().incoming(message)
