DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'owri',
        'USER': 'owri',
        'PASSWORD': 'owri',
        'ADMINUSER': 'postgres',
        'HOST': 'localhost'
    },
}

INTERNAL_IPS = ('0.0.0.0', '127.0.0.1', '::1')

SECRET_KEY = '12345'

FABRIC_USER = ''

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False


def show_toolbar(request):
    return False


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'owri.settings.local.show_toolbar',
}

GA_ID = ''
AC_TOKEN = ''
AC_USER = ''
AC_BASE_URL = ''
