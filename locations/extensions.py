#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from django.db import models
from rapidsms.models import extends
from .models import LocationType, Location


@extends("rapidsms.Contact")
class PersonLocation(models.Model):
    location = models.ForeignKey(Location, null=True, blank=True)

    class Meta:
        abstract = True


from django.conf import settings
if "messaging" in settings.INSTALLED_APPS:

    from messaging import filters
    filters.register(LocationType.messaging_filters)
