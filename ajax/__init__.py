#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

class Error(Exception):
    pass

class AjaxAppNotRunningError(Error):
    pass

class ConnectionError(Error):
    pass

class RequestError(Error):
    pass
