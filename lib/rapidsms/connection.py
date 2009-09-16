#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


#from django.db import models


class Connection(object):
    """
    The connection class pairs a backend with an individual identity unique to
    that backend (eg. a phone number, email address, irc nickname), so RapidSMS
    app developers need not concern themselves with backends.
    """

    def __init__(self, backend, identity):
        self.backend = backend
        self.identity = identity
