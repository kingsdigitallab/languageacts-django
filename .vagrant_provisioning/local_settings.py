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

# @languageacts Twitter's APIs and tokens
TWITTER_API_KEY = ''
TWITTER_API_SECRET = ''
TWITTER_ACCESS_TOKEN = ''
TWITTER_ACCESS_TOKEN_SECRET = ''

# ActiveCollab API URL
AC_BASE_URL = 'https://app.activecollab.com/148987'
AC_API_URL = AC_BASE_URL + '/api/v1/'
# ActiveCollab API token
AC_TOKEN = ''
# ActiveCollab project ID
AC_PROJECT_ID = 771
# ActiveCollab user ID to create the issues
AC_USER = 36

GA_ID = ''

MEDIA_URL = 'media/'
