#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from .render_to_response import render_to_response

def web_message(req, msg, link=None):
    return render_to_response(req,
        "message.html", {
            "message": msg,
            "link": link
    })


