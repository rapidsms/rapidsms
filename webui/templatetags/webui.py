#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os
from django.db import connection
from rapidsms.config import conf

from django import template
register = template.Library()


@register.inclusion_tag("webui/partials/region.html")
def region(name):
    def __path(app):
        return "%s/templates/regions/%s.html" %\
            (app["path"], name)
    
    return {
        "name": name,
        "includes": [
            __path(app)
             for app in conf("rapidsms", "apps")
             if os.path.exists(__path(app))
        ]}


@register.inclusion_tag("webui/partials/debug-dump.html")
def debug_dump():
    return { "queries": connection.queries }
