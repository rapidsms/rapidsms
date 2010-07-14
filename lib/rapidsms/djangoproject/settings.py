#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os, tempfile


# the default ROOT_URLCONF module, bundled with rapidsms, detects and
# maps the urls.py module of each app into a single project urlconf.
# this is handy, but too magical for the taste of some. (remove it?)
ROOT_URLCONF = "rapidsms.djangoproject.urls"


# for some reason, this setting is blank in django's global_settings.py,
# so i'm setting it to something sane here, just to avoid having to do
# it per-project.
MEDIA_URL = "/static/"


# this is required for the django.contrib.sites tests to run, but also
# not included in global_settings.py, and is almost always ``1``.
# see: http://docs.djangoproject.com/en/dev/ref/contrib/sites/
SITE_ID = 1


# ugh. this is why django is garbage. these weird dependencies should be
# handled by their respective apps, but they're not, so here they are.
TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request"
]


# to get up and running quickly with a minimal rapidsms project, start
# with these apps. just prepend them to your INSTALLED_APPS.
RAPIDSMS_BASE_APPS = [

    # the essentials.
    "django_nose",
    "djangotables",
    "rapidsms",

    # common dependencies (which don't clutter up the ui).
    "rapidsms.contrib.handlers",
    "rapidsms.contrib.ajax",

    # enable the django admin using a little shim app (which includes
    # the required urlpatterns), and a bunch of undocumented apps that
    # the AdminSite seems to explode without.
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "rapidsms.contrib.djangoadmin"
]


# alternatively, start with ALL of the contrib apps, for a useful system
# out of the box. (don't forget RAPIDSMS_TABS, or they'll be invisible.)
RAPIDSMS_APPS = RAPIDSMS_BASE_APPS + [
    "rapidsms.contrib.default",
    "rapidsms.contrib.echo",
    "rapidsms.contrib.export",
    "rapidsms.contrib.httptester",
    "rapidsms.contrib.locations",
    "rapidsms.contrib.messagelog",
    "rapidsms.contrib.messaging",
    "rapidsms.contrib.registration",
    "rapidsms.contrib.scheduler",
    "rapidsms.contrib.search",
    #"rapidsms.contrib.training"
]


# the tabs for RAPISMS_BASE_APPS.
RAPIDSMS_BASE_TABS = [
    ("rapidsms.views.dashboard", "Dashboard")
]


# the tabs for RAPIDSMS_APPS.
RAPIDSMS_TABS = RAPIDSMS_BASE_TABS + [
    ("rapidsms.contrib.messagelog.views.message_log",       "Message Log"),
    ("rapidsms.contrib.registration.views.registration",    "Registration"),
    ("rapidsms.contrib.messaging.views.messaging",          "Messaging"),
    ("rapidsms.contrib.locations.views.locations",          "Map"),
    ("rapidsms.contrib.scheduler.views.index",              "Event Scheduler"),
    ("rapidsms.contrib.httptester.views.generate_identity", "Message Tester"),
]


# use django-nose to run tests. rapidsms contains lots of packages and
# modules which django does not find automatically, and importing them
# all manually is tiresome and error-prone.
TEST_RUNNER = "django_nose.NoseTestSuiteRunner"


# since we might hit the database from any thread during testing, the
# in-memory sqlite database isn't sufficient. it spawns a separate
# virtual database for each thread, and syncdb is only called for the
# first. this leads to confusing "no such table" errors. so i'm
# defaulting to a temporary file instead.
TEST_DATABASE_NAME = os.path.join(tempfile.gettempdir(), "rapidsms.test.sqlite3")


# the default log settings are very noisy.
LOG_LEVEL   = "DEBUG"
LOG_FILE    = "/tmp/rapidsms.log"
LOG_FORMAT  = "[%(name)s]: %(message)s"
LOG_SIZE    = 8192 # 8192 bytes = 64 kb
LOG_BACKUPS = 256 # number of logs to keep
