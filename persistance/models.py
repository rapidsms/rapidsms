#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from rapidsms.webui import settings


class PersistantApp(models.Model):
    """This model exists to provide a primary key for other models (in any
       app) to link to with a foreign key, rather than storing module strings
       themselves. The Django ContentType stuff doesn't quite work here, since
       not all RapidSMS apps are valid Django apps. It would be nice to fill
       in the gaps and inherit from it at some point in the future.

       Instances of this model are generated after syncdb (or on-demand) by the
       update_apps command, and generally shouldn't be messed with."""

    title  = models.CharField(max_length=30, blank=True)
    module = models.CharField(max_length=30, unique=True)
    active = models.BooleanField()


    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self.module)


    @classmethod
    def resolve(cls, app):
        """Resolves a RapidSMS app or module string into a PersistantApp
           instance, or returns None if nothing could be found. This is useful
           for swapping _something_ for a linkable object."""

        try:

            # if it's already a persistant app,
            # (maybe a double call), return as-is
            if isinstance(app, cls):
                return app

            # if it looks like a rapidsms app
            elif hasattr(app, "config"):
                return cls.objects.get(
                    module=app.config["module"])

            # otherwise, assume it's a module string
            else:
                return PersistantApp.objects.get(
                    module=app)

        except cls.DoesNotExist:
            return None


class PersistantBackend(models.Model):
    """This model exists to provide a primary key for each RapidSMS backend,
       for other models (in any app) to link to with a foreign key. We can't
       use a char field with OPTIONS, since the available backends (and their
       order) may change after deployment."""

    title = models.CharField(max_length=30, blank=True)
    slug  = models.CharField(max_length=30, unique=True)


    def __unicode__(self):
        return self.title or self.slug

    def __repr__(self):
        return '<%s: %s via %s>' %\
            (type(self).__name__, self.slug)

    @classmethod
    def from_message(cls, msg):
        return cls.from_backend(
            msg.connection.backend)

    @classmethod
    def from_backend(cls, backend):
        return cls.objects.get(
            slug=backend.slug)
