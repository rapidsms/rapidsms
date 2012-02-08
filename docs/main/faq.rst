Is RapidSMS an application I can download and install?
=======================================================

No. RapidSMS is a software framework designed to be used by software developers to build custom applications. If you are looking for a simple application you can download and install we highly recommend FrontlineSMS.

Is it possible to connect multiple modems to a RapidSMS instance?
==================================================================

Yes. A use case would be you wanted to connect to two different GSM networks, say Zain and MTN. RapidSMS would see multiple modems as multiple backends and treat them the same.

In your settings.py file, under the `INSTALLED_BACKENDS` section, list the backends with a unique name, the backend engine (type, ie. gsm, http) and port.::

    "Zain": {
        "ENGINE": "rapidsms.backends.gsm",
        "PORT": "/dev/ttyUSB0"
    },
    "MTN": {
        "ENGINE": "rapidsms.backends.gsm,
        "PORT": "/dev/ttyUSB1"
    },


What if RapidSMS is not installed on the same system as the GSM device?
========================================================================

One possible solution to this use case it to use the `Kannel gateway <http://kannel.org>`_ on the machine which hosts the modem(s) and use the `Kannel backend <http://gist.github.com/214985>`_ on the RapidSMS server.

Which modems are known to be compatible with RapidSMS?
=======================================================

The most often used GSM modem is the MultiTech MTCBA-G-F4. You can browse a list of modems known to work with RapidSMS on the pygsm Wiki.

or look at the :doc:`Modem Configs <../configuration/modem-configs>` page.

Is it possible to install RapidSMS on Windows?
================================================

RapidSMS can run on Linux, Windows and Mac OS X operating systems. However, it has been tested the most on Linux and much the documentation is written for Ubuntu Linux. Therefore we recommend using Linux. See :doc:`Windows <../installation/windows>` for Windows installation instructions.

How can I send and receive messages with RapidSMS?
===================================================

Sending and Receiving messages: The Router's phases

RapidSMS's router is a middleman who sits between RapidSMS apps and backends. Since the router passes messages from apps to backends, and vice-versa, app authors don't need to worry about which backends are running.

Whenever a message is received (via any backend), the router initiates the incoming phases by calling the following methods in each running app.

Incoming phases

parse
------

The parse phase is provided to allow all apps a chance to view each incoming message. Apps may add additional metadata to the message object, trigger application logic, or even modify the message text.

handle
-------

The handle phase is provided to allow a single app to 'handle' a particular message. Unlike the parse phase, every app's handle method may not be called for each incoming message. If an app returns True (or anything, really), the handle phase is 'short-circuited' and the router moves on to the next phase. So, the router calls each app's handle method until one of them returns True -- any remaining apps do not experience a handle phase for this message. The handle phase is intended to provide a way for several apps to be deployed simultaneously so that any app can, for example, respond to a message and stop other apps from also responding.

cleanup
--------

The cleanup phase is provided so that all apps may perform logic at the end of an incoming message's lifecycle -- after any apps have parsed, saved, analyzed, or responded to the message.

Outgoing phases

outgoing
---------

The outgoing phase is provided to allow every app to view, modify, or halt each message originating from a RapidSMS app. For example, the logger app saves each outgoing message to a database, and the censor can be configured to prevent apps from sending messages which contain profanity.

Originating messages

There are several ways to originate an outgoing message from an app (rather than responding to an incoming message).

To send a message via a particular backend (where backend.slug is 'gsm')::

    my_backend = self.router.get_backend('gsm')
    my_backend.message('123456789', 'Hello world').send()

Or::

    my_connection = Connection('123456789', my_backend)
    Message(my_connection, 'Hello again').send()

Or::

    self.router.outgoing(my_connection, 'Hello once more')

To send a message to a known Reporter (where reporter.alias is 'foo')::

    my_reporter = Reporter.objects.get(alias='foo')
    my_reporter.send(self.router, 'Hello foo')

Outgoing messages can also be originated from the web interface, by using the ajax app. See `apps/ajax/app.py` for usage information.

How can I send messages from the web interface?
================================================
TODO

What is the License for RapidSMS?
==================================

RapidSMS is licensed under BSD. See more about the RapidSMS :doc:`License <../misc/license>`.