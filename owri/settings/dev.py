from base import *  # noqa

CACHE_REDIS_DATABASE = '2'
CACHES['default']['LOCATION'] = '127.0.0.1:6379/' + CACHE_REDIS_DATABASE

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'app_owri_dev',
        'USER': 'app_owri',
        'PASSWORD': '',
        'HOST': ''
    },
}

INSTALLED_APPS = INSTALLED_APPS + ('wagtail.contrib.wagtailstyleguide',)

INTERNAL_IPS = INTERNAL_IPS + ('', )

LOGGING_LEVEL = logging.DEBUG

LOGGING['loggers']['owri']['level'] = LOGGING_LEVEL

TEMPLATES[0]['OPTIONS']['debug'] = True

HAYSTACK_CONNECTIONS['default']['INDEX_NAME'] = 'owri_haystack_dev'
WAGTAILSEARCH_BACKENDS['default']['INDEX'] = 'owri_wagtail_dev'

# -----------------------------------------------------------------------------
# Django Extensions
# http://django-extensions.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

try:
    import django_extensions  # noqa

    INSTALLED_APPS = INSTALLED_APPS + ('django_extensions',)
except ImportError:
    pass

# -----------------------------------------------------------------------------
# Django Debug Toolbar
# http://django-debug-toolbar.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

try:
    import debug_toolbar  # noqa

    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
        'debug_toolbar.middleware.DebugToolbarMiddleware',)
    DEBUG_TOOLBAR_PATCH_SETTINGS = True
except ImportError:
    pass

# -----------------------------------------------------------------------------
# Local settings
# -----------------------------------------------------------------------------

try:
    from local import *  # noqa
except ImportError:
    print('failed to import local settings')

    from test import *  # noqa
    print('the project is running with test settings')
    print('please create a local settings file')
