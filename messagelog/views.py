#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.templatetags.tabs_tags import register_tab
from rapidsms.utils import render_to_response
from .tables import MessagelogTable


@register_tab
def message_log(req):
    return render_to_response(req,
        "logger/index.html", {
            "table": MessagelogTable(req)
        })
