RapidSMS Architecture Overview
==============================

.. image:: /_static/rapidsms-architecture.png
    :width: 100 %

You can also view the `full-sized version`_.

Introduction
------------

RapidSMS is divided into a few core components:

* :ref:`Applications <application-overview>`
* :ref:`Backends <backend-overview>`
* :ref:`Router <router-overview>`

If you are new to RapidSMS most likely you will want to develop Applications.


.. _application-overview:

Applications
------------

RapidSMS :doc:`applications <applications/index>`, or "apps", perform one or
more of the following functions:

* Performs your business logic
* Handles and responds to messages
* Extends the data model
* Creates a web interface with Django views and templates

For example, a registration application may provide a messaging protocol for
users to register themselves into the system. In general, you'll probably be writing applications more than anything else. Please see the
:doc:`application documentation <applications/index>` for more information.

RapidSMS represents the entities it communicates with using
:ref:`contacts`, which you'll also want to understand before writing
applications.

.. _backend-overview:

Backends
--------

:doc:`Backends <backends/index>` receive messages from external sources and
deliver messages from applications to external sources. Example backends
include:

* Using :doc:`Kannel <backends/kannel>` to communicate to a `GSM modem`_ connected over USB or Serial
* Using `Twilio`_ or `Clickatell`_ to send and receive SMS messages over HTTP

Please see the :doc:`backend documentation <backends/index>` for more
information.

.. _router-overview:

Router
------

The :doc:`router <router/index>` is the message processing component of
RapidSMS. It provides the infrastructure to receive incoming, send outgoing
messages, and gluing together your applications and backends. RapidSMS provides several built-in routers to use based on the needs of your application.

Please see the :doc:`router documentation <router/index>` for more information.

.. _full-sized version: https://raw.github.com/rapidsms/rapidsms/master/docs/_static/rapidsms-architecture.png
.. _GSM modem: http://en.wikipedia.org/wiki/GSM
.. _Twilio: http://www.twilio.com/
.. _Clickatell: http://www.clickatell.com/
