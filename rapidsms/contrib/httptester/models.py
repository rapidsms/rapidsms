#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.db import models


DIRECTION_CHOICES = (
    ("in", "Incoming"),
    ("out", "Outgoing"))


class HttpTesterMessage(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES)
    identity = models.CharField(max_length=100)
    text = models.TextField()

    class Meta(object):
        ordering = ['date', 'id']
