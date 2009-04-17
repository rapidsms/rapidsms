#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os, re
from datetime import datetime
from django.db import models

from apps.modelrelationship.models import *

# load the rapidsms configuration, for BackendManager
# to check which backends are currently running
from rapidsms.config import Config
conf = Config(os.environ["RAPIDSMS_INI"])



class Role(models.Model):
    """Basic representation of a role that someone can have.  For example,
       'supervisor' or 'data entry clerk'"""
    name = models.CharField(max_length=160)
    code = models.CharField(max_length=20, blank=True, null=True,\
        help_text="Abbreviation")
    
    def __unicode__(self):
        return self.name

class LocationType(models.Model):
    """A type of location.  For example 'School' or 'Factory'"""
    name = models.CharField(max_length=160,help_text="Name of location type")
        
    def __unicode__(self):
        return self.name
    

class Location(models.Model):
    """A location.  Locations have a name, an optional type, and optional geographic information."""
    name = models.CharField(max_length=160, help_text="Name of location")
    type = models.ForeignKey(LocationType, blank=True, null=True, help_text="Type of location")
    code = models.CharField(max_length=15)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True, help_text="The physical latitude of this location")
    longitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True, help_text="The physical longitude of this location")
    
    # the parent property.  currently handled by model-relationship 
    # and and the django signal framework below.
    _parent = None
    def _get_parent(self):
        return self._parent
    def _set_parent(self, parent):
        self._parent = parent
    
    parent = property(_get_parent, _set_parent, None, None)

    def __unicode__(self):
        return self.name
    
# location signals for saving the parent type  
def loc_post_save(sender, **kwargs):
    """Location post save signal that updates model-relationship with
       the parent/child hierarchy."""
    # created = kwargs["created"]
    instance = kwargs["instance"]
    if instance.parent:
        type = _get_location_parent_edge_type()
        if type:
            try:
                # if the edge already exists, update it
                edge = Edge.objects.get(relationship=type, child_id=instance.id)
                edge.parent_object = instance.parent
                edge.save()
            except Edge.DoesNotExist:
                # otherwise create a new one
                edge = Edge(relationship=type, child_object=instance, parent_object=instance.parent)
                edge.save()

# this registers the signal so it's called every time we save locations
models.signals.post_save.connect(loc_post_save, sender=Location)

def loc_post_init(sender, **kwargs):
    """Location post init signal that reads the parent from model-relationship 
       if it is defined"""
    instance = kwargs["instance"]
    
    type = _get_location_parent_edge_type()
    if type:
        try:
            edge = Edge.objects.get(relationship=type, child_id=instance.id)
            instance.parent = edge.parent_object
        except Edge.DoesNotExist:
            # no parent was set, not a problem
            pass

models.signals.post_init.connect(loc_post_init, sender=Location)

def _get_location_parent_edge_type():
    content_type = ContentType.objects.get(name="location")
    # there is an implicit dependency on this name (Location Parent) being defined
    # as an edge between locations.  This will be done with fixtures
    types = EdgeType.objects.all().filter(name="Location Parent").filter(parent_type=content_type).filter(child_type=content_type)
    # this is dumb for now.  if we have more than one of these edge types, or none,
    # we won't get anything back
    if len(types) == 1:
        return types[0]
    return None

