#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import rapidsms
from reporters.models import *


class App (rapidsms.app.App):
    def ajax_POST_send_message(self, params, form):
        rep = Reporter.objects.get(pk=form["uid"])
        pconn = rep.connection()
        
        # abort if we don't know where to send the message to
        # (if the device the reporter registed with has been
        # taken by someone else, or was created in the WebUI)
        if pconn is None:
            raise Exception("%s is unreachable (no connection)" % rep)
        
        # attempt to send the message
        # TODO: what could go wrong here?
        be = self.router.get_backend(pconn.backend.slug)
        return be.message(pconn.identity, form["text"]).send()
