#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

def layout(req):
    """This function is included in TEMPLATE_CONTEXT_PROCESSORS as default
       by RapidSMS, to inject hacks and settings into the template, without
       exposing the entire HttpRequest. That would be... bad."""
    
    # a magic GET parameter can be provided to remove various
    # parts of the webui. this is handy for nesting parts of
    # the webui in iframes
    return {
        "bare": bool(req.GET.get("bare", None))
    }
