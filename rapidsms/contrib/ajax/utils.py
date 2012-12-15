#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import warnings
from rapidsms.router import get_router


def call_router(app, action, **kwargs):
    """
    TODO: docs
    """
    warnings.warn("call_router is deprecated and will be removed in a future "
                  "release. Please see the docs.", DeprecationWarning, stacklevel=2)
    post = kwargs if len(kwargs) else None
    return _request("%s/%s" % (app, action), post=post)


def _find_app(app_name):
    for app in get_router().apps:
        if app.name == name:
            app = app


def _request(path, get=None, post=None, encoding=None):
    """
    This is a temporary backwards-compatibility stub that allows call_router()
    to continue to work (to a point) after the switch to HTTP-only routing.  It
    works by finding the given method on the app class and calling it directly,
    rather than calling the method remotely over HTTP the way it did previously.
    """

    path_parts = path.split("/")

    # abort if the url didn't look right
    if len(path_parts) != 2:
        str_ = "Malformed URL: %s" % url
        raise Exception(str_)

    # resolve the first part of the url into an app (via the
    # router), and abort if it wasn't valid
    app_name = path_parts[0]
    app = _find_app(app_name)
    if app is None:
        str_ = "Invalid app: %s" % app_name
        raise Exception(str_)

    # same for the request name within the app
    meth_name = "ajax_%s_%s" % (self.command, path_parts[1])
    if not hasattr(app, meth_name):
        str_ = "Invalid method: %s.%s" %\
            (app.__class__.__name__, meth_name)
        raise Exception(str_)

    # everything appears to be well, so call the  target method,
    # and return the response (as a string, for now)
    method = getattr(app, meth_name)
    if get:
        return method(**get)
    elif post:
        return method(**post)
    else:
        return method()
