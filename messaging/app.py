#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

class App (rapidsms.app.App):
    def ajax_GET_recipients(self, params):
        return [
            {"app": app, "recipients": app.ajax_GET_recipients(params)}
            for app in self.router.apps
            if (app != self) and hasattr(app, "ajax_GET_recipients")]
