#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from rapidsms.utils.pagination import paginated
from rapidsms.models import Contact
from . import filters
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import json
from rapidsms.contrib.messaging.utils import send_message


def messaging(req):
    return render_to_response(
        "messaging/dashboard.html", {
            "people": paginated(req, Contact.objects.all()),
            "filters": filters.fetch()
        }, context_instance=RequestContext(req)
    )

@require_POST
def send(req):
    text = req.POST["text"]
    data = json.loads(req.POST["recipients"])
    sent_to = []
    for item in data:
        contact = get_object_or_404(Contact, pk=item)
        send_message(contact.default_connection, text)
        sent_to.append(contact)
    return HttpResponse("'%s' sent to %s" % (text, ", ".join(str(c) for c in sent_to)))
                    
