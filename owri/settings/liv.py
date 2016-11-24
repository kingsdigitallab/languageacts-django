from base import *  # noqa

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'app_owri_liv',
        'USER': 'app_owri',
        'PASSWORD': '',
        'HOST': ''
    },
}

INTERNAL_IPS = INTERNAL_IPS + ('', )

# -----------------------------------------------------------------------------
# Local settings
# -----------------------------------------------------------------------------

try:
    from local import *  # noqa
except ImportError:
    pass
