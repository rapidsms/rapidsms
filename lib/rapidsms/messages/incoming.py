#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from copy import copy
from datetime import datetime
from base import MessageBase
from outgoing import OutgoingMessage
from error import ErrorMessage


class IncomingMessage(MessageBase):
    """
    This class represents, naturally, an incoming message. It is probably only
    useful when instantiated by RapidSMS backends or test harnesses.
    """

    def __init__(self, connection, text, received_at=None, sent_at=None):
        MessageBase.__init__(self, connection, text)
        
        self.sent_at = sent_at
        self.received_at = received_at or datetime.now()
        self.responses = []

        # store the text AGAIN, somewhere that it really shouldn't
        # be messed with. some apps may choose to fudge with the
        # message text, so it's important to be able to recall
        # what the message started looking like
        self._raw_text = copy(self.text)

        # a message is considered "unprocessed" until rapidsms has
        # dispatched it to all apps, and flushed the responses out.
        # at least one http backend cares about this, because they
        # can only send messages in response to the incoming http
        # request; so they have to wait until processing is done.
        self.processed = False


    @property
    def raw_text(self):
        """
        Returns the message text in its original state.
        """

        return self._raw_text


    @property
    def date(self):
        return self.received_at


    def flush_responses(self):
        """
        Immediately sends all responses added to this message (via the respond
        method) in the order which they were added, and clears the queue.
        """

        while self.responses:
            self.responses.pop(0).send()


    def respond(self, text=None, cls=OutgoingMessage, **kwargs):
        """
        Instantiates a new OutgoingMessage object bound to the same connection
        as this object containing *text*, and queues it for delivery when the
        flush method is called.

        Optionally, the class (*cls*) of the outgoing message can be given, to
        give a hint about the contents of the message, which can be introspected
        by other apps during the outgoing phase(s).

        Any additional keyword arguments given are passed along to the outgoing
        message class initialize. See OutgoingMessage.__init__ for more on that.
        You really should. It's rather exciting.
        """

        msg = cls(self.connection, text, **kwargs)
        self.responses.append(msg)
        return msg


    def error(self, text, **kwargs):
        """
        docs plz.
        """

        return self.respond(text, ErrorMessage, **kwargs)
