#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from rapidsms.models import ExtensibleModelBase


class LocationTypeStub(object):
    """
    This is not a model. It's just a regular class which looks like a
    model, to support the old interface. It will go away soon.
    """

    def __init__(self, model):
        self.model = model

    def __unicode__(self):
        return unicode(self.plural)

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self.model.__name__)

    @property
    def singular(self):
        return self.model._meta.verbose_name

    @property
    def plural(self):
        return self.model._meta.verbose_name_plural

    @property
    def slug(self):
        return self.singular.lower()

    def get_children(self):
        pass


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

    name  = models.CharField(max_length=100)
    slug  = models.CharField(max_length=30)
    point = models.ForeignKey(Point, null=True, blank=True)

    parent_type = models.ForeignKey(ContentType, null=True, blank=True)
    parent_id   = models.PositiveIntegerField(null=True, blank=True)
    parent      = generic.GenericForeignKey("parent_type", "parent_id")

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self)
    
    @property
    def path(self):
        next = self
        locations = []

        while next is not None:
            locations.insert(0, next)
            next = next.parent

        return locations

    @property
    def type_slug(self):
        return ContentType.objects.get_for_model(self).model

    @property
    def full_name(self):
        """
        Return the full-qualified name of this Location, including all
        of its ancestors. Ideal for displaying in the Django admin.
        """

        def _code(location):
            return location.slug or\
                ("#%d" % location.pk)

        return "/".join(map(_code, self.path))

    @property
    def label(self):
        """
        Return an HTML fragment, for embedding in a Google map. This
        method should be overridden by subclasses wishing to provide
        better contextual information.
        """

        return self.slug.upper()

    def save(self, *args, **kwargs):

        # remove any superfluous spaces from the _name_. it would be a
        # huge bother to require the user to do it manually, but the
        # __search__ method assumes that a single space is the only
        # delimiter, so we'll do it here transparently.
        self.name = re.sub(r"\s+", " ", self.name)

        # do some processing on the slug field to ensure we only store 
        # lowercase and strip spaces
        self.slug = self.slug.lower().strip()
        
        # then save the model as usual
        models.Model.save(self, *args, **kwargs)
