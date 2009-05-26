#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os, time


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS


# default to the system's timezone settings. this can still be
# overridden in rapidsms.ini [django], by providing one of:
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

# Make this unique, and don't share it with anybody.
SECRET_KEY = '2rgmwtyq$thj49+-6u7x9t39r7jflu&1ljj3x2c0n0fl$)04_0'

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

ROOT_URLCONF = "rapidsms.webui.urls"

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




# ====================
# LOAD RAPIDSMS CONFIG
# ====================

# this module will usually be called up via the django
# reloader, which is (in turn) called up by rapidsms's
# server.py, which adds RAPIDSMS_INI to the environment.
# just in case, though, check that it's defined rather
# than repeating the filename selection logic here
if not "RAPIDSMS_INI" in os.environ:
    raise(
        EnvironmentError,
        "The RAPIDSMS_INI environment variable is not "  +\
        "defined. Without it, settings.py doesn't know " +\
        "which ini file to load settings from")

# load the rapidsms configuration
from rapidsms import Config
RAPIDSMS_CONF = Config(os.environ["RAPIDSMS_INI"])

# since iterating and reading the config of apps is
# common, build a handy dict of apps and their configs
RAPIDSMS_APPS = dict([
    (app["type"], app)
    for app in RAPIDSMS_CONF["rapidsms"]["apps"]])




# ==========================
# LOAD OTHER DJANGO SETTINGS
# ==========================

# load the database settings first, since those
# keys don't correspond exactly to their eventual
# name in this module (they're missing the prefix
# in rapidsms.ini); inject them into this module
if "database" in RAPIDSMS_CONF:
    for key, val in RAPIDSMS_CONF["database"].items():
        vars()["DATABASE_%s" % key.upper()] = val

else:
    # database settings are missing, so
    # blow up. TODO: is there a way to
    # run django without a database?
    raise(
        "Your RapidSMS configuration does not contain " +\
        "a [database] section, which is required " +\
        "for the Django WebUI to function.")

# if there is a "django" section, inject
# the items as CONSTANTS in this module
if "django" in RAPIDSMS_CONF:
    for key, val in RAPIDSMS_CONF["django"].items():
        vars()[key.upper()] = val




# ====================
# INJECT RAPIDSMS APPS
# ====================

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs'
] + [app["module"] for app in RAPIDSMS_APPS.values()]
