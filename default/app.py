#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.conf import settings
import rapidsms


class App(rapidsms.App):
    def default(self, msg):
        if settings.DEFAULT_RESPONSE is not None:
            msg.error(settings.DEFAULT_RESPONSE,
                project_name=settings.PROJECT_NAME)
