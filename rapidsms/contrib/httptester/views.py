#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from random import randint

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from rapidsms.utils.pagination import paginated

from . import forms
from . import storage


def generate_identity(request, backend_name='message_tester'):
    """Simple view to generate a random identity.

    Just generates a random phone number and redirects to the
    message_tester view.

    :param request: HTTP request
    :param backend_name: Name of a RapidSMS backend, default is 'httptester'
    :return: An HTTPResponse
    """
    return redirect("httptester", backend_name, randint(111111, 999999))


def message_tester(request, identity, backend_name="httptester"):
    """The main Message Tester view.

    GET: will display the form, with the default phone number filled
    in from `identity`.

    POST: will process the form and handle it. In this case the identity
    passed to the view is ignored; the identity in the form is used to
    send any messages.

    :param request: HTTP request
    :param identity: Phone number the message will be sent from
    :param backend_name:  Name of a RapidSMS backend, default is 'httptester'
    :return: An HTTPResponse
    """
    if request.method == "POST":
        form = forms.MessageForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            identity = cd["identity"]
            if cd['clear_all']:
                storage.clear_all_messages()
            elif cd['clear']:
                storage.clear_messages(identity)
            else:
                if "bulk" in request.FILES:
                    for line in request.FILES["bulk"]:
                        line = line.rstrip("\n")
                        storage.store_and_queue(backend_name, identity, line)
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
        "message_log": paginated(request, storage.get_messages(),
                                 default_page=-1),
        "message_form": form
    }
    return render(request, "httptester/index.html", context)
