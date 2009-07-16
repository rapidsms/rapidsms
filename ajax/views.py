#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import urllib, urllib2
from django.http import HttpResponse
from rapidsms.webui import settings

def proxy(req, path):
    
    # build the url to the http server running
    # in ajax.app.App via conf hackery
    conf = settings.RAPIDSMS_APPS["ajax"]
    url = "http://%s:%d/%s?%s" % (
        conf["host"], conf["port"],
        path, req.GET.urlencode())
    
    try:
        # attempt to fetch the requested url from the
        # backend, and proxy the response back as-sis
        args = [url]
        code = 200
        
        # if this was a POST, included exactly
        # the same form data in the subrequest
        if req.method == "POST":
            args.append(req.POST.urlencode())
        
        out = urllib2.urlopen(*args)
    
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
