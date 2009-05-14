#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os, re
from datetime import datetime
from django.db import models

from apps.patterns.models import Pattern

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
    patterns = models.ManyToManyField(Pattern, null=True, blank=True)
    
    def match(self, token):
        return self.regex and re.match(self.regex, token, re.IGNORECASE)
    
    @property
    def regex(self):
        # convenience accessor for joining patterns
        return Pattern.join(self.patterns)
    
    def __unicode__(self):
        return self.name

class LocationType(models.Model):
    """A type of location.  For example 'School' or 'Factory'"""
    name = models.CharField(max_length=160,help_text="Name of location type")
        
    def __unicode__(self):
        return self.name
    

class RecursiveManager(models.Manager):
    """Provides a method to flatten a recursive model (a model which has a ForeignKey field linked back
       to itself), in addition to the usual models.Manager methods. This Manager queries the database
       only once (unlike select_related), and sorts them in-memory. Obivously, this efficiency comes
       at the cost local inefficiency -- O(n^2) -- but that's still preferable to recursively querying
       the database."""
    
    def flatten(self, via_field="parent_id"):
        all_objects = list(self.all())
        
        def pluck(pk=None, depth=0):
            output = []
            
            for object in all_objects:
                if getattr(object, via_field) == pk:
                    output += [object] + pluck(object.pk, depth+1)
                    object.depth = depth
            
            return output
        return pluck()


class Location(models.Model):
    """A location.  Locations have a name, an optional type, and optional geographic information."""
    name = models.CharField(max_length=160, help_text="Name of location")
    type = models.ForeignKey(LocationType, related_name="locations", blank=True, null=True, help_text="Type of location")
    code = models.CharField(max_length=15)
    parent = models.ForeignKey("Location", related_name="children", null=True, blank=True, help_text="The parent location of this")
    latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True, help_text="The physical latitude of this location")
    longitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True, help_text="The physical longitude of this location")
    objects = RecursiveManager()

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
        
    def top_children(self):
        # this is a pretty silly way to provide easy access to the first N children
        # inside a template
        count = 10
        return self.children.all()[0:10]

    def one_contact(self, role, display=False):
        def __get_one(contacts):
            if contacts.count() > 0:

                # since we are formatting for display,
                # loop through all contacts until we
                # find one that has a name and number
                if display:
                    for contact in contacts:
                        string = __display(contact)
                        if (len(string) > 4):
                            return string

                # return the first contact if we are
                # not formatting for display
                else:
                    return contacts[0]

            # return None if no contacts are found
            # or return an empty string if we are
            # formatting this for display
            else:
                return "" if display else None

        def __display(contact):
                string = contact.first_name + " " + contact.last_name
                if contact.connection() is not None:
                    string = string + " (" + contact.connection().identity + ")"
                return string

        return __get_one(Reporter.objects.filter(location=self).filter(role__code__iexact=role))

    def contacts(self, role=None):
        if role is not None:
            return Reporter.objects.filter(location=self).filter(role__code__iexact=role)
        return Reporter.objects.filter(location=self)

    def __unicode__(self):
        return self.name


