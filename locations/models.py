#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from django.db import models
from rapidsms.models import Extensible


MARKER_CHOICES = (
    ("0",       "Red"),
    ("1",    "Orange"),
    ("2",    "Yellow"),
    ("3",     "Green"),
    ("4", "Turquoise"),
    ("5",      "Cyan"),
    ("6",      "Blue"),
    ("7",    "Indigo"),
    ("8",    "Purple"),
    ("9",      "Pink"))


# see the following url for gmap/bing/yahoo conversion ratios:
#   http://code.davidjanes.com/blog/2008/11/08/switching-between-mapping
#   -apis-and-universal-map-levels/
ZOOM_CHOICES = (
    ("-19", "19"),
    ("-18", "18"),
    ("-17", "17 (block)"),
    ("-16", "16"),
    ("-15", "15"),
    ("-14", "14"),
    ("-13", "13 (city)"),
    ("-12", "12"),
    ("-11", "11"),
    ("-10", "10"),
    ("-9",  "9"),
    ("-8",  "8"),
    ("-7",  "7 (state)"),
    ("-6",  "6"),
    ("-5",  "5"),
    ("-4",  "4"),
    ("-3",  "3"),
    ("-2",  "2"),
    ("-1",  "1 (space)"),
    ("0",   "0 (always)"))


class LocationType(models.Model):
    """
    This model allows Locations to be organized into a hierachy, via the
    mutually recursive *LocationType.exists_in* and *Location.type*
    fields. Multiple LocationTypes of the same name (eg. City, County)
    may exist within separate Locations.This looks something like:

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

    slug = models.CharField(max_length=100,
        help_text="An URL-safe alternative to the <em>plural</em> field.")

    exists_in = models.ForeignKey("Location", null=True, blank=True,
        help_text='The Location which this LocationType exists within. For '
                  'example, "states" may exist within "The United States", '
                  'and "counties" may exist within "England".')

    visible_at_zoom_level = models.IntegerField(blank=True, choices=ZOOM_CHOICES,
        help_text="The zoom level (in David Janes' Universal Zoom Levels) "
                  "at which Locations of this LocationType become visible.")

    # require a marker to be chosen, so the types don't all end up the
    # same color on the maps
    marker = models.CharField(max_length=10, choices=MARKER_CHOICES)


    class Meta:
        verbose_name = "Type"


    def __unicode__(self):
        return self.singular


class Location(models.Model):
    """
    This model represents a named point on the globe. It is deliberately
    spartan, so more specific apps can extend it with their own fields
    and relationships without clashing with built-in functionality.

    Note that there is no *parent* field. Since each LocationType exists
    within a single Location (ie, cities in the USA are distinct from
    cities in the UK), the hierachy of Locations can be derrived by the
    hierachy of types. An explicit Location parent would be ambiguous.
    """

    __metaclass__ = Extensible

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30)
    type = models.ForeignKey(LocationType)

    latitude  = models.DecimalField(max_digits=13, decimal_places=10, blank=True, null=True, help_text="The physical latitude of this location")
    longitude = models.DecimalField(max_digits=13, decimal_places=10, blank=True, null=True, help_text="The physical longitude of this location")


    def __unicode__(self):
        return self.name


    def full_name(self):
        """
        Return the full-qualified name of this Location, including all
        of its ancestors. Ideal for displaying in the Django admin.
        """

        def _code(location):
            return location.code or\
                ("#%d" % location.pk)

        next = self
        locations = []

        while next is not None:
            locations.insert(0, _code(next))
            next = next.type.exists_in

        return "/".join(locations)


    def save(self, *args, **kwargs):

        # remove any superfluous spaces from the _name_. it would be a
        # huge bother to require the user to do it manually, but the
        # __search__ method assumes that a single space is the only
        # delimiter, so we'll do it here transparently.
        self.name = re.sub(r"\s+", " ", self.name)

        # then save the model as usual
        models.Model.save(self, *args, **kwargs)
