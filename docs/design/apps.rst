RapidSMS Applications
=======================

Creating new SMS functionality can be done in a few simple steps:

* create a model which inherits from rapidsms.apps.base.AppBase
* save it as yourapplicationname/apps.py
* add it to your INSTALLED_APPS list in settings.py.

The most basic app could look like::

    from rapidsms.apps.base import AppBase
 
    class App(AppBase):
        def handle(self, message):
            message.respond("hello world")


Notice that in the above example, only the 'handle' phase is implemented. RapidSMS apps can (but don't have to) implement 6 phases:

filter
-------

The first phase, before any actual work is done. This is the only phase that can entirely abort further processing of the incoming message, which it does by returning True.

e.g. a filter to kill spam messages

parse
-------

Typically used to modify all messages in a way which is globally useful. Each apps parse phase will see all incoming messages that were not filtered. Don't do INSERTs or UPDATEs in here!

e.g. an app which adds metadata about phone number registration to each message

handle
--------

Respond to messages here.

The router will pass incoming messages through each apps 'handle' phase until one of them returns true. All subsequent apps will never see the message. Note that RapidSMS provides no guarantee of ordering.

e.g. an interactive poll

default
--------

Only called if no apps returned true during the Handle phase.

cleanup
-----------

An opportunity to clean up anything started during earlier phases.

outgoing
----------

Processes all outgoing messages.
