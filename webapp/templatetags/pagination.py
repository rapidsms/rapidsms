#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.webui.utils import self_link

from django import template
register = template.Library()


@register.inclusion_tag("webapp/partials/paginator.html", takes_context=True)
def paginator(context, objects):
    
    prefix = getattr(objects, "prefix", "")
    page_param = prefix + "page"
    req = context["request"]
    
    def __link_to(page):
        kwargs = { page_param: page }
        return self_link(req, **kwargs)
    
    return {
        "objects":         objects,
        "page_param":      page_param,
        "first_page_link": __link_to(1),
        "prev_page_link":  __link_to(objects.previous_page_number()),
        "next_page_link":  __link_to(objects.next_page_number()),
        "last_page_link":  __link_to(objects.paginator.num_pages),
        
        # django's template tags suck. we must also include the request
        # object in this context, because django doesn't pass along the
        # parent context (containing request.GET, from which we pluck
        # the current page number and objects per page) automatically. 
        "request": context["request"]
    }
