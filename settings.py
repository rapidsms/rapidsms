#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.djangoproject.settings import *


DATABASE_ENGINE = "sqlite3"
DATABASE_NAME   = "/tmp/rapidsms.sqlite3"


INSTALLED_APPS = [
    "rapidsms",
    "rapidsms.contrib.handlers",
    "rapidsms.contrib.echo"
]


INSTALLED_BACKENDS = [
]
