#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.views.decorators.http import require_GET
from django.templatetags.tabs_tags import register_tab
from rapidsms.utils import render_to_response

@require_GET
@register_tab
def dashboard(req):
    return render_to_response(req, "dashboard.html")
