#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
register = template.Library()


@register.inclusion_tag('rapidsms/templatetags/form.html')
def render_form(form):
    return {"form": form}
