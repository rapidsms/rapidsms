#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .forms import MessageForm


@login_required
def messaging(request):
    return render(request, 'messaging/dashboard.html', {
        'form': MessageForm(),
    })


@login_required
@require_POST
def send(request):
    try:
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.send()
            if len(message.connections) == 1:
                return HttpResponse('Your message was sent to 1 recipient.')
            else:
                msg = 'Your message was sent to {0} ' \
                    'recipients.'.format(len(message.connections))
                return HttpResponse(msg)
        else:
            return HttpResponseBadRequest(str(form.errors))
    except:
        return HttpResponse("Unable to send message.", status=500)
