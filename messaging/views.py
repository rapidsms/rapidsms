#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.template import RequestContext
from django.shortcuts import render_to_response
from rapidsms.models import Contact
from rapidsms.utils import paginated
from . import filters


def messaging(req):
    return render_to_response(
        "messaging/dashboard.html", {
            "people": paginated(req, Contact.objects.all()),
            "filters": filters.fetch()
        }, context_instance=RequestContext(req)
    )
