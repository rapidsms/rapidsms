.. _tutorial04:

RapidSMS Tutorial Part 4
========================

*This tutorial is a draft.* Comments are welcome in `this discussion`_ on Google Groups.

.. _this discussion: https://groups.google.com/forum/#!topic/rapidsms-dev/NLd3lUinUFQ

In this part of the tutorial, we'll show one way to move beyond the
message tester to send and receive text message with real phones.

Online Providers
----------------

A common way to connect your RapidSMS application to the telephone
system is to use an online service. Typically such a service will
provide an HTTP interface that lets you send messages, and a phone
number that can receive messages. When a message is received, the
service will deliver it to your application via HTTP request as
well.

Tropo
-----

For this example we'll use `Tropo`_. There's a `Tropo RapidSMS backend`_ we
can use, and if you're in the United States, you can get a free developer
account that includes a phone number and enough free messages to try out
the service. Tropo also has service in the rest of North America and
western Europe, though the free developer account is not available.
If you're outside Tropo's service area, you'll have to use another
provider, but hopefully this tutorial will still show you the basics
of how it works.

Get an account
--------------

To create a Tropo account, go to https://www.tropo.com/account/register.jsp
and fill in the form.

Install the backend
-------------------

Add the Tropo RapidSMS backend to your requirements by editing
``requirements/base.txt``:

.. code-block:: text
    :emphasize-lines: 4

    Django>=1.5,<1.6
    RapidSMS==0.14.0
    South==0.7.6
    rapidsms-tropo==0.1.1

Then use pip to install it:

.. code-block:: console

    $ pip install -r requirements/base.txt

That will pull in a few dependencies of rapidsms-tropo.

.. _Tropo: https://www.tropo.com/
.. _Tropo RapidSMS backend: https://pypi.python.org/pypi/rapidsms-tropo/
