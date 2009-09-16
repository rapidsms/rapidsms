#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from datetime import datetime
from base import MessageBase


class OutgoingMessage(MessageBase):
    """
    """

    def __init__(self, connection, text):
        MessageBase.__init__(self, connection, text)
        self.sent_at = None


    @property
    def date(self):
        return self.sent_at


    def send(self):
        """
        Send this message via self.connection.backend, and returns true if the
        message was sent successfully.

        Warning: This method blocks the current thread until the backend accepts
        or rejects the message, which takes... as long as it takes. There is
        currently no way to send messages asynchronously.
        """

        self.sent = self.connection.backend.router.outgoing(self)
        if self.sent: self.sent_at = datetime.now()
        return self.sent
