#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.djangoproject.settings import *


DATABASE_ENGINE = "sqlite3"
DATABASE_NAME   = "/tmp/rapidsms.sqlite3"


INSTALLED_APPS = [
    "rapidsms",
    "rapidsms.contrib.handlers",
    "rapidsms.contrib.echo",

    # enable the django admin using a little shim app (which includes
    # the required urlpatterns), and a bunch of undocumented apps that
    # the AdminSite seems to explode without
    "django.contrib.auth",
    "django.contrib.admin",
    'django.contrib.sessions',
    "django.contrib.contenttypes",
    "rapidsms.contrib.djangoadmin"
]


INSTALLED_BACKENDS = [
]
