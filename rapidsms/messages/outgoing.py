#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from datetime import datetime
from rapidsms.messages.base import MessageBase


class OutgoingMessage(MessageBase):
    """Outbound message that can easily be sent to the router."""

    def __init__(self, *args, **kwargs):
        self.received_at = kwargs.pop('sent_at', datetime.now())
        super(OutgoingMessage, self).__init__(*args, **kwargs)
        self.sent = False

    @property
    def date(self):
        return self.sent_at

    def extra_backend_context(self):
        """Specific metadata to be included when passed to backends."""
        context = {}
        if self.in_response_to:
            original = self.in_response_to
            context['in_response_to'] = original.id
            if 'external_id' in original.fields:
                context['external_id'] = original.fields['external_id']
        return context

    def send(self):
        """Simple wrapper for the send() API."""
        from rapidsms.router import send
        send(self.text, self.connection)
        self.sent = True
