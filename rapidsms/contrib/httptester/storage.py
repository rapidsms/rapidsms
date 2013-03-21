#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

""" Store and get messages from cache """

from rapidsms.backends.db.models import INCOMING, BackendMessage


def get_messages():
    """Return a queryset with the message data"""
    return BackendMessage.objects.all()


def store_message(direction, identity, text):
    """

    :param direction: "in" or "out" depending on whether the message
       was sent to (into) RapidSMS, or out of RapidSMS.
    :param identity: Phone number the message was sent from (in)
       or to (out)
    :param text: The message
    """
    BackendMessage.objects.create(direction=direction, identity=identity,
                                  text=text)


def store_and_queue(backend_name, identity, text):
    """Store a message in our log and send it into RapidSMS.

    :param backend_name:
    :param identity: Phone number the message will appear to come from
    :param text: The message
    """
    from rapidsms.router import receive, lookup_connections
    store_message(INCOMING, identity, text)
    connection = lookup_connections(backend_name, [identity])[0]
    receive(text, connection)


def clear_messages(identity):
    """Forget messages to/from this identity

    :param identity: The phone number whose messages will be cleared
    """
    BackendMessage.objects.filter(identity=identity).delete()


def clear_all_messages():
    """Forget all messages"""
    BackendMessage.objects.all().delete()
