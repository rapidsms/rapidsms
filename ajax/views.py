#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.http import HttpResponse
from .utils import request


def proxy(req, path):

    # call the router via app.py
    status, content_type, body = request(
        path, req.GET, req.POST,
        req.encoding)

    # set some sensible defaults, in case the request failed
    if status is None: status = 500
    if content_type is None: content_type = "text/plain"
    if body is None: body = "Couldn't reach the router."

    return HttpResponse(body, status=status, content_type=content_type)
