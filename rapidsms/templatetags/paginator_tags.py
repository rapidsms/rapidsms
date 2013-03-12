#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import math
from django import template
register = template.Library()

# when this module is imported via {% load paginator_tags %}, it is
# imported as django.templatetags.paginator_tags, which prevents a
# relative import (..conf) to rapidsms from working here. in fact, that
# would import django.conf, so it will appear to be working, but per-app
# settings won't work! PAGINATOR_ defaults are in the ..settings module.
from rapidsms.conf import settings


@register.inclusion_tag("rapidsms/templatetags/paginator.html", takes_context=True)
def paginator(context, page, prefix=""):

    dom_id = prefix + "paginator"
    page_param = prefix + "page"
    request = context["request"]

    def _link(page_number):
        return _self_link(request, **{page_param: page_number})

    def _page(number):
        return {
            "number": number,
            "link": _link(number),
            "active": (page.number == number)}

    #border_links represent the first N pages and last N pages in the paginator
    border_links = settings.PAGINATOR_BORDER_LINKS
    #adjacent_links represents the N pages around the current page
    adjacent_links = settings.PAGINATOR_ADJACENT_LINKS
    last_page_number = page.paginator.num_pages + 1
    page_links = []

    #first set of border links
    pages = {p for p in range(1, border_links + 1)}
    #last border links
    for p in range(last_page_number - border_links, last_page_number):
        pages.add(p)
    #make sure that the adjacent links do not go outside of the page range
    first_adjacent = max(1, page.number - adjacent_links)
    last_adjacent = min(page.number + adjacent_links+1, last_page_number)
    for p in range(first_adjacent, last_adjacent):
        pages.add(p)
    last_page = None
    for p in sorted(pages):
        #if there is a gap in the list, add a None which will generate an elipsis
        if last_page and last_page != p - 1:
            page_links.append(None)
        last_page = p
        page_links.append(_page(p))

    subcontext = {
        "dom_id":     dom_id,
        "page_links": page_links}

    # if we're viewing the first page, the  << first and < prev links
    # are replaced with spans.
    if page.number > 1:
        subcontext.update({
            "first_page_link": _link(1),
            "prev_page_link":  _link(page.previous_page_number())})

    # likewise for the last page.
    if page.number < page.paginator.num_pages:
        subcontext.update({
            "next_page_link":  _link(page.next_page_number()),
            "last_page_link":  _link(page.paginator.num_pages)})

    return subcontext


def _self_link(request, **kwargs):
    new_kwargs = request.GET.copy()

    # build a new querydict using the GET params from the current
    # request, with those passed to this function overridden. we can't
    # use QueryDict.update here, since it APPENDS, rather than REPLACES.
    for k, v in kwargs.items():
        new_kwargs[k] = v

    kwargs_enc = new_kwargs.urlencode()
    return "%s?%s" % (request.path, kwargs_enc)
