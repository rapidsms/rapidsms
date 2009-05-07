#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
from rapidsms.webui.utils import render_to_response
from apps.ajax.utils import get

def index(req):
    
    # fetch ALL recipients from the router. this is a
    # very expensive operation. and should be cached
    apps_with_recipients = get("messaging", "recipients")
    
    # what the hell is going on here?
    
    columns = reduce(
        lambda cols, app: cols + filter(
            lambda x: x not in cols,
            app["columns"]),
        apps_with_recipients, [])
    
    recipients = reduce(
        lambda recips, app: recips + map(
            lambda recip: map(
                lambda n: recip[app["columns"].index(columns[n])] if columns[n] in app["columns"] else "-",
                range(0, len(columns))),
            app["recipients"]),
        apps_with_recipients, [])
    
    return render_to_response(req,
        "messaging/index.html",{
            "columns": columns,
            "recipients": recipients
    })
