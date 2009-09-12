#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.views.decorators.http import require_GET, require_http_methods
from django.shortcuts import get_object_or_404
from rapidsms.webui.utils import render_to_response
from models import *

@require_GET
def index(req):
    return render_to_response(req,
        "i18n/index.html", {
            "languages": Language.objects.all(),

            # not named "apps", because that clashes with
            # some badly-named auto-populated stuff in r_to_r
            "persistant_apps": [app for app in PersistantApp.objects.all()]
        })
