#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
register = template.Library()


@register.inclusion_tag("webui/partials/paginator.html", takes_context=True)
def paginator(context, objects):
    return {
        "objects": objects,
        
        # django's template tags suck. we must also include the request
        # object in this context, because django doesn't pass along the
        # parent context (containing request.GET, from which we pluck
        # the current page number and objects per page) automatically. 
        "request": context["request"]
    }
