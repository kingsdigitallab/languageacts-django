from .base import *  # noqa

DEBUG = True
TEMPLATE_DEBUG = True

SECRET_KEY = 'test'

# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# ActiveCollab API URL
AC_BASE_URL = ''
AC_API_URL = AC_BASE_URL + '/api/v1/'
# ActiveCollab API token
AC_TOKEN = ''
# ActiveCollab project ID
AC_PROJECT_ID = 0
# ActiveCollab user ID to create the issues
AC_USER = 0

GA_ID = ''

MEDIA_URL = 'media/'
