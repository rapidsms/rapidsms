#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


class AjaxError(Exception):
    pass


class RouterNotResponding(AjaxError):
    """
    The router did not respond. It's probably not running, or the AJAX
    app isn't installed.
    """


class MalformedRouterResponse(AjaxError):
    """
    The router responded, but it could not be understood.
    """


class RouterError(AjaxError):
    """
    The router responded with an HTTP 500 error, because an exception
    was raised while processing the request.
    """

    def __init__(self, code, content_type, response):
        self.code = code
        self.content_type = content_type
        self.response = response

    def __unicode__(self):
        return self.response
