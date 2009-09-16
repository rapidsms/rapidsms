#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.connection import Connection


class MessageBase(object):
    def __init__(self, connection, text=None):
        self._connection = connection
        self.text = text

    def __unicode__(self):
        return self.text

    @property
    def connection(self):
        return self._connection

    @property
    def peer (self):
        """
        Returns the identity (eg. a phone number, email address, irc nickname)
        of the other end of this message. But don't use this method. It only
        seems to encourage people to ignore the backend/identity distinction,
        and create fields like "mobile_number", which is all kinds of wrong.
        """

        return self.connection.identity 
