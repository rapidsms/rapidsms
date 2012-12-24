#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from random import randint

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from . import forms
from . import storage


def generate_identity(request, backend_name):
    identity = randint(111111, 999999)
    return HttpResponseRedirect(reverse(message_tester,
                                        args=[backend_name, identity]))


def message_tester(request, backend_name, identity):
    if request.method == "POST":
        form = forms.MessageForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            identity = cd["identity"]
            if "bulk" in request.FILES:
                for line in request.FILES["bulk"]:
                    storage.store_and_queue(identity, line)
            # no bulk file was submitted, so use the "single message"
            # field. this may be empty, which is fine, since contactcs
            # can (and will) submit empty sms, too.
            else:
                storage.store_and_queue(backend_name, identity, cd["text"])
            url = reverse(message_tester, args=[backend_name, identity])
            return HttpResponseRedirect(url)

    else:
        form = forms.MessageForm({"identity": identity})
    context = {
        "router_available": True,
        "message_log": storage.get_messages(),
        "message_form": form
    }
    return render_to_response("httptester/index.html", context,
                              context_instance=RequestContext(request))
