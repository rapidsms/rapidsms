#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from random import randint
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_GET, require_POST
from django.templatetags.tabs_tags import register_tab
from rapidsms.contrib.ajax.utils import call_app
from rapidsms.utils import render_to_response
from . import forms


def _redirect(identity):
    url = reverse(message_tester, kwargs={ "identity": identity })
    return HttpResponseRedirect(url)


@register_tab(caption="Message Tester")
def generate_identity(req):
    identity = randint(111111, 999999)
    return _redirect(identity)


def message_tester(req, identity):
    if req.method == "POST":
        form = forms.MessageForm(req.POST)
        if form.is_valid():
            call_app("httptester", "send", **form.cleaned_data)
            return _redirect(form.cleaned_data["identity"])

    else:
        form = forms.MessageForm({
            "identity": identity })

    log = call_app("httptester", "log")

    return render_to_response(
        req, "httptester/index.html", {
            "message_form": form,
            "message_log": log })
