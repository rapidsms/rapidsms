#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST

from rapidsms.contrib.messaging.forms import MessageForm


def messaging(request):
    return render(request, "messaging/dashboard.html", {
        'form': MessageForm(),
    })


@require_POST
def send(request):
    form = MessageForm(request.POST)
    if form.is_valid():
        try:
            text, recipients = form.send()
        except:
            return HttpResponse("Unable to send messages.", status=500)
        names = ", ".join(str(r) for r in recipients)
        return HttpResponse("'%s' sent to %s" % (text, names))
    return HttpResponseBadRequest(unicode(form.errors))
