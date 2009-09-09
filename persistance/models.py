#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from rapidsms.webui import settings


class AppManager(models.Manager):
    def get_query_set(self):
        if not hasattr(self, "_updated"):

            # fetch a list of all the apps
            # that we already have objects for
            known_apps = PersistantApp.raw_objects.values_list(
                "module", flat=True)

            # find any running apps which currently
            # don't have objects, and fill in the gaps
            for conf in settings.RAPIDSMS_APPS.values():
                module = conf["module"]

                if not module in known_apps:
                    PersistantApp.raw_objects.create(
                        title=conf["title"],
                        module=module)

            # add an attr to this class, to limit
            # this update to once per process
            self._updated = True

        # now that we're sure the persistantapp table is up
        # to date, continue fetching the queryset as usual
        return super(AppManager, self).get_query_set()


class PersistantApp(models.Model):
    """This model exists to provide a primary key for other models (in any
       app) to link to with a foreign key, rather than storing module strings
       themselves. The Django ContentType stuff doesn't quite work here, since
       not all RapidSMS apps are valid Django apps. It would be nice to fill
       in the gaps and inherit from it at some point in the future.

       Instances of this model are created by AppManager on-demand, so even when
       the database is empty, PersistantApp.objects.all() can still be used to
       iterate the running apps."""

    title  = models.CharField(max_length=30, blank=True)
    module = models.CharField(max_length=30, unique=True)
    active = models.BooleanField()

    objects     = AppManager()
    raw_objects = models.Manager()


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


class BackendManager(models.Manager):
    def get_query_set(self):
        if not hasattr(self, "_updated"):

            # fetch a list of all the backends
            # that we already have objects for
            known_backends = PersistantBackend.raw_objects.values_list(
                "slug", flat=True)
            
            # find any running backends which currently
            # don't have objects, and fill in the gaps
            for conf in settings.RAPIDSMS_BACKENDS.values():
                slug = conf["name"]

                if not slug in known_backends:
                    PersistantBackend.raw_objects.create(
                        title=conf.get("title", ""),
                        slug=slug)

            # add an attr to this class, to limit
            # this update to once per process
            self._updated = True

        # now that we're sure the persistantbackend table is
        # up to date, continue fetching the queryset as usual
        return super(BackendManager, self).get_query_set()


class PersistantBackend(models.Model):
    """This model exists to provide a primary key for each RapidSMS backend,
       for other models (in any app) to link to with a foreign key. We can't
       use a char field with OPTIONS, since the available backends (and their
       order) may change after deployment."""

    title = models.CharField(max_length=30, blank=True)
    slug  = models.CharField(max_length=30, unique=True)

    objects     = BackendManager()
    raw_objects = models.Manager()


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
