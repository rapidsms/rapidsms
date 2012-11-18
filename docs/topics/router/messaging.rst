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

.. function:: receive(text, connection, fields=None)
    :module: rapidsms.router.api

    Creates an incoming message and passes it to the router for processing.

    :param text: text message
    :param connection: RapidSMS connection object
    :param fields: Optional meta data to attach to the message object

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
official RapidSMS `backends <https://github.com/rapidsms/rapidsms/tree/feature
/new-routing/lib/rapidsms/backends>`_.

.. _sending-messages:

Sending Messages
----------------

.. function:: send(text, connections)
    :module: rapidsms.router.api

    Creates an outgoing message and passes it to the router to be processed
    and sent via the respective backend.

    :param text: text message
    :param connection: a single or list of RapidSMS connection objects

It's just as easy to send a message using RapidSMS. Similar to ``recieve``,
backends will primarliy use ``send``, but you can send a message from anywhere
within your application.

Here's an example using ``send``::

    from rapidsms.router import send
    send("hello", connection)

This sends ``echo hello`` to the identity and backend associated with the
``connection`` object.  You can find more examples of ``send`` in the official
RapidSMS `backends <https://github.com/rapidsms/rapidsms/tree/feature/new-
routing/lib/rapidsms/backends>`_.

.. _connection_lookup:

Connection Lookup
-----------------

.. function:: lookup_connections(backend, identities)
    :module: rapidsms.router.api

    Return connections associated with backend and identities.

    :param backend: backend name (as a string) or RapidSMS backend object
    :param connection: list of identities associated

Since most of the time you'll need to find connections for a backend and phone
number, RapidSMS has a helper function, ``lookup_connections``, to do the
lookup for you. Additionally, if the backend and phone number connection
doesn't exist, it'll be created automatically. Here's an example of
``lookup_connections``::

    from rapidsms.router import send, lookup_connections
    connections = lookup_connections(backend="example-backend",
                                     identities=['1112223333'])
    send("hello", connections=connections)
