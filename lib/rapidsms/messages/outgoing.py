#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.utils.translation.trans_real import translation
from datetime import datetime
from base import MessageBase


class OutgoingMessage(MessageBase):
    """
    """

    def __init__(self, connection, template, **kwargs):
        self._connection = connection
        self.template = template
        self.kwargs = kwargs
        self.sent_at = None

        try:
            from rapidsms.djangoproject import settings
            self.language = settings.LANGUAGE_CODE

        except EnvironmentError:
            self.language = None


    def __repr__(self):
        return "<OutgoingMessage (%s): %s>" %\
            (self.language, self.text)


    @property
    def text(self):
        t = translation(self.language)
        tmpl = t.gettext(self.template)
        return tmpl % self.kwargs


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
