#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os, time, tempfile


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS


# default to the system's timezone settings. this can still be
# hard-coded in the project's settings.py, by providing one of:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = time.tzname[0]


# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = "rapidsms.djangoproject.urls"

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request"
]

TEMPLATE_DIRS = [
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
]


# since we might hit the database from any thread during testing, the in-memory
# sqlite database isn't sufficient. it spawns a separate virtual database for
# each thread, and syncdb is only called for the first. this leads to confusing
# "no such table" errors. so i'm defaulting to a temporary file instead.
TEST_DATABASE_NAME = os.path.join(tempfile.gettempdir(), "rapidsms.test.sqlite3")


# the default log settings are very noisy
LOG_LEVEL   = "DEBUG"
LOG_FILE    = "/tmp/rapidsms.log"
LOG_FORMAT  = "[%(name)s]: %(message)s"
LOG_SIZE    = 8192 # 8192 bytes = 64 kb
LOG_BACKUPS = 256 # number of logs to keep

# if file None, this settings defaults to whatever LOG_FILE
# ends up set to after merging rapidsms.ini and cmd-line args
LOG_FILE_FORMAT = None
