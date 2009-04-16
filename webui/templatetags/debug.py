#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
register = template.Library()


from django.db import connection


@register.inclusion_tag("webui/partials/debug-dump.html")
def debug_dump():
    return { "queries": connection.queries }
