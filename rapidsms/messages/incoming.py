#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from datetime import datetime
from rapidsms.messages.base import MessageBase
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.messages.error import ErrorMessage


class IncomingMessage(MessageBase):
    """Inbound message that provides an API to generate responses."""

    def __init__(self, *args, **kwargs):
        self.received_at = kwargs.pop('received_at', datetime.now())
        super(IncomingMessage, self).__init__(*args, **kwargs)
        # list of messages created by IncomingMessage.respond()
        self.responses = []

    @property
    def date(self):
        return self.received_at

    def respond(self, text, **kwargs):
        """
        Respond to this message. Router will process responses automatically.
        """
        context = {'text': text, 'connections': self.connections,
                   'in_reply_to': self}
        context.update(kwargs)
        self.responses.append(context)
        return context

    def error(self, text, **kwargs):
        return self.respond(class_=ErrorMessage, text=text, **kwargs)
