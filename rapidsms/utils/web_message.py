#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.shortcuts import render_to_response
from django.template import RequestContext


def web_message(req, msg, link=None):
    return render_to_response(
        "message.html",
        {"message": msg, "link": link},
        context_instance=RequestContext(req),
    )
