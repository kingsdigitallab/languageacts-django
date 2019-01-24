from .base import *  # noqa

CACHE_REDIS_DATABASE = '1'
CACHES['default']['LOCATION'] = '127.0.0.1:6379:' + CACHE_REDIS_DATABASE

ALLOWED_HOSTS = ['']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'app_owri_stg',
        'USER': 'app_owri',
        'PASSWORD': '',
        'HOST': ''
    },
}

INTERNAL_IPS = INTERNAL_IPS + ('', )
HAYSTACK_CONNECTIONS['default']['INDEX_NAME'] = 'owri_haystack_dev'
WAGTAILSEARCH_BACKENDS['default']['INDEX'] = 'owri_wagtail_stg'

# -----------------------------------------------------------------------------
# Local settings
# -----------------------------------------------------------------------------

try:
    from .local import *  # noqa
except ImportError:
    pass
