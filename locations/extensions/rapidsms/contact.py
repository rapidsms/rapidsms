#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models


class ContactLocation(models.Model):
    location = models.ForeignKey('locations.Location', null=True, blank=True, help_text=
        "The location which this Contact last reported from.")

    class Meta:
        abstract = True
