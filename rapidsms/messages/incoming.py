#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.messages.base import MessageBase
from rapidsms.messages.error import ErrorMessage


class IncomingMessage(MessageBase):
    """Inbound message that provides an API to handle responses.
    """

    def __init__(self, *args, **kwargs):
        if 'received_at' in kwargs:
            raise Exception("IncomingMessage.received_at is meaningless")
        super(IncomingMessage, self).__init__(*args, **kwargs)
        #: list of messages created by IncomingMessage.respond()
        self.responses = []

    @property
    def date(self):
        raise Exception("IncomingMessage.date is meaningless")

    def respond(self, text, **kwargs):
        """
        Respond to this message, sending the given text to the connections
        that this message came from.

        Responses are saved, and sent after incoming processing phases are
        complete.

        Arbitrary arguments are passed along to the
        :py:meth:`~rapidsms.router.send` method.

        :param string text: The text of the message
        :param connections: (optional) send to a different set of connections
            than were in the incoming message.
        :type connections: list of :py:class:`~rapidsms.models.Connection`
        :param in_response_to: (optional) the message being responded to.
        :type in_response_to: :py:class:`~rapidsms.messages.base.MessageBase`
        :returns: dictionary with the arguments that will be passed to
            :py:meth:`rapidsms.router.send` to send this response.
        """
        if 'template' in kwargs:
            raise TypeError("`template` is no longer valid usage for "
                            "respond().  Pass the message text as `text`.")

        context = {'text': text,
                   'connections': self.connections,
                   'in_response_to': self}
        context.update(kwargs)
        self.responses.append(context)
        return context

    def error(self, text, **kwargs):
        return self.respond(class_=ErrorMessage, text=text, **kwargs)
