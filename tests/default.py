import os

db_name = 'test_rapidsms'
db_engine = os.environ.get('DBENGINE', 'sqlite3')

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{0}'.format(db_engine),
        'NAME': '{0}.sqlite3'.format(db_name),
    }
}

INSTALLED_BACKENDS = {
    "message_tester": {
        "ENGINE": "rapidsms.backends.database.DatabaseBackend",
    },
}

INSTALLED_APPS = [
    "rapidsms",
    # third party apps.
    "django_nose",
    "djtables",
    "django_tables2",
    "selectable",
    # django contrib apps
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.contenttypes",
    # rapidsms contrib apps.
    "rapidsms.contrib.handlers",
    "rapidsms.contrib.httptester",
    "rapidsms.contrib.locations",
    "rapidsms.contrib.messagelog",
    "rapidsms.contrib.messaging",
    "rapidsms.contrib.registration",
    "rapidsms.contrib.echo",
    "rapidsms.router.db",
    "rapidsms.backends.database",
    "rapidsms.backends.kannel",
    "rapidsms.tests.translation",

    "rapidsms.contrib.default",  # Should be last
]

# Django 1.7+ emits a warning if this is not set
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

SITE_ID = 1

SECRET_KEY = 'super-secret'

LOGIN_REDIRECT_URL = "/"

STATIC_URL = '/static/'

# Insecure, but fast for running tests
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

ROOT_URLCONF = "tests.urls"

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

PROJECT_NAME = 'rapidsms-test-suite'

import djcelery
djcelery.setup_loader()

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
