from celery import Celery


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_BACKENDS = {
    'message_tester': {
        'ENGINE': 'rapidsms.backends.database.DatabaseBackend',
    },
}

INSTALLED_APPS = [
    'rapidsms',
    # third party apps.
    'django_tables2',
    'selectable',
    # django contrib apps
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    # rapidsms contrib apps.
    'rapidsms.contrib.handlers',
    'rapidsms.contrib.httptester',
    'rapidsms.contrib.messagelog',
    'rapidsms.contrib.messaging',
    'rapidsms.contrib.registration',
    'rapidsms.contrib.echo',
    'rapidsms.router.db',
    'rapidsms.backends.database',
    'rapidsms.backends.kannel',
    'rapidsms.tests.translation',

    'rapidsms.contrib.default',  # Should be last
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        }
    },
    'root': {
        'handlers': ['null'],
    },
    'loggers': {
        'py.warnings': {
            'handlers': ['console'],
        },
    }
}

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

SITE_ID = 1

SECRET_KEY = 'super-secret'

LOGIN_REDIRECT_URL = '/'

STATIC_URL = '/static/'

# Insecure, but fast for running tests
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

ROOT_URLCONF = 'tests.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

PROJECT_NAME = 'rapidsms-test-suite'

app = Celery('rapidsms')
app.config_from_object('django.conf:settings')

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
