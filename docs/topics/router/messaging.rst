=========
Messaging
=========

.. module:: rapidsms.router.api

A clean, simple API is provided to send and receive messages in RapidSMS. For
most cases, you'll just need to use the ``send`` and ``receive`` functions
outlined below.

.. _receiving-messages:

Receiving Messages
------------------

.. autofunction:: rapidsms.router.receive

To receive a message, you can use the ``receive`` function, which will
automaticaly create an ``IncomingMessage`` and pass it to your router to be
processed. Typically, backends will make the most use of ``receive``, but it
can be used anywhere within your application to route an incoming message (such
as from a Django view).

Here's an example using ``receive``::

    from rapidsms.router import receive
    receive("echo hello", connection)

This sends a message to the router saying ``echo hello`` was received from a
``connection`` object. You can find more examples of ``receive`` in the
official RapidSMS `backends <https://github.com/rapidsms/rapidsms/tree/master/rapidsms/backends>`_.

.. autoclass:: rapidsms.messages.incoming.IncomingMessage
    :members:
    :inherited-members:


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
