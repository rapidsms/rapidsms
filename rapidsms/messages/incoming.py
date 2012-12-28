#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from datetime import datetime
from .base import MessageBase
from .outgoing import OutgoingMessage
from .error import ErrorMessage


class IncomingMessage(MessageBase):
    """
    This class represents, naturally, an incoming message. It is probably only
    useful when instantiated by RapidSMS backends or test harnesses.
    """

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
