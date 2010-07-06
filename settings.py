#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.djangoproject.settings import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = "sqlite3"
DATABASE_NAME   = "/tmp/rapidsms.sqlite3"

INSTALLED_APPS = RAPIDSMS_APPS
TABS = RAPIDSMS_TABS

# these apps should not be started by rapidsms in your tests, however,
# the models and bootstrap will still be available through django.
TEST_EXCLUDED_APPS = (
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rapidsms",
    "rapidsms.contrib.ajax",
    "rapidsms.contrib.httptester",
)

# the INSTALLED_BACKENDS setting is intended to resemble django 1.2's
# DATABASE: http://docs.djangoproject.com/en/dev/ref/settings/#databases
INSTALLED_BACKENDS = {
    #"AT&T": {
    #    "ENGINE": "rapidsms.backends.gsm",
    #    "PORT": "/dev/ttyUSB0"
    #},
    #"Verizon": {
    #    "ENGINE": "rapidsms.backends.gsm,
    #    "PORT": "/dev/ttyUSB1"
    #},
    "message_tester": {
        "ENGINE": "rapidsms.backends.bucket"
    }
}

# after login (which is handled by django.contrib.auth), redirect to the
# dashboard rather than 'accounts/profile' (the default).
LOGIN_REDIRECT_URL = "/"
