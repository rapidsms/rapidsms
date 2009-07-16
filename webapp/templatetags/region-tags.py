#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os
from rapidsms.webui import settings

from django import template
register = template.Library()


@register.inclusion_tag("webapp/partials/region.html", takes_context=True)
def region(context, name):
    def __path(app):
        return "%s/templates/regions/%s.html" %\
            (app["path"], name)

    return {
        "name": name,
        "request": context["request"],
        "includes": [
            __path(app)
             for app in settings.RAPIDSMS_APPS.values()
             if os.path.exists(__path(app))
        ]}
