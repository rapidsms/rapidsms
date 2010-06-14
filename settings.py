#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.djangoproject.settings import *


DATABASE_ENGINE = "sqlite3"
DATABASE_NAME   = "/tmp/rapidsms.sqlite3"


INSTALLED_APPS = [
    "rapidsms",
    "djangotables",

    "rapidsms.contrib.handlers",
    "rapidsms.contrib.echo",
    "rapidsms.contrib.ajax",
    "rapidsms.contrib.httptester",
    "rapidsms.contrib.registration",

    # enable the django admin using a little shim app (which includes
    # the required urlpatterns), and a bunch of undocumented apps that
    # the AdminSite seems to explode without
    "django.contrib.auth",
    "django.contrib.admin",
    'django.contrib.sessions',
    "django.contrib.contenttypes",
    "rapidsms.contrib.djangoadmin"
]

# These apps should not be started by rapidsms in your tests
# However the models + bootstrap will still be available through
# django
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

# after login, django redirects to this URL
# rather than the default 'accounts/profile'
LOGIN_REDIRECT_URL='/'
