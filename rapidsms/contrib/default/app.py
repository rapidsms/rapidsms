#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.conf import settings
from rapidsms.apps.base import AppBase


class App(AppBase):

    def default(self, msg):
        response = settings.DEFAULT_RESPONSE
        if response is not None:
            if hasattr(settings, 'PROJECT_NAME') and settings.PROJECT_NAME:
                response = response % {'project_name': settings.PROJECT_NAME}
            msg.error(response)
