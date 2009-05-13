#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.webui.utils import *
from apps.reporters.models import *


def index(req):
    return render_to_response(req,
        "messaging/index.html", {
            "columns": ["Name", "Role", "Location"],
            "reporters": paginated(req, Reporter.objects.all()) })
