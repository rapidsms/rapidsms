#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.templatetags.tabs_tags import register_tab
from rapidsms.utils import render_to_response, paginated
from rapidsms.models import Contact
from . import filters


@register_tab
def messaging(req):
    return render_to_response(req,
        "messaging/dashboard.html", {
            "people": paginated(req, Contact.objects.all()),
            "filters": filters.fetch()
        })
