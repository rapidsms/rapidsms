#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models


class Backend(models.Model):
    """
    This model isn't really a backend. Those are regular Python classes, in
    rapidsms/backends/*. This is just a stub model to provide a primary key for
    each running backend, so other models can be linked to it with ForeignKeys.
    """

    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s: %s via %s>' %\
            (type(self).__name__, self.slug)


class Connection(models.Model):
    """
    The connection model pairs a backend with an individual identity unique to
    that backend (eg. a phone number, email address, irc nickname), so RapidSMS
    app developers need not concern themselves with backends.
    """

    backend  = models.ForeignKey(Backend)
    identity = models.CharField(max_length=100)
