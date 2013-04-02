#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.db import models


INCOMING = 'I'
OUTGOING = 'O'

DIRECTION_CHOICES = (
    (INCOMING, "Incoming"),
    (OUTGOING, "Outgoing"),
)


class BackendMessage(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES,
                                 db_index=True)
    message_id = models.CharField(max_length=64)
    external_id = models.CharField(max_length=64, blank=True)
    identity = models.CharField(max_length=100)
    text = models.TextField()

    def __unicode__(self):
        return self.text[:60]