class Reporter(models.Model):
    """This model represents a KNOWN person, that can be identified via
       their alias and/or connection(s). Unlike the RapidSMS Person class,
       it should not be used to represent unknown reporters, since that
       could lead to multiple objects for the same "person". Usually, this
       model should be created through the WebUI, in advance of the reporter
       using the system - but there are always exceptions to these rules..."""
    alias      = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name  = models.CharField(max_length=30, blank=True)
    password   = models.CharField(max_length=30, blank=True)
    location = models.ForeignKey("Location", null=True, blank=True)
    role = models.ForeignKey("Role", null=True, blank=True)

    def __unicode__(self):
            return self.connection.identity
        

    # the language that this reporter prefers to
    # receive their messages in, as a w3c language tag
    #
    # the spec:   http://www.w3.org/International/articles/language-tags/Overview.en.php
    # reference:  http://www.iana.org/assignments/language-subtag-registry
    #
    # to summarize:
    #   english  = en
    #   amharic  = am
    #   chichewa = ny
    #   klingon  = tlh
    #
    language = models.CharField(max_length=10)
	
    # although it's impossible to enforce, if a user registers
    # themself (via the app.py backend), this flag should be set
    # indicate that they probably shouldn't be trusted
    registered_self = models.BooleanField()
	
	
    class Meta:
        ordering = ["last_name", "first_name"]
    
    
    def full_name(self):
        return ("%s %s" % (
            self.first_name,
            self.last_name)).strip()
    
    def __unicode__(self):
        return self.full_name()
    
    def __repr__(self):
        return "%s (%s)" % (
            self.full_name(),
            self.alias)
    
    
    @classmethod
    def parse_name(klass, flat_name):
        """Given a single string, this function returns a three-string
           tuple containing a suggested alias, first name, and last name,
           via some quite crude pattern matching."""
        
        patterns = [
            # try a few common name formats.
            # this is crappy but sufficient
            r"([a-z]+)",                       # Adam
            r"([a-z]+)\s+([a-z]+)",            # Evan Wheeler
            r"([a-z]+)\s+[a-z]\.?\s+([a-z]+)", # Mark E. Johnston
            r"([a-z]+)\s+([a-z]+\-[a-z]+)"     # Erica Kochi-Fabian
        ]
        
        # try each pattern, returning as
        # soon as we find something that fits
        for pat in patterns:
            m = re.match("^%s$" % pat, flat_name, re.IGNORECASE)
            print (("^%s$" % pat) + " vs. %s" % flat_name)
            
            if m is not None:
                g = m.groups()
                
                # return single names as-is
                # they might already be aliases
                if len(g) == 1:
                    alias = g[0].lower()
                    return (alias, g[0], g[1])
                    
                else:
                    # return only the letters from
                    # the first and last names
                    alias = g[0][0] + re.sub(r"[^a-zA-Z]", "", g[1])
                    return (alias.lower(), g[0], g[1])
        
        # we have no idea what is going on,
        # so just return the whole thing
        alias = re.sub(r"[^a-zA-Z]", "", flat_name)
        return (alias.lower(), flat_name, None)
    
    
    def connection(self):
        """Returns the connection object last used by this Reporter.
           The field is (probably) updated by app.py when receiving
           a message, so depends on _incoming_ messages only."""
        
        # TODO: add a "preferred" flag to connection, which then
        # overrides the last_seen connection as the default, here
        return self.connections.latest("last_seen")

    def last_seen(self):
        """Returns the Python datetime that this Reporter was last seen,
           on any Connection. Before displaying in the WebUI, the output
           should be run through the XXX  filter, to make it prettier."""
        
        # comprehend a list of datetimes that this
        # reporter was last seen on each connection,
        # excluding those that have never seen them
        timedates = [
            c.last_seen
            for c in self.connections.all()
            if c.last_seen is not None]
        
        # return the latest, or none, if they've
        # has never been seen on ANY connection
        return max(timedates) if timedates else None

class RecursiveManager(models.Manager):
    """Provides a method to flatten a recursive model (a model which has a ForeignKey field linked back
       to itself), in addition to the usual models.Manager methods. This Manager queries the database
       only once (unlike select_related), and sorts them in-memory. Obivously, this efficiency comes
       at the cost much higher CPU usage."""
    
    def flatten(self, via_field="parent_id"):
        all_objects = list(self.model.objects.all())
        
        def pluck(pk=None, depth=0):
            output = []
            
            for object in all_objects:
                if getattr(object, via_field) == pk:
                    output += [object] + pluck(object.pk, depth+1)
                    object.depth = depth
            
            return output
        return pluck()


