#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from rapidsms.webui.managers import *


class LocationType(models.Model):
    name = models.CharField(max_length=100)
    
    
    class Meta:
        verbose_name = "Type"
    
    def __unicode__(self):
        return self.name


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
    
    latitude  = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True, help_text="The physical latitude of this location")
    longitude = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True, help_text="The physical longitude of this location")
    
    
    def __unicode__(self):
        return self.name
    
    
    # TODO: how can we port the Location.contacts and Location.one_contact
    #       methods, now that the locations app has been split from reporters?
    #       even if they can import one another, they can't know if they're
    #       both running at parse time, and can't monkey-patch later.
    def one_contact(self, role, display=False):
        return "Mr. Fixme"

    def contacts(self, role=None):
        return Location.objects.get(pk=2)
    
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
