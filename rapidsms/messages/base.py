#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import copy
from uuid import uuid4
import warnings


class MessageBase(object):
    """Basic message representation with text and connection(s)."""

    def __init__(self, connections=None, text=None, id_=None,
                 in_response_to=None, fields=None,
                 connection=None):  # old deprecated parameter
        # Allow and cope with old 'connection' argument but issue a warning
        if connections is None and connection is not None:
            connections = [connection]
            connection = None
            warnings.warn("Message(connection=) is deprecated, please start "
                          "using .connections", DeprecationWarning)
        if connection is not None:
            raise TypeError("Do not pass both `connections` and `connection`"
                            "to MessageBase.__init__(), just `connections`")

        # had to make `text` optional so we could make connections optional,
        # but it really is required
        if text is None:
            raise TypeError("MessageBase.__init__ did not get required "
                            "argument `text`")
        #: a unique ID for this message
        self.id = id_ or self.generate_id()
        #: The connections this message was received from or sent to. A
        #: list of :py:class:`~rapidsms.models.Connection`
        self.connections = connections
        #: the message
        self.text = text
        #: save original text for future reference
        self.raw_text = copy.copy(self.text)
        #: fields can be used to pass along arbitrary metadata
        self.fields = fields or {}
        #: link back to original message if this is a response
        self.in_response_to = in_response_to
        #: a message is considered "unprocessed" until rapidsms has
        #: dispatched it to all apps.
        self.processed = False
        #: a message can be marked "handled" by any app, which will
        #: short-circuit the default phase in the router.
        self.handled = False

    def __unicode__(self):
        return self.text

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.text)

    @staticmethod
    def generate_id():
        """Create a random unique ID for this message object."""
        return uuid4().get_hex()

    @property
    def connection(self):
        """The first :py:class:`~rapidsms.models.Connection` - `deprecated`.
        """
        warnings.warn("MessageBase.connection is deprecated; please start using .connections", DeprecationWarning)
        return self.connections[0]

    @property
    def contact(self):
        """The first connection's :py:class:`~rapidsms.models.Contact`
        - `deprecated`
        """
        warnings.warn(
            "MessageBase.contact is deprecated; please start using .connections[i].contact",
            DeprecationWarning
        )
        return self.connections[0].contact

    @property
    def peer(self):
        """
        Return the identity (eg. a phone number, email address, irc
        nickname) on the other end of this message. But you shouldn't
        use this method. It only seems to encourage people to ignore the
        distinction between backends and identities, and create fields
        like "mobile_number", which is all kinds of wrong.
        `deprecated`
        """
        warnings.warn("MessageBase.peer is deprecated; please access the needed data directly.")
        return self.connections[0].identity
