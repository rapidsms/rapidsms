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

    def respond(self, text, class_=OutgoingMessage, **kwargs):
        """
        Instantiates a new OutgoingMessage object bound to the same
        connection(s). Optionally, the class of the outgoing message can be
        given, to give a hint about the contents of the message, which can be
        introspected by other apps during the outgoing phase(s).
        """
        msg = class_(connections=self.connections, text=text, in_reply_to=self,
                     **kwargs)
        self.responses.append(msg)
        return msg

    def error(self, text, **kwargs):
        return self.respond(class_=ErrorMessage, text=text, **kwargs)
