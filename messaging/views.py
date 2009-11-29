#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re, urllib
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import FieldError
from django.core.urlresolvers import reverse
from rapidsms.djangoproject.utils import *
from reporters.models import *
from models import combined_message_log, __combined_message_log_row


def index(req):
    def cookie_recips(status):
        flat = urllib.unquote(req.COOKIES.get("recip-%s" % status, ""))
        return map(int, re.split(r'\s+', flat)) if flat != "" else []

    checked  = cookie_recips("checked")
    error    = cookie_recips("error")
    sent     = cookie_recips("sent")

    show_search = False
    filtered    = False
    hits        = []

    def __reporter(rep):
        rep.is_checked = rep.pk in checked
        rep.is_error   = rep.pk in error
        rep.is_sent    = rep.pk in sent
        rep.is_hit     = rep.pk in hits
        return rep

    # if the field/cmp/query parameters were provided (ALL
    # OF THEM), we will mark some of the reporters as HIT
    if "query" in req.GET or "field" in req.GET or "cmp" in req.GET:
        if "query" not in req.GET or "field" not in req.GET or "cmp" not in req.GET:
            return HttpResponse("The query, field, and cmp fields may only be provided or omitted TOGETHER.",
                status=500, mimetype="text/plain")

        # search with: field__cmp=query
        kwargs = { str("%s__%s" % (req.GET["field"], req.GET["cmp"])): req.GET["query"] }
        hits = Reporter.objects.filter(**kwargs).values_list("pk", flat=True)
        show_search = True
        filtered = True

    # optionally show the search field as default
    if "search" in req.GET and req.GET["search"]:
        show_search = True

    # the columns to display in the "field"
    # field of the search form. this is WAY
    # ugly, and should be introspected
    columns = [
        ("alias", "Alias"),
        ("first_name", "First Name"),
        ("last_name", "Last Name")]#,
        #("role__title", "Role"),
        #("location__name", "Location")]

    resp = render_to_response(req,
        "messaging/index.html", {
            "columns":     columns,
            "filtered":    filtered,
            "query":       req.GET.get("query", ""),
            "field":       req.GET.get("field", ""),
            "cmp":         req.GET.get("cmp", ""),
            "show_search": show_search,
            "message_log": paginated(req, combined_message_log(checked), prefix="msg", wrapper=__combined_message_log_row),
            "reporters":   paginated(req, Reporter.objects.all(), wrapper=__reporter) })

    # if we just searched via GET (not via AJAX), store the hits
    # in a cookie for the client-side javascript to pick up. if
    # we don't, the javascript will overwrite the classes that
    # set in the template
    if filtered:
        flat_hits = " ".join(map(str, hits))
        resp.set_cookie("recip-hit", flat_hits)

        # update the search cookie (in the same weird-ass
        # pipe-delimited format as in the client-side script),
        # in case we're  mixing js and non-js searches
        resp.set_cookie("recip-search", 
            "|".join([
                req.GET["field"],
                req.GET["cmp"],
                req.GET["query"]]))

    return resp


def search(req):

    # fetch the data, filtering by ALL GET
    # parameters (raise if any are invalid)
    try:
        filters = dict([(str(k), v) for k, v in req.GET.items()])
        results = Reporter.objects.filter(**filters)

    except FieldError, e:
        return HttpResponse(e.message,
            status=500, mimetype="text/plain")

    recips = results.values_list("pk", flat=True)

    return HttpResponse(
        " ".join(map(str, recips)),
        content_type="text/plain")


def __redir_to_index():
    return HttpResponseRedirect(
        reverse("messaging-index"))


def all(req):
    """If this view is requested directly, add the primary key of every
       recipient to the recip-checked cookie (which is used to pass around
       the list of recipients that the user is planning to message), and
       redirect to the index to view it. If the view was requested by AJAX,
       return only the data that we _would_ have cookied, to allow the client
       to do it without reloading the page."""

    recips = Reporter.objects.values_list("pk", flat=True)

    if req.is_ajax():
        return HttpResponse(
            " ".join(map(str, recips)),
            content_type="text/plain")

    else:
        resp = __redir_to_index()
        flat_recips = "%20".join(map(str, recips))
        resp.set_cookie("recip-checked", flat_recips)
        return resp


def none(req):
    """Delete the reicp-checked cookie, and redirect back to
       the messaging index. This is another HTML-only fallback."""

    resp = __redir_to_index()
    resp.delete_cookie("recip-checked")
    return resp


def clear(req):
    """Delete the recip-error and recip-sent cookies, which are used
       to store the primary keys of recipients that receive (or fail to
       receive) messages, for users to inspect on the messaging index."""

    resp = __redir_to_index()
    resp.delete_cookie("recip-error")
    resp.delete_cookie("recip-sent")
    return resp