class ReporterGroup(models.Model):
    title       = models.CharField(max_length=30, unique=True)
    parent      = models.ForeignKey("self", related_name="children", null=True, blank=True)
    description = models.TextField(blank=True)
    objects     = RecursiveManager()
    
    
    class Meta:
        verbose_name = "Group"

    
    def __unicode__(self):
        return self.title


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
    groups     = models.ManyToManyField(ReporterGroup, blank=True)
    
    # here are some fields that don't belong here
    location   = models.ForeignKey("Location", related_name="reporters", null=True, blank=True)
    role       = models.ForeignKey("Role", related_name="reporters", null=True, blank=True)

    def __unicode__(self):
        return self.connection().identity
        

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
    language = models.CharField(max_length=10, blank=True)
	
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
    
    def __json__(self):
        return {
            "pk":         self.pk,
            "alias":      self.alias,
            "first_name": self.first_name,
            "last_name":  self.last_name,
            "str":        unicode(self) }
    
    
    @classmethod
    def exists(klass, reporter, connection):
        """Checks if a reporter has already been entered into the system"""
        try:
            # look for a connection and reporter object matching what
            # was passed in, and if they are already linked then this
            # reporter already exists
            existing_conn = PersistantConnection.objects.get\
                (backend=connection.backend, identity=connection.identity)
            # this currently checks first and last name, location and role.
            # we may want to make this more lax
            filters = {"first_name" : reporter.first_name,
                       "last_name" : reporter.last_name,
                       "location" : reporter.location,
                       "role" : reporter.role } 
            existing_reps = Reporter.objects.filter(**filters)
            for existing_rep in existing_reps:
                if existing_rep == existing_conn.reporter:
                    return True
            return False 
        except PersistantConnection.DoesNotExist:
            # if we couldn't find a connection then they 
            # don't exist
            return False 
        
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
            r"([a-z]+)\s+[a-z]+\.?\s+([a-z]+)",# Mark E. Johnston, Lee Harvey Oswald 
            r"([a-z]+)\s+([a-z]+\-[a-z]+)"     # Erica Kochi-Fabian
        ]
        
        def unique(str):
            """Checks an alias for uniqueness; if it is already taken, alter it
               (by append incrementing digits) until an available alias is found."""
            
            n = 1
            alias = str.lower()
            
            # keep on looping until an alias becomes available.
            # --
            # WARNING: this isn't going to work at high volumes, since the alias
            # that we return might be taken before we have time to do anything
            # with it! This should logic should probably be moved to the
            # initializer, to make the find/grab alias loop atomic
            while klass.objects.filter(alias__iexact=alias).count():
                alias = "%s%d" % (str.lower(), n)
                n += 1
            
            return alias
        
        # try each pattern, returning as
        # soon as we find something that fits
        for pat in patterns:
            m = re.match("^%s$" % pat, flat_name, re.IGNORECASE)
            if m is not None:
                g = m.groups()
                
                # return single names as-is
                # they might already be aliases
                if len(g) == 1:
                    alias = unique(g[0].lower())
                    return (alias, g[0], "")
                    
                else:
                    # return only the letters from
                    # the first and last names
                    alias = unique(g[0][0] + re.sub(r"[^a-zA-Z]", "", g[1]))
                    return (alias.lower(), g[0], g[1])
        
        # we have no idea what is going on,
        # so just return the whole thing
        alias = unique(re.sub(r"[^a-zA-Z]", "", flat_name))
        return (alias.lower(), flat_name, "")
    
    
    def connection(self):
        """Returns the connection object last used by this Reporter.
           The field is (probably) updated by app.py when receiving
           a message, so depends on _incoming_ messages only."""
        
        # TODO: add a "preferred" flag to connection, which then
        # overrides the last_seen connection as the default, here
        try:
            return self.connections.latest("last_seen")
        
        # if no connections exist for this reporter (how
        # did that happen?!), then just return None...
        except PersistantConnection.DoesNotExist:
            return None

    
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


class PersistantBackend(models.Model):
    """This class exists to provide a primary key for each
       named RapidSMS backend, which can be linked from the
       other modules. We can't use a char field with OPTIONS
       (in models which wish to link to a backend), since the
       available backends (and their orders) may change after
       deployment; hence, something persistant is needed."""
    slug        = models.CharField(max_length=30, unique=True)
    title       = models.CharField(max_length=30)
    
    
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
        be_slug = msg.connection.backend.slug
        return klass.objects.get(slug=be_slug)


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
    
    def __json__(self):
        return {
            "pk": self.pk,
            "identity": self.identity,
            "reporter": self.reporter,
            "str": unicode(self) }
    
    
    @classmethod
    def from_message(klass, msg):
        obj, created = klass.objects.get_or_create(
            backend  = PersistantBackend.from_message(msg),
            identity = msg.connection.identity)
        
        if created:
            obj.save()
        
        # just return the object. it doesn't matter
        # if it was created or fetched. TODO: maybe
        # a parameter to return the tuple
        return obj
    
    
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
