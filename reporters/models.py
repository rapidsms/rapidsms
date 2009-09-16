#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from datetime import datetime
from django.db import models
from django.core.urlresolvers import reverse
from rapidsms.djangoproject.managers import *
from persistance.models import PersistantBackend


class ReporterGroup(models.Model):
    title       = models.CharField(max_length=30, unique=True)
    parent      = models.ForeignKey("self", related_name="children", null=True, blank=True)
    description = models.TextField(blank=True)
    objects     = RecursiveManager()

    # this belongs in Meta, but Django won't
    # let us put _unapproved_ things there
    followable = True


    class Meta:
        verbose_name = "Group"


    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self.title)


    # see the FOLLOW app, for now,
    # although this will be expanded
    @classmethod
    def __search__(cls, terms):

        # re-join the terms into a single string, and search
        # for a group with this title (we wont't worry about
        # other delimiters for now, but might need to come back)
        try:
            return cls.objects.get(
                title__iexact=" ".join(terms))

        # if this doesn't work, the terms
        # are not a valid location name
        except cls.DoesNotExist, cls.MultipleObjectsReturned:
            return None


    def __message__(self, *args, **kwargs):
        """Sends a message to every Reporter in this ReporterGroup."""

        for rep in self.reporters.all():
            try:
                rep.__message__(*args, **kwargs)
            except:
                pass


    # TODO: rename to something that indicates
    #       that it's a counter, not a queryset
    def members(self):
        return self.reporters.all().count()


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
    groups     = models.ManyToManyField(ReporterGroup, related_name="reporters", blank=True)


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


    # this belongs in Meta, but Django won't
    # let us put _unapproved_ things there
    followable = True


    class Meta:
        ordering = ["last_name", "first_name"]


    def full_name(self):
        return ("%s %s" % (
            self.first_name,
            self.last_name)).strip()

    def __unicode__(self):
        return self.full_name() or self.alias

    def __repr__(self):
        fn = self.full_name()
        n = type(self).__name__
        
        if fn == "":
            return '<%s: %s>' %\
                (n, self.alias)

        else:
            return '<%s: %s (%s)>' %\
                (n, fn, self.alias)

    def __json__(self):
        return {
            "pk":         self.pk,
            "alias":      self.alias,
            "first_name": self.first_name,
            "last_name":  self.last_name,
            "str":        unicode(self) }

    # see the FOLLOW app, for now,
    # although this will be expanded
    @classmethod
    def __search__(cls, terms):
        try:
            if len(terms) == 1:
                try:
                    return cls.objects.get(
                        pk=int(terms[0]))

                except (ValueError, cls.DoesNotExist):
                    return cls.objects.get(
                        alias__iexact=terms[0])

            elif len(terms) == 2:
                return cls.objects.get(
                    first_name__iexact=terms[0],
                    last_name__iexact=terms[1])

        except cls.DoesNotExist:
            return None


    def __message__(self, router, text):
        """Sends a message to this Reporter, via _router_."""

        # abort if we don't know where to send the message to
        # (if the device the reporter registed with has been
        # taken by someone else, or was created in the WebUI)
        pconn = self.connection()
        if pconn is None:
            raise Exception("%s is unreachable (no connection)" % self)

        # abort if we can't find a valid backend. persistance.models.Backend
        # objects SHOULD refer to a valid RapidSMS backend (via their slug),
        # but sometimes backends are removed or renamed.
        be = router.get_backend(pconn.backend.slug)
        if be is None:
            raise Exception(
                "No such backend: %s" %
                pconn.backend)

        # attempt to send the message
        # TODO: what could go wrong here?
        return [be.message(pconn.identity, text).send()]


    @classmethod
    def exists(klass, reporter, connection):
        """Checks if a reporter has already been entered into the system"""
        try:
            # look for a connection and reporter object matching what
            # was passed in, and if they are already linked then this
            # reporter already exists
            existing_conn = PersistantConnection.objects.get\
                (backend=connection.backend, identity=connection.identity)
            # this currently checks first and last name.
            # we may want to make this more lax
            filters = {"first_name" : reporter.first_name,
                       "last_name" : reporter.last_name } 
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
    def IsCodeUnique(klass,alias): 
        """ Check if the code is not used before."""

        if klass.objects.filter(alias__iexact=alias).count():  
            return False
        else:
            return True 
   
        

    @classmethod
    def parse_name(cls, flat_name):
        """
            Returns a three-string tuple containing a suggested alias, first
            name, and last name, by performing some crude pattern matching on
            *flat_name*. For example:

              >>> Reporter.parse_name("Adam Mckaig")
              ('amckaig', 'Adam', 'Mckaig')

              >>> Reporter.parse_name('XYZZY ^__^')
              ('xyzzy', 'XYZZY', '')

              >>> Reporter.parse_name('12345')
              ('12345', '', '')

              # if an alias is already taken, incrementing
              # digits are appended until one is available

              >>> Reporter.objects.create(alias='ewheeler')
              <Reporter: ewheeler>

              >>> Reporter.parse_name('Evan Wheeler')
              ('ewheeler2', 'Evan', 'Wheeler')
        """

        def unique(alias):
            try_alias = alias
            n = 2

            # keep on looping until an alias becomes available.
            # --
            # WARNING: this isn't going to work at high volumes, since the alias
            # that we return might be taken before we have time to do anything
            # with it! This should logic should probably be moved to the
            # initializer, to make the find/grab alias loop atomic
            while cls.objects.filter(alias__iexact=try_alias).count():
                try_alias = "%s%d" % (alias, n)
                n += 1

            return try_alias

        patterns = [
            # try a few common name formats.
            # this is crappy but sufficient
            r"([a-z]+)\s+([a-z]+)",            # Evan Wheeler
            r"([a-z]+)\s+[a-z]+\.?\s+([a-z]+)",# Mark E. Johnston
            r"([a-z]+)\s+([a-z]+\-[a-z]+)"     # Erica Kochi-Fabian
        ]

        # try each pattern, returning as
        # soon as we find something that fits
        for pat in patterns:

            m = re.match(pat, flat_name, re.I)
            if m is not None:
                first_name, last_name = m.groups()

                # generate an alias from the first letter of the first
                # name, and the letters (no dots or dashes) from the last
                alias = (first_name[0] + re.sub(r"[^a-zA-Z]", "", last_name)).lower()
                return (unique(alias), first_name.title(), last_name.title())

        # flat_name doesn't look like a full name, so generate an alias
        # from the alphanumerics (some aliases are entirely numeric),
        # and a name from just the letters (there might not be any)
        alias = unique(re.sub(r"[^a-zA-Z0-9]", "", flat_name).lower())
        name = re.sub(r"[^a-zA-Z]", "", flat_name)
        return (alias, name, "")


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
        unique_together = ("backend", "identity")


    def __unicode__(self):
        return "%s:%s" % (
            self.backend,
            self.identity)

    def __repr__(self):
        return '<%s: %s via %s>' %\
            (type(self).__name__, self.identity, self.backend.slug)

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


    @property
    def dict(self):
        """Returns a handy dictionary containing the most personal persistance
           information that we have about this connection. this is useful when
           creating an object that we would like to link to a reporter, but can
           fall back to a connection if we haven't identified them yet.

           For example:

               class SomeObject(models.Model):
                   connection = models.ForeignKey(PersistantConnection, null=True)
                   reporter   = models.ForeignKey(Reporter, null=True)
                   stuff      = models.CharField()

                # this object will be linked to a Reporter, if
                # one exists - otherwise, a PersistantConnection
                SomeObject(stuff="hello", **connection.dict)

           Don't forget to verify that _one_ of reporter or connection is not
           None before saving. See logger.models.ModelBase for an example."""

        if self.reporter:
            return { "reporter": self.reporter }

        elif self.pk:
            return { "connection": self }

        else:
            raise(Exception,
                "This PersistantConnection must be saved " +\
                "before it can be linked to another object.")

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

    def add_reporter_url(self):
        """Returns the URL to the "add-reporter" view, prepopulated with this
           PersistantConnection object. This shouldn't be here, since it couples
           the Model and view layers, but the folks in #django don't have any
           better suggestions."""
        return "%s?connection=%s" % (reverse("add-reporter"), self.pk)
