#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
from rapidsms.webui.utils import render_to_response
from training.models import *

def index(req):
    tmpls = Template.objects.values_list("key", "text")
    tmpl_map = dict([(int(k), t) for k, t in tmpls])
    
    all_tmpls = [
        { "key": n, "text": tmpl_map.get(n, "") }
        for n in range(1,10)]
    
    return render_to_response(req,
        "training/index.html",
        { "templates": all_tmpls })
