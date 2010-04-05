#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.paginator import Paginator, EmptyPage, InvalidPage


def paginated(req, query_set, per_page=None, prefix="", wrapper=None):

    if per_page is None:
        from ..conf import settings
        per_page = settings.PAGINATOR_OBJECTS_PER_PAGE

    # since the behavior of this function depends on GET parameters, if
    # there is more than one paginated set per view, we must prefix the
    # parameters to differentiate them: path?users-page=1&groups-page=2
    prefix = ("%s-" % (prefix)) if prefix else ""

    # the per_page argument to this function provides a default, but can
    # be overridden. (the template provides no interface for this yet.)
    if (prefix + "per-page") in req.GET:
        try:
            per_page = int(req.GET[prefix+"per-page"])

        # if it was provided, it must be valid
        except ValueError:
            raise ValueError("Invalid per-page parameter: %r" %
                (req.GET[prefix + "per-page"]))

    try:
        page = int(req.GET.get(prefix+"page", "1"))
        paginator = Paginator(query_set, per_page)
        objects = paginator.page(page)

    # have no mercy if the page parameter is not valid. there should be
    # no links to an invalid page, so coercing it to assume "page=xyz"
    # means "page=1" would just mask bugs
    except (ValueError, EmptyPage, InvalidPage):
        raise ValueError("Invalid Page: %r" %
            (req.GET[prefix + "page"]))

    # if a wrapper function was provided, call it for each object on the
    # page, and replace the list with the result. TODO: make it lazy!
    if wrapper is not None:
        objects.raw_object_list = objects.object_list
        objects.object_list = map(wrapper, objects.object_list)

    # attach the prefix (it might be blank) to the objects, to be found
    # by the {% paginator %} tag, to create the prev/next page links
    objects.prefix = prefix

    return objects

