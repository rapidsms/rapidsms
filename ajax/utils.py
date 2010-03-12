#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import urllib
import urllib2
from copy import copy
from django.conf import settings
from django.utils.simplejson import JSONDecoder


def call_app(app, action, **kwargs):
    """
    TODO: docs
    """

    post = kwargs if len(kwargs) else None
    (status, content_type, body) = request(
        "%s/%s" % (app, action),
        post=post)

    # if the response was encoded json, decode it before returning
    if content_type == "application/json":
        return JSONDecoder().decode(body)

    # requests failing is an exceptional condition, so explode. this
    # makes debuggery a lot simpler, in development mode
    if status != 200:
        raise ValueError(body)

    # explode if the response was something unknown, to avoid spurting
    # binary data over unsuspecting callers
    if content_type == "text/plain":
        return body

    # i have no idea what's going on
    raise ValueError(
        "The call_app helper can only return decoded JSON or plain" +\
        "text responses. The content_type was: %s" % content_type)


def request(path, get=None, post=None, encoding=None):
    """
    Send an HTTP request to the RapidSMS router, via the AJAX app (which
    must be running for this to work), and return a tuple containing the
    returned HTTP status, content-type, and body.
    """

    # todo: make these more configurable
    host = getattr(settings, "AJAX_PROXY_HOST", "localhost")
    port = getattr(settings, "AJAX_PROXY_PORT", 8001)

    # build the url to the http server running in the app. encoding
    # doesn't apply here, since the query string only supports ASCII:
    # http://www.w3.org/TR/REC-html40/interact/forms.html#idx-POST-1
    query = "?%s" % urllib.urlencode(get) if (get is not None) else ""
    url = "http://%s:%d/%s%s" % (host, port, path, query)

    # if *post* quacks like a QuerySet, it can urlencode itself, taking
    # its own character encoding into account. which is nice.
    if hasattr(post, "urlencode"):
        encoding = post.encoding()
        data = post.urlencode()

    # ...but if it's just a dict, we have no idea what we're encoding,
    # so let's pretend that it's the django default
    else:
        encoding = settings.DEFAULT_CHARSET
        data = urllib.urlencode(post)\
            if post is not None else None

    # build the content-type header, including the character set
    # that we just encoded the POST data into
    headers = {
        "content-type": "%s; charset=%s" % (
            "application/x-www-form-urlencoded",
            encoding) }

    try:

        # do the subrequest; this might raise
        req = urllib2.Request(url, data, headers)
        res = urllib2.urlopen(req)

        # it worked!
        content_type = res.info()["content-type"]
        return (res.code, content_type, res.read())

    # the request was successful, but the server returned an error. as
    # above, send it as-is, so we receive as much debug info as possible
    except urllib2.HTTPError, err:
        content_type = err.info()["content-type"]
        return (err.code, content_type, err.read())

    # the router couldn't be reached, but we have no idea why. return a
    # useless error
    except urllib2.URLError, err:
        return (None, None, None)
