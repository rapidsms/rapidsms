#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
register = template.Library()


from django.db import connection


@register.inclusion_tag("webui/partials/query-log.html")
def query_log():
    return { "queries": connection.queries }
