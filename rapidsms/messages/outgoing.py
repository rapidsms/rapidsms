#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from datetime import datetime
from rapidsms.messages.base import MessageBase


class OutgoingMessage(MessageBase):
    """Outbound message that can easily be sent to the router."""

    def __init__(self, *args, **kwargs):
        self.in_reply_to = kwargs.pop('in_reply_to', None)
        self.received_at = kwargs.pop('sent_at', datetime.now())
        super(OutgoingMessage, self).__init__(*args, **kwargs)
        self.sent = False

    @property
    def date(self):
        return self.sent_at

    def send(self):
        """Simple wrapper for the send() API."""
        from rapidsms.router import send
        send(self.text, self.connection)
        self.sent = True
