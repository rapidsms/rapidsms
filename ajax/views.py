#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import urllib
import urllib2
from django.http import HttpResponse
from django.conf import settings


def proxy(req, path):

    # todo: make these more configurable
    host = getattr(settings, "AJAX_PROXY_HOST", "localhost")
    port = getattr(settings, "AJAX_PROXY_PORT", 8001)

    # build the url to the http server running in ajax.app.App. there
    # are no encoding worries here, since GET only supports ASCII.
    # http://www.w3.org/TR/REC-html40/interact/forms.html#idx-POST-1
    url = "http://%s:%d/%s?%s" % (host, port, path, req.GET.urlencode())

    try:
        data = None
        headers = {}

        # send along POST data verbatim
        if req.method == "POST":
            data = req.POST.urlencode()

            # it doesn't matter if req.POST contains unicode, because
            # req.urlencode will smartly (via djano's smart_str) convert
            # it all back to ASCII using the same encoding that it was
            #  submitted with. but we must pass along the content-type
            # (containing the charset) to ensure that it's decoded
            # correctly the next time around.
            headers["content-type"] = req.META["CONTENT_TYPE"]

        # call the router (app.py) via HTTP
        sub_request = urllib2.Request(url, data, headers)
        sub_response = urllib2.urlopen(sub_request)
        out = sub_response.read()
        code = 200

    # the request was successful, but the server returned an error. as
    # above, send it as-is, so we receive as much debug info as possible
    except urllib2.HTTPError, err:
        out = err.read()
        code = err.code

    # the router couldn't be reached, but we have no idea why. return a
    # useless error
    except urllib2.URLError, err:
        out = "Couldn't reach the router."
        code = 500

    # if the subresponse specified a content type (which it ALWAYS
    # should), pass it along. else, default to plain text
    try:    ct = out.info()["content-type"]
    except: ct = "text/plain"

    return HttpResponse(out, status=code, content_type=ct)
