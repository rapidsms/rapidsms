#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
register = template.Library()


@register.inclusion_tag("rapidsms/templatetags/tables/table.html")
def render_table(table):
    return { "table": table }


@register.inclusion_tag("rapidsms/templatetags/tables/colgroup.html")
def render_colgroup(table):
    return { "table": table }


@register.inclusion_tag("rapidsms/templatetags/tables/thead.html")
def render_thead(table):
    return { "table": table }


@register.inclusion_tag("rapidsms/templatetags/tables/tbody.html")
def render_tbody(table):
    return { "table": table }


@register.inclusion_tag("rapidsms/templatetags/tables/tfoot.html")
def render_tfoot(table):
    return { "table": table }


@register.simple_tag
def render_cell(table, column, row):
    return table.render_cell(column, row)
