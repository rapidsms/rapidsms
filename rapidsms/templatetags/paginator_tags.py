#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
from django.core.exceptions import ImproperlyConfigured


register = template.Library()

# when this module is imported via {% load paginator_tags %}, it is
# imported as django.templatetags.paginator_tags, which prevents a
# relative import (..conf) to rapidsms from working here. in fact, that
# would import django.conf, so it will appear to be working, but per-app
# settings won't work! PAGINATOR_ defaults are in the ..settings module.
from rapidsms.conf import settings  # noqa


if "django.template.context_processors.request" not in settings.TEMPLATES[0]['OPTIONS']['context_processors']:
    raise ImproperlyConfigured(
        "To use paginator tag, add 'django.template.context_processors.request' "
        "to your TEMPLATES 'context_processors'"
    )


@register.inclusion_tag("rapidsms/templatetags/paginator.html", takes_context=True)
def paginator(context, page, prefix=""):
    """Paginator Template Tag

    Take a page from a paginator, creates links to relevant pages, and returns
    an HTML version of those links.  It links to the first
    ``rapidsms.settings.PAGINATOR_BORDER_LINKS``, last
    ``rapidsms.settings.PAGINATOR_BORDER_LINKS`` pages,
    and the ``rapidsms.settings.PAGINATOR_ADJACENT_LINKS`` pages around the
    current page.

    :param context: Template context
    :param page: Paginator page object representing the current page
    :param prefix: Prefix for the page GET parameter
    """

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

    # num_border_links represent the first N pages and last N pages in the paginator
    num_border_links = min(settings.PAGINATOR_BORDER_LINKS, page.paginator.num_pages)
    # num_adjacent_links represents the N pages around the current page
    num_adjacent_links = min(settings.PAGINATOR_ADJACENT_LINKS, page.paginator.num_pages)
    last_page_number = page.paginator.num_pages + 1

    pages = set([page.number])
    # first set of border links
    for p in range(1, num_border_links + 1):
        pages.add(p)
    # last border links
    for p in range(last_page_number - num_border_links, last_page_number):
        pages.add(p)
    # make sure that the adjacent links do not go outside of the page range
    first_adjacent = max(1, page.number - num_adjacent_links)
    last_adjacent = min(page.number + num_adjacent_links + 1, last_page_number)
    for p in range(first_adjacent, last_adjacent):
        pages.add(p)

    page_links = []
    pages = sorted(pages)
    for i in range(len(pages) - 1):
        page_links.append(_page(pages[i]))
        gap = pages[i + 1] - pages[i]
        if gap == 2:
            # if the ellipsis would only cover 1 page, add that page.
            page_links.append(_page(pages[i] + 1))
        elif gap > 2:
            # add an ellipsis when there is a gap in the pages.
            page_links.append(None)
    if pages:
        page_links.append(_page(pages[-1]))

    subcontext = {
        "dom_id": dom_id,
        "page_links": page_links}

    if page.number > 1:
        subcontext.update({
            "prev_page_link": _link(page.previous_page_number())})

    if page.number < page.paginator.num_pages:
        subcontext.update({
            "next_page_link": _link(page.next_page_number())})

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
