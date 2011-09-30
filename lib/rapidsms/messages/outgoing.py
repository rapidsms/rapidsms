#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from datetime import datetime
from django.utils.translation.trans_real import translation
from .base import MessageBase
from ..errors import NoRouterError
from ..conf import settings


class OutgoingMessage(MessageBase):
    """
    """

    def __init__(self, connection=None, template=None, **kwargs):
        self._parts = []
        
        if template is not None:
            self.append(template, **kwargs)

        self._connection = connection
        self.sent_at = None


    @property
    def language(self):
        """
        Return the language which this message will be sent in. If
        possible, this is fetched from the recipient Contact model.
        Otherwise, it defaults to the ``LANGUAGE_CODE`` setting.
        """

        if self._connection.contact is not None:
            if self._connection.contact.language:
                return self._connection.contact.language

        return settings.LANGUAGE_CODE


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
        return unicode(" ".join([
            self._render_part(template, **kwargs)
            for template, kwargs in self._parts
        ]))


    @property
    def date(self):
        return self.sent_at


    def send(self):
        """
        Raises an exception to help developers upgrade legacy code to use
        the new interface for sending messages.
        """
        raise NoRouterError('The global router has been removed from RapidSMS. '
                            'You must send the this message by calling '
                            'router.outgoing(message).')
