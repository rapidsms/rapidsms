#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.core.paginator import Paginator
from rapidsms.webui.utils import render_to_response
from apps.reporters.models import *


def index(req):
    all_reporters = Reporter.objects.all()
    paginator = Paginator(all_reporters, 20)

    try:
        page = int(req.GET.get("p", "1"))
        
    except ValueError:
        page = 1
    
    
    try:
        reporters = paginator.page(page)
        
    except (EmptyPage, InvalidPage):
        reporters = paginator.page(paginator.num_pages)
    
    
    return render_to_response(req,
        "messaging/index.html", {
        "reporters": reporters
    })
