#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re, urllib
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from rapidsms.webui.utils import *
from apps.reporters.models import *


def index(req):
    def cookie_recips(status):
        flat = urllib.unquote(req.COOKIES.get("recip-%s" % status, ""))
        return re.split(r'\s+', flat) if flat != "" else []
    
    checked = cookie_recips("checked")
    error   = cookie_recips("error")
    sent    = cookie_recips("sent")
    
    def __reporter(rep):
        uid = str(rep.pk)
        rep.is_checked = uid in checked
        rep.is_error   = uid in error
        rep.is_sent    = uid in sent
        return rep
    
    return render_to_response(req,
        "messaging/index.html", {
            "columns": ["Name", "Role", "Location"],
            "reporters": paginated(req, Reporter.objects.all()) })


def __redir_to_index():
    return HttpResponseRedirect(
        reverse("messaging-index"))


def all(req):
    """Add the primary key of every recipient to the recip-checked
       cookie, which is used to pass around the list of recipients
       that the user is planning to message. This job can be done
       in Javascript (and will); this is the HTML-only fallback."""
    recips = Reporter.objects.values_list("pk", flat=True)
    flat_recips = "%20".join(map(str, recips))
    
    resp = __redir_to_index()
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
       sto tore the primary keys of recipients that receive (or fail to
       receive) messages, for users to inspect on the messaging index."""
    resp = __redir_to_index()
    resp.delete_cookie("recip-error")
    resp.delete_cookie("recip-sent")
    return resp