class ReporterGroup(models.Model):
    title       = models.CharField(max_length=30, unique=True)
    parent      = models.ForeignKey("self", related_name="children", null=True, blank=True)
    description = models.TextField(blank=True)
    objects     = RecursiveManager()
    
    
    class Meta:
        verbose_name = "Group"

    
    def __unicode__(self):
        return self.title
    
    
    @classmethod
    def flat_tree(klass):
        return [g.flat_children() for g in klass.objects.filter(parent=None)]
    
    def flat_children(self):
        return [self] + [c.flat_children() for c in self.children.all()]


class BackendManager(models.Manager):
    def get_query_set(self):
        
        # fetch a list of all the backends
        # that we already have objects for
        known_backends  = PersistantBackend.raw_objects.values_list("title", flat=True)
        
        # and a list of the backends which are
        # running, which we SHOULD have objects for 
        running_backends = [be["title"] for be in conf["rapidsms"]["backends"]]
        
        # find any running backends which currently
        # don't have objects, and fill in the gaps
        for t in running_backends:
            if not t in known_backends:
                PersistantBackend(title=t).save()
        
        # now that we're sure the backends table is up
        # to date, continue fetching the queryset as usual
        return super(BackendManager, self).get_query_set()


class PersistantBackend(models.Model):
    """This class exists to provide a primary key for each
       named RapidSMS backend, which can be linked from the
       other modules. We can't use a char field with OPTIONS
       (in models which wish to link to a backend), since the
       available backends (and their orders) may change after
       deployment; hence, something persistant is needed."""
    title       = models.CharField(max_length=30, unique=True)
    raw_objects = models.Manager()
    objects     = BackendManager()
    
    
    class Meta:
        verbose_name = "Backend"
    
    
    def __unicode__(self):
        return self.title
    
    
    @classmethod
    def from_message(klass, msg):
        """"Fetch a PersistantBackend object from the data buried in a rapidsms.message.Message
            object. In time, this should be moved to the message object itself, since persistance
            should be fairly ubiquitous; but right now, that would couple the framework to this
            individual app. So you can use this for now."""
        be_title = msg.connection.backend.name
        return klass.objects.get(title=be_title)



class PersistantConnection(models.Model):
    """This class is a persistant version of the RapidSMS Connection
       class, to keep track of the various channels of communication
       that Reporters use to interact with RapidSMS (as a backend +
       identity pair, like rapidsms.connection.Connection). When a
       Reporter is seen communicating via a new backend, or is expected
       to do so in future, a PersistantConnection should be created,
       so they can be recognized by their backend + identity pair."""
    backend   = models.ForeignKey(PersistantBackend, related_name="connections")
    identity  = models.CharField(max_length=30)
    reporter  = models.ForeignKey(Reporter, related_name="connections", blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    
    
    class Meta:
        verbose_name = "Connection"
    
    
    def __unicode__(self):
        return "%s:%s" % (
            self.backend,
            self.identity)
    
    
    @classmethod
    def from_message(klass, msg):
        return klass.objects.get(
            backend  = PersistantBackend.from_message(msg),
            identity = msg.connection.identity)
        
    
    
    def seen(self):
        """"Updates the last_seen field of this object to _now_, and saves.
            Unless the linked Reporter has an explict preferred connection
            (see PersistantConnection.prefer), calling this method will set
            it as the implicit default connection for the Reporter. """
        self.last_seen = datetime.now()
        return self.save()
    
    def prefer(self):
        """Removes the _preferred_ flag from all other PersistantConnection objects
           linked to the same Reporter, and sets the _preferred_ flag on this object."""
        for pc in PersistantConnection.objects.filter(reporter=self.reporter):
            pc.preferred = True if pc == self else False
            pc.save()
