#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.utils.timezone import now
from rapidsms.messages.base import MessageBase


class OutgoingMessage(MessageBase):
    """Outbound message that can easily be sent to the router.
    """

    def __init__(self, *args, **kwargs):
        self.received_at = kwargs.pop('sent_at', now())
        if 'sent_at' in kwargs:
            raise Exception("OutgoingMessage.sent_at is meaningless")
        super(OutgoingMessage, self).__init__(*args, **kwargs)

    @property
    def sent_at(self):
        raise Exception("OutgoingMessage.sent_at is meaningless")

    @property
    def sent(self):
        raise Exception("OutgoingMessage.sent is meaningless")

    @property
    def date(self):
        raise Exception("OutgoingMessage.date is meaningless")

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
        """Send the message.  Equivalent to
        ``rapidsms.router.send(text, connections)``.
        """
        from rapidsms.router import send
        send(self.text, self.connections)
