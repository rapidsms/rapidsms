#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from django.db import models
from django.utils.safestring import SafeString
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from rapidsms.models import ExtensibleModelBase


class Point(models.Model):
    """
    This model represents an anonymous point on the globe. It should be
    replaced with something from GeoDjango soon, but I can't seem to get
    Spatialite to build right now...
    """

    latitude  = models.DecimalField(max_digits=13, decimal_places=10)
    longitude = models.DecimalField(max_digits=13, decimal_places=10)

    def __unicode__(self):
        return "%s, %s" % (self.latitude, self.longitude)

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self)


class Location(models.Model):
    """
    This model represents a named point on the globe. It is deliberately
    spartan, so more specific apps can extend it with their own fields
    and relationships without clashing with built-in functionality.
    """

    __metaclass__ = ExtensibleModelBase

    point = models.ForeignKey(Point, null=True, blank=True)

    parent_type = models.ForeignKey(ContentType, null=True, blank=True)
    parent_id   = models.PositiveIntegerField(null=True, blank=True)
    parent      = generic.GenericForeignKey("parent_type", "parent_id")

    class Meta:
        abstract = True

    def __unicode__(self):
        """
        """
        
        return getattr(self, "name", "#%d" % self.pk)

    @property
    def uid(self):
        """
        Return a unique ID for this location, suitable for embedding in
        URLs. The primary key is insufficient, because the name of the
        model must also be included.

        This method (and ``get_for_uid`` will go away, once the ``slug``
        field is validated as unique across all Location subclasses.
        """

        return "%s:%d" % (self.content_type, self.pk)

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self).model

    @staticmethod
    def get_for_uid(uid):
        """
        Return the object (an instance of a subclass of Location) named
        by ``uid``. The UID should be in the form ``model:id``, as
        returned by the Location.uid property.
        """

        model, pk = uid.split(":")
        type = ContentType.objects.get(model=model)
        return type.get_object_for_this_type(pk=pk)

    @staticmethod
    def subclasses():
        """
        Return a list of all known subclasses of Location.
        """

        return [
            cls
            for cls in models.loading.get_models()
            if issubclass(cls, Location) and\
                (cls is not Location)]

    @property
    def path(self):
        next = self
        locations = []

        while next is not None:
            locations.insert(0, next)
            next = next.parent

        return locations

    def as_html(self):
        """
        """

        return SafeString(self.label)

    @property
    def label(self):
        """
        Return an HTML fragment, for embedding in a Google map. This
        method should be overridden by subclasses wishing to provide
        better contextual information.
        """

        return unicode(self)


#class Country(Location):
#    name = models.CharField(max_length=100)
#    iso_code = models.CharField("ISO Code", max_length=2)

#    class Meta:
#        verbose_name_plural = "countries"

#    @property
#    def label(self):
#        return self.iso_code.upper()


#class State(Location):
#    name = models.CharField(max_length=100)
#    usps_code = models.CharField("USPS Code", max_length=2,
#        help_text="The two-letter state abbreviation")

#    @property
#    def label(self):
#        return self.usps_code.upper()


#class City(Location):
#    name = models.CharField(max_length=100)

#    class Meta:
#        verbose_name_plural = "cities"
