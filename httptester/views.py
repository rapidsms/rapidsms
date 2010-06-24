#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from random import randint
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_GET, require_POST
from rapidsms.contrib.ajax.exceptions import RouterNotResponding
from rapidsms.utils import render_to_response
from . import forms
from . import utils


def _redirect(identity):
    url = reverse(message_tester, kwargs={ "identity": identity })
    return HttpResponseRedirect(url)


def generate_identity(req):
    identity = randint(111111, 999999)
    return _redirect(identity)


def bulk_messages(req):
    file = req.FILES['file']
    identity = req.POST['identity']
    for line in file:
        utils.send_test_message(identity=identity, text=line)
    return _redirect(identity)


def message_tester(req, identity):
    if req.method == "POST":
        form = forms.MessageForm(req.POST)
        if form.is_valid():
            cd = form.cleaned_data
            utils.send_test_message(**cd)
            return _redirect(cd["identity"])

    else:
        form = forms.MessageForm({
            "identity": identity })

    # attempt to fetch the message log from the router, but don't expode
    # if it's not available. (the router probably just isn't running.)
    try:
        router_available = True
        message_log = utils.get_message_log()

    except RouterNotResponding:
        router_available = False
        message_log = None

    return render_to_response(
        req, "httptester/index.html", {
            "router_available": router_available,
            "message_log": message_log,
            "message_form": form, })
