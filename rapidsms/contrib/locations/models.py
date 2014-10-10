#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from django.utils.html import escape
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from rapidsms.models import ExtensibleModelBase


class Point(models.Model):
    """
    This model represents an anonymous point on the globe. It should be
    replaced with something from GeoDjango soon, but I can't seem to get
    Spatialite to build right now...
    """

    latitude = models.DecimalField(max_digits=13, decimal_places=10)
    longitude = models.DecimalField(max_digits=13, decimal_places=10)

    def __unicode__(self):
        return "%s, %s" % (self.latitude, self.longitude)

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self)


class LocationType(models.Model):
    """
    This model represents the 'type' of Location, as an option for a
    simpler way of having a location heirarchy without having different
    classes for each location type (as is supported by the generic
    relation to parent).
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, primary_key=True)

    def __unicode__(self):
        return self.name


class Location(models.Model):
    """
    This model represents a named point on the globe. It is deliberately
    spartan, so more specific apps can extend it with their own fields
    and relationships without clashing with built-in functionality.
    """

    __metaclass__ = ExtensibleModelBase
    point = models.ForeignKey(Point, null=True, blank=True)
    type = models.ForeignKey(LocationType, related_name="locations",
                             blank=True, null=True)
    parent_type = models.ForeignKey(ContentType, null=True, blank=True)
    parent_id = models.PositiveIntegerField(null=True, blank=True)
    parent = generic.GenericForeignKey("parent_type", "parent_id")

    # choices for the Location.direction method.
    # (values stolen from label-overlay.js)
    class Direction:
        CENTER = "center"
        ABOVE = "above"
        RIGHT = "right"
        BELOW = "below"
        LEFT = "left"

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
            if issubclass(cls, Location) and (cls is not Location)
        ]

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
        Return the HTML fragment to be embedded in the map. This method
        should be overridden by subclasses wishing to fully customize
        the the rendering of their instance in the map.

        The output of this method is not escaped before being included
        in the template, so be careful to escape it yourself.
        """

        return escape(self.label)

    @property
    def label(self):
        """
        Return the caption for this Location, to be embedded in the
        map. This method should be overridden by subclasses wishing to
        provide better contextual information.

        The output of this method is included in the template as-is, so
        is HTML-escaped by default. If you wish to customize the HTML,
        override the ``as_html`` method, instead.
        """

        return unicode(self)

    @property
    def css_class(self):
        """
        Return the CSS class name of the label overlay. This method
        should be overriden by subclasses wishing to customize the
        appearance of the embedded HTML fragment.
        """

        return "bubble"

    @property
    def direction(self):
        """
        Return the direction which the embedded HTML fragment should be
        offset from the anchor point. Return one of Location.Direction.
        """

        return self.Direction.ABOVE


# class Country(Location):
#    name = models.CharField(max_length=100)
#    iso_code = models.CharField("ISO Code", max_length=2)

#    class Meta:
#        verbose_name_plural = "countries"

#    @property
#    def label(self):
#        return self.iso_code.upper()


# class State(Location):
#    name = models.CharField(max_length=100)
#    usps_code = models.CharField("USPS Code", max_length=2,
#        help_text="The two-letter state abbreviation")

#    @property
#    def label(self):
#        return self.usps_code.upper()


# class City(Location):
#    name = models.CharField(max_length=100)

#    class Meta:
#        verbose_name_plural = "cities"
