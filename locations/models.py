#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from django.db import models
from rapidsms.models import ExtensibleModelBase


class LocationType(models.Model):
    """
    This model allows Locations to be organized into a hierachy, via the
    mutually recursive *LocationType.exists_in* and *Location.type*
    fields. Multiple LocationTypes of the same name (eg. City, County)
    may exist within separate Locations. This looks something like:

                                                        +---------+
                                                     /->| Arizona |
                      +---------------+  /--------\  |  +---------+
                   /->| United States |->| States |--+->| Alabama |
                   |  +---------------+  \--------/  |  +---------+
                   |                                 \->| Alaska  |
    /-----------\  |                                    +---------+
    | Countries |--+
    \-----------/  |                                +-----------------+
                   |                             /->| Bedfordshire    |
                   |  +---------+  /----------\  |  +-----------------+
                   \->| England |->| Counties |--+->| Berkshire       |
                      +---------+  \----------/  |  +-----------------+
                                                 \->| Buckinghamshire |
                                                    +-----------------+

    It should be obvious to all inhabitants of Planet Earth which boxes
    are Locations, and which are LocationTypes. Although it is not shown
    here, multiple LocationTypes may be linked to a single Location, to
    represent more complex or incomplete hierarchies.
    """

    # django doesn't like to automatically pluralize things (and neither
    # do i), but it's not a _huge_ inconvenience to provide them both,
    # since the names of LocationTypes rarely change
    singular = models.CharField(max_length=100)
    plural   = models.CharField(max_length=100)

    slug = models.CharField(max_length=30, unique=True,
        help_text="An URL-safe alternative to the <em>plural</em> field.")
                  

    exists_in = models.ForeignKey("Location", null=True, blank=True,
        help_text='The Location which this LocationType exists within. For '
                  'example, "states" may exist within "The United States", '
                  'and "counties" may exist within "England".')


    class Meta:
        verbose_name = "Type"


    def __unicode__(self):
        return self.singular

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self)

    
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


class LocationBase(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=30, unique=True,
                            help_text = "A unique identifier that will be lowercased going into the database.")
    type = models.ForeignKey(LocationType)
    point = models.ForeignKey(Point, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)

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
            next = next.type.exists_in

        return locations

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


class Location(LocationBase):
    """
    This model represents a named point on the globe. It is deliberately
    spartan, so more specific apps can extend it with their own fields
    and relationships without clashing with built-in functionality.

    Note that there is no *parent* field. Since each LocationType exists
    within a single Location (ie, cities in the USA are distinct from
    cities in the UK), the hierachy of Locations can be derrived by the
    hierachy of types. An explicit Location parent would be ambiguous.
    """

    __metaclass__ = ExtensibleModelBase
