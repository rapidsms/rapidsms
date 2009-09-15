#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from django.db import models
from rapidsms.djangoproject.managers import *
from reporters.models import Reporter


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


class LocationType(models.Model):

    # django doesn't like to automatically pluralize things
    # (and neither do i), but it's not a _huge_ inconvenience
    # to provide them both, since LocationTypes rarely change
    singular = models.CharField(max_length=100, unique=True)
    plural   = models.CharField(max_length=100, unique=True)

    slug = models.CharField(max_length=100, unique=True,
        help_text="An URL-safe alternative to the <em>plural</em> field.")

    # require a marker to be chosen, so the types
    # don't all end up the same color on the maps
    marker = models.CharField(max_length=10, choices=MARKER_CHOICES)

    # some types of locations (like countries) only
    # exist to contain other locations, not to actually
    # link things to. we don't enforce this in the db,
    # but can use it as a hint to improve the interface
    is_linkable = models.BooleanField(
        help_text="Allows other models from being linked to this model " +\
                  "in the WebUI. Has no effect in the Django admin.")

    # make this recursive, to provide hints on how
    # to display the linked locations in the webui
    # (eg: in a deployment with Planet -> Country -> State LocationTypes, we
    # can assume that a Location being created within a Country will be a State)
    objects = RecursiveManager()
    parent = models.ForeignKey("LocationType", related_name="children", null=True, blank=True,
        help_text="The parent of this LocationType. Provides a structure " +\
                  "for linked Locations in the WebUI. Has no effect " +\
                  "in the Django admin.")


    class Meta:
        verbose_name = "Type"

    def __unicode__(self):
        return self.title


    class ManyLocationTypesStub(object):
        """This class only exists to serve the LocationType.label method, which
           usually returns a single LocationType, which is embedded into a
           template where a description is required -- but sometimes, we have
           to be generic. This little stub allows us to do so (by using, for
           example, {{ location_type.plural }}, without worrying about whether
           it will output "OTPs", "States", or just "Locations"). This is an
           object, rather than a dict, so the attrs can be accessed just like
           Django model fields would."""

        def __init__(self):
            self.singular = "Location"
            self.plural   = "Locations"


    @classmethod
    def label(cls, only_linkable=False):
        """Since most LocationType hierarchies only allow reports to be
           linked to the lowest-level Locations, and many deployments don't
           evan _have_ a LoctionType hierarchy (only a single LocationType),
           we can sometimes do a lot better than "Location" as a label for
           fields to select a linkable Location."""

        # fetch all relevant LocationTypes
        if not only_linkable: objects = cls.objects.all()
        else: objects = cls.objects.filter(is_linkable=1)

        # if there's only one, we can use its title.
        # otherwise, we'll just have to be generic
        return objects[0] if len(objects) == 1 else cls.ManyLocationTypesStub()


    @property
    def title(self):
        """Returns the singular form of this LocationType.
           This is only here for consistency, because most
           models have a "title" field."""
        return self.singular


class Location(models.Model):
    """A Location is technically a geopgraphical point (lat+long), but is often
       used to represent a large area such as a city or state. It is recursive
       via the _parent_ field, which can be used to create a hierachy (Country
       -> State -> County -> City) in combination with the _type_ field."""

    objects = RecursiveManager()
    type = models.ForeignKey(LocationType, related_name="locations", blank=True, null=True)
    name = models.CharField(max_length=100, help_text="Name of location")
    code = models.CharField(max_length=30, unique=True)

    parent = models.ForeignKey("Location", related_name="children", null=True, blank=True,
        help_text="The parent of this Location. Although it is not enforced, it" +\
                  "is expected that the parent will be of a different LocationType")

    latitude  = models.DecimalField(max_digits=13, decimal_places=10, blank=True, null=True, help_text="The physical latitude of this location")
    longitude = models.DecimalField(max_digits=13, decimal_places=10, blank=True, null=True, help_text="The physical longitude of this location")


    # this belongs in Meta, but Django won't
    # let us put _unapproved_ things there
    followable = True


    def __unicode__(self):
        return self.name


    # see the FOLLOW app, for now,
    # although this will be expanded
    @classmethod
    def __search__(cls, terms):

        # if we're searching for a single term, it
        # could be a location code, so try that first
        if len(terms) == 1:
            try:
                return cls.objects.get(
                    code__iexact=terms[0])

            # no matter if it didn't work.
            # it could still be a name
            except cls.DoesNotExist:
                pass

        # re-join the terms into a single string, and search
        # for a location with this name (we wont't worry about
        # other delimiters for now, but might need to come back)
        try:
            return cls.objects.get(
                name__iexact=" ".join(terms))

        # if this doesn't work, the terms
        # are not a valid location name
        except (cls.DoesNotExist, cls.MultipleObjectsReturned):
            return None


    def save(self, *args, **kwargs):

        # override the default save behavior, to remove extra spaces from
        # the _name_ property. It's not important enough to bother the end-
        # user with, but self.__search__ assumes that a single space is the
        # only delimiter -- so we just do it here, transparently.
        self.name = re.sub(r"\s+", " ", self.name)

        # then save the model as usual
        models.Model.save(self, *args, **kwargs)


    # TODO: how can we port the Location.contacts and Location.one_contact
    #       methods, now that the locations app has been split from reporters?
    #       even if they can import one another, they can't know if they're
    #       both running at parse time, and can't monkey-patch later.

    def ancestors(self, include_self=False):
        """Returns all of the parent locations of this location,
           optionally including itself in the output. This is
           very inefficient, so consider caching the output."""
        locs = [self] if include_self else []
        loc = self

        # keep on iterating
        # until we return
        while True:
            locs.append(loc)
            loc = loc.parent

            # are we at the top?
            if loc is None:
                return locs


    def descendants(self, include_self=False):
        """Returns all of the locations which are descended from this location,
           optionally including itself in the output. This is very inefficient
           (it recurses once for EACH), so consider caching the output."""
        locs = [self] if include_self else []

        for loc in self.children.all():
            locs.extend(loc.descendants(True))

        return locs


class ReporterLocation(models.Model):
    """This model is kind of a hack, to add a _location_ field
       to the Reporter class without extending it -- in the same
       way that the Django docs recommend creating a UserProfile
       rather than patching User."""

    reporter = models.OneToOneField(Reporter)
    location = models.ForeignKey(Location)
    location.rel.verbose_name = "Reporters"
