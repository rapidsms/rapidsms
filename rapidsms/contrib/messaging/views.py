#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .forms import MessageForm


def messaging(request):
    return render(request, 'messaging/dashboard.html', {
        'form': MessageForm(),
    })


@require_POST
def send(request):
    try:
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.send()
            if len(message.connections) == 1:
                return HttpResponse('Your message was sent to 1 recipient.')
            else:
                return HttpResponse('Your message was sent to {0} '
                        'recipients.'.format(len(message.connections)))
        else:
            return HttpResponseBadRequest(unicode(form.errors))
    except:
        return HttpResponse("Unable to send message.", status=500)
