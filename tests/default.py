import os
import sys

db_name = 'test_rapidsms'
db_engine = os.environ.get('DBENGINE', 'sqlite3')
db_name = "rapidsms_{0}".format(os.environ.get('TESTENV', db_name))

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{0}'.format(db_engine),
        'NAME': '{0}.sqlite3'.format(db_name),
    }
}

INSTALLED_BACKENDS = {
    "message_tester": {
        "ENGINE": "rapidsms.contrib.httptester.backend",
    },
}

INSTALLED_APPS = [
    "rapidsms",
    # third party apps.
    "django_nose",
    "djtables",
    # django contrib apps
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    # rapidsms contrib apps.
    "rapidsms.contrib.default",
    "rapidsms.contrib.export",
    "rapidsms.contrib.handlers",
    "rapidsms.contrib.httptester",
    "rapidsms.contrib.locations",
    "rapidsms.contrib.messagelog",
    "rapidsms.contrib.messaging",
    "rapidsms.contrib.registration",
    "rapidsms.contrib.echo",
]

SITE_ID = 1

SECRET_KEY = 'super-secret'

LOGIN_REDIRECT_URL = "/"

# Insecure, but fast for running tests
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

ROOT_URLCONF = "tests.urls"

RAPIDSMS_TABS = [
    ("rapidsms.contrib.messagelog.views.message_log",       "Message Log"),
    ("rapidsms.contrib.registration.views.registration",    "Registration"),
    ("rapidsms.contrib.messaging.views.messaging",          "Messaging"),
    ("rapidsms.contrib.locations.views.locations",          "Map"),
    ("rapidsms.contrib.scheduler.views.index",              "Event Scheduler"),
    ("rapidsms.contrib.httptester.views.generate_identity", "Message Tester"),
]
