#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re, urllib
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
            "num_checked": len(checked),
            "reporters": paginated(req, Reporter.objects.all(), wrapper=__reporter) })
