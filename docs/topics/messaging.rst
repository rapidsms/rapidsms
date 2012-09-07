=========
Messaging
=========

.. module:: rapidsms.messaging

A clean, simple API is provided to send and receive messages in RapidSMS. For most cases, you'll just need to use the ``send`` and ``receive`` functions outlined below.

Receiving Messages
------------------

To receive a message, you can use the ``receive`` function, which will automaticaly create an ``IncomingMessage`` and pass it to your router to be processed. Typically, backends will make the most use of ``receive``, but it can be used anywhere within your application to route an incoming message (such as from a Django view).

Here's an example using ``receive``::

    from rapidsms.router import receive
    receive("echo hello", identity="12223334444", backend_name="example-backend")

This sends a message to the router saying ``echo hello`` was received on the ``example-backend`` from number ``12223334444``. You can find more examples of ``receive`` in the official RapidSMS `backends <https://github.com/rapidsms/rapidsms/tree/feature/new-routing/lib/rapidsms/backends>`_.

Sending Messages
----------------

It's just as easy to send a message using RapidSMS. Similar to ``recieve``, backends will primarliy use ``send``, but you can send a message from anywhere within your application.

Here's an example using ``send``::

    from rapidsms.router import send
    send("hello", identity="12223334444", backend_name="example-backend")

This sends ``echo hello`` to ``12223334444`` using ``example-backend``. You can find more examples of ``send`` in the official RapidSMS `backends <https://github.com/rapidsms/rapidsms/tree/feature/new-routing/lib/rapidsms/backends>`_.
