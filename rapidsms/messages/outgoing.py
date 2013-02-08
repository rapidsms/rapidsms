#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from datetime import datetime
from rapidsms.messages.base import MessageBase


class OutgoingMessage(MessageBase):
    """Outbound message that can easily be sent to the router."""

    def __init__(self, *args, **kwargs):
        self.in_response_to = kwargs.pop('in_response_to', None)
        self.received_at = kwargs.pop('sent_at', datetime.now())
        super(OutgoingMessage, self).__init__(*args, **kwargs)
        self.sent = False

    @property
    def date(self):
        return self.sent_at

    def extra_backend_context(self):
        """Specific metadata to be included when passed to backends."""
        return {
            'fields': self.fields,
            'in_response_to': self.in_response_to,
        }

    def send(self):
        """Simple wrapper for the send() API."""
        from rapidsms.router import send
        send(self.text, self.connection)
        self.sent = True
