#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.db import models


DIRECTION_CHOICES = (
    ("I", "Incoming"),
    ("O", "Outgoing"))


class HttpTesterMessage(models.Model):
    direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES)
    identity = models.CharField(max_length=100)
    text = models.TextField()
