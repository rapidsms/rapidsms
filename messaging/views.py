#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re, urllib
from rapidsms.webui.utils import *
from apps.reporters.models import *


def index(req):
    flat_checked = urllib.unquote(req.COOKIES.get("recipients", ""))
    checked = re.split(r'\s+', flat_checked)
    
    def __reporter(rep):
        rep.checked = str(rep.pk) in checked
        return rep
    
    return render_to_response(req,
        "messaging/index.html", {
            "columns": ["Name", "Role", "Location"],
            "reporters": paginated(req, Reporter.objects.all(), wrapper=__reporter) })
