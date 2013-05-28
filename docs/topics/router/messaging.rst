=============
Messaging API
=============

.. module:: rapidsms.router.api

A clean, simple API is provided to send and receive messages in RapidSMS. For
most cases, you'll just need to use the ``send`` and ``receive`` functions
outlined below.

.. _receiving-messages:

Receiving Messages
------------------

.. autofunction:: rapidsms.router.receive

To receive a message, you can use the ``receive`` function, which will
automatically create an :py:class:`~rapidsms.messages.incoming.IncomingMessage`
and pass it to your router to be
processed. Typically, backends will make the most use of ``receive``, but it
can be used anywhere within your application to route an incoming message (such
as from a Django view).

Here's an example using ``receive``::

    from rapidsms.router import receive
    receive("echo hello", connection)

This sends a message to the router saying ``echo hello`` was received from a
:py:class:`~rapidsms.models.Connection` object. You can find more examples of
``receive`` in the official RapidSMS
`backends <https://github.com/rapidsms/rapidsms/tree/master/rapidsms/backends>`_.

.. autoclass:: rapidsms.messages.incoming.IncomingMessage
    :show-inheritance:
    :members:


.. _sending-messages:

Sending Messages
----------------

.. autofunction:: rapidsms.router.send

It's just as easy to send a message using RapidSMS. You can send a message from
anywhere within your application. Here's an example using ``send``::

    from rapidsms.router import send
    send("hello", connections)

This sends ``hello`` to each identity and backend associated with the
``connections`` object.  You can find more examples of ``send`` in the official
RapidSMS `backends <https://github.com/rapidsms/rapidsms/tree/master/rapidsms/backends>`_.

.. autoclass:: rapidsms.messages.outgoing.OutgoingMessage
    :show-inheritance:
    :members:

MessageBase
-----------

Both incoming and outgoing message classes inherit from a common class,
MessageBase.

.. autoclass:: rapidsms.messages.base.MessageBase
    :members:

ErrorMessage
------------

There's also an ErrorMessage class that can be used when sending error
messages.

.. autoclass:: rapidsms.messages.error.ErrorMessage
    :show-inheritance:
    :members:

.. _contacts:

Contacts
--------

RapidSMS represents entities that it can communicate with
using a :py:class:`~rapidsms.models.Contact` object. Each
Contact has a name. A Contact could represent a person,
an organization, or any other entity that might have a phone,
email account, etc.

.. autoclass:: rapidsms.models.Contact
    :show-inheritance:

Most of a Contact is represented in the ContactBase class:

.. autoclass:: rapidsms.models.ContactBase
    :members:

Connections
-----------

RapidSMS might be able to communicate with an entity represented by
a Contact in multiple ways. The entity could have several phone numbers,
email addresses, etc.

RapidSMS uses a :py:class:`~rapidsms.models.Connection`
to represent each way of communicating with a
Contact. Each Connection specifies a backend to use, and how the entity
is identified on that backend. The identifier is called an ``identity``,
and depending on the backend, it could be a phone number, email address,
or something else. Most RapidSMS code should not make any assumptions
about the format of identities.

.. autoclass:: rapidsms.models.Connection
    :show-inheritance:
    :members:

Most of a Connection is represented in the ConnectionBase class:

.. autoclass:: rapidsms.models.ConnectionBase
    :members:

.. _connection_lookup:

Connection Lookup
-----------------

.. autofunction:: rapidsms.router.lookup_connections

Since most of the time you'll need to find connections for a backend and phone
number, RapidSMS has a helper function, ``lookup_connections``, to do the
lookup for you. Additionally, if the backend and phone number connection
doesn't exist, it'll be created automatically. Here's an example of
``lookup_connections``::

    from rapidsms.router import send, lookup_connections
    connections = lookup_connections(backend="example-backend",
                                     identities=['1112223333'])
    send("hello", connections=connections)
