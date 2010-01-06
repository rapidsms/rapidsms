#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from django.db import models
from rapidsms.models import extends
from .models import Location


@extends("rapidsms.Contact")
class PersonLocation(models.Model):
    location = models.ForeignKey(Location, null=True, blank=True)

    class Meta:
        abstract = True
