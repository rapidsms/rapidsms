#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import urllib, urllib2
from django.http import HttpResponse
from rapidsms.webui import settings

def proxy(req, path):
    
    # build the url to the http server running in apps.ajax.app.App via
    # conf hackery no encoding worries here, since GET only supports ASCII.
    # see: http://www.w3.org/TR/REC-html40/interact/forms.html#idx-POST-1
    conf = settings.RAPIDSMS_APPS["ajax"]
    url = "http://%s:%d/%s?%s" % (
        conf["host"], conf["port"],
        path, req.GET.urlencode())
    
    try:
        data = None
        headers = {}
        
        # if this was a POST, included exactly
        # the same form data in the subrequest
        if req.method == "POST":
            data = req.POST.urlencode()
            
            # it doesn't matter if req.POST contains unicode, because .urlencode
            # will smartly (via djano's smart_str) convert it all back to ASCII
            # using the same encoding that it was submitted with, but we must
            # pass along the content-type (containing the charset) to ensure
            # that it's decoded (again) correctly
            headers["content-type"] = req.META["CONTENT_TYPE"]

        # attempt to fetch the requested url from the
        # backend, and proxy the response back as-sis
        sub_request = urllib2.Request(url, data, headers)
        sub_response = urllib2.urlopen(sub_request)
        
        # if no exceptions were raised by urlopen,
        # we can assume the subrequest succeeded
        out = sub_response.read()
        code = 200
    
    # the request was successful, but the server
    # returned an error. as above, proxy it as-is,
    # so we can receive as much debug info as possible
    except urllib2.HTTPError, err:
        out = err.read()
        code = err.code
    
    # the server couldn't be reached. we have no idea
    # why it's down, so just return a useless error
    except urllib2.URLError, err:
        out = "Couldn't reach the backend."
        code = 500
    
    # attempt to fetch the content type of the
    # response we received, or default to text
    try:    ct = out.info()["content-type"]
    except: ct = "text/plain"
    
    # whatever happend during the subrequest, we
    # must return a response to *this* request
    return HttpResponse(out, status=code, content_type=ct)
