#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseBadRequest

from rapidsms.models import Contact
from rapidsms.utils.pagination import paginated
from rapidsms.contrib.messaging.forms import MessageForm


def messaging(request):
    context = {
        "people": paginated(request, Contact.objects.all()),
    }
    return render(request, "messaging/dashboard.html", context)


@require_POST
def send(request):
    form = MessageForm(request.POST)
    if form.is_valid():
        recipients = form.send()
        text = form.cleaned_data['text']
        names = ", ".join(str(r) for r in recipients)
        return HttpResponse("'%s' sent to %s" % (text, names))
    return HttpResponseBadRequest(unicode(form.errors))
