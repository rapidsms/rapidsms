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


@register.inclusion_tag("rapidsms/templatetags/paginator.html")
def paginator(objects):

    prefix = getattr(objects, "prefix", "")
    dom_id = prefix + "paginator"
    page_param = prefix + "page"

    def _link(page_number):
        return _self_link(objects.request, **{page_param: page_number})

    def _page(number):
        return {
            "number": number,
            "link": _link(number),
            "active": (objects.number == number)}

    # TODO: gah, extract this junk a private method
    max_page_links = settings.PAGINATOR_MAX_PAGE_LINKS
    last_page_number = objects.paginator.num_pages + 1
    last_low_number = math.floor(max_page_links / 2)
    first_high_number = last_page_number - math.ceil(max_page_links / 2)

    page_links = [
        _page(number)
        for number in range(1, last_page_number)
        if number <= last_low_number or number >= first_high_number]

    # if any pages were hidden, inject None, to be rendered as elipsis
    if max_page_links < last_page_number:
        page_links.insert(last_low_number, None)

    subcontext = {
        "dom_id":     dom_id,
        "page_links": page_links}

    # if we're viewing the first page, the  << first and < prev links
    # are replaced with spans.
    if objects.number > 1:
        subcontext.update({
            "first_page_link": _link(1),
            "prev_page_link":  _link(objects.previous_page_number())})

    # likewise for the last page.
    if objects.number < objects.paginator.num_pages:
        subcontext.update({
            "next_page_link":  _link(objects.next_page_number()),
            "last_page_link":  _link(objects.paginator.num_pages)})

    return subcontext


def _self_link(req, **kwargs):
    new_kwargs = req.GET.copy()

    # build a new querydict using the GET params from the current
    # request, with those passed to this function overridden. we can't
    # use QueryDict.update here, since it APPENDS, rather than REPLACES.
    for k, v in kwargs.items():
        new_kwargs[k] = v

    kwargs_enc = new_kwargs.urlencode()
    return "%s?%s" % (req.path, kwargs_enc)
