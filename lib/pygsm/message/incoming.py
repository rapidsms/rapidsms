#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import datetime
import pytz


class IncomingMessage(object):
    def __init__(self, device, sender, sent, text):

        # move the arguments into "private" attrs,
        # to try to prevent from from being modified
        self._device = device
        self._sender = sender
        self._sent   = sent
        self._text   = text

        # assume that the message was
        # received right now, since we
        # don't have an incoming buffer
        self._received = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


    def __repr__(self):
        return "<pygsm.IncomingMessage from %s: %r>" %\
            (self.sender, self.text)


    def respond(self, text):
        """Responds to this IncomingMessage by sending a message containing
           _text_ back to the sender via the modem that created this object."""
        return self.device.send_sms(self.sender, text)


    @property
    def device(self):
        """Returns the pygsm.GsmModem device which received
           the SMS, and created this IncomingMessage object."""
        return self._device

    @property
    def sender(self):
        """Returns the phone number of the originator of this IncomingMessage.
           It is stored directly as reported by the modem, so no assumptions
           can be made about it's format."""
        return self._sender

    @property
    def sent(self):
        """Returns a datetime object containing the date and time that this
           IncomingMessage was sent, as reported by the modem. Sometimes, a
           network or modem will not report this field, so it will be None."""
        return self._sent

    @property
    def text(self):
        """Returns the text contents of this IncomingMessage. It will usually
           be 160 characters or less, by virtue of being an SMS, but multipart
           messages can, technically, be up to 39015 characters long."""
        return self._text

    @property
    def received(self):
        """Returns a datetime object containing the date and time that this
           IncomingMessage was created, which is a close aproximation of when
           the SMS was received."""
        return self._received
