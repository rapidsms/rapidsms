#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.utils.translation.trans_real import translation
from datetime import datetime
from base import MessageBase


class OutgoingMessage(MessageBase):
    """
    """

    def __init__(self, connection=None, template=None, **kwargs):
        self._parts = []
        
        if template is not None:
            self.append(template, **kwargs)

        self._connection = connection
        self.sent_at = None

        # default to LANGUAGE_CODE from django settings (which can
        # be set in the [django] section of rapidsms.ini, or english,
        # if no LANGUAGE_CODE is set anywhere
        try:
            from rapidsms.djangoproject import settings
            self.language = settings.LANGUAGE_CODE

        except:
            self.language = "en"



    def append(self, template, **kwargs):
        self._parts.append((template, kwargs))


    def __repr__(self):
        return "<OutgoingMessage (%s): %s>" %\
            (self.language, self.text)


    def _render_part(self, template, **kwargs):
        t = translation(self.language)
        tmpl = t.gettext(template)
        return tmpl % kwargs


    @property
    def text(self):
        return " ".join([
            self._render_part(template, **kwargs)
            for template, kwargs in self._parts
        ])


    @property
    def date(self):
        return self.sent_at


    def send(self):
        """
        Send this message via self.connection.backend, and returns true if the
        message was sent successfully.

        Warning: This method blocks the current thread until the backend accepts
        or rejects the message, which takes... as long as it takes. There is
        currently no way to send messages asynchronously.
        """

        self.sent = self.connection.backend.router.outgoing(self)
        if self.sent: self.sent_at = datetime.now()
        return self.sent
