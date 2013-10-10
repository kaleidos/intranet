# -*- coding: utf-8 -*-
import os.path, sys
from django.utils.translation import ugettext_lazy as _

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
BASE_URL="http://localhost:8000"

CLIENT_DOMAIN = "localhost:9003"
CLIENT_USE_HTTPS = False


ADMINS = (
    ('Alejandro Alonso', 'alejandro.alonso@kaleidos.net'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'intranet',
        'USER': 'intranet',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

AUTH_USER_MODEL = 'intranet.User'

EMAIL_BACKEND="djmail.backends.default.EmailBackend"
DJMAIL_REAL_BACKEND="django.core.mail.backends.console.EmailBackend"
DJMAIL_TEMPLATE_EXTENSION = 'jinja'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = 'media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
import os
STATIC_ROOT = './static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'
#~ ADMIN_MEDIA_PREFIX = STATIC_URL + "grappelli/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'vy%#h-^hg6f7tbzfg)4j%ny#7c#)+hk&_1_5dcv6-a(lz*ka7m'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django_jinja.loaders.AppLoader',
    'django_jinja.loaders.FileSystemLoader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'intranet.middleware.TokenSessionMiddleware',
    'intranet.middleware.CoorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'lot.middleware.LOTMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    #~ 'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'south',
    'rest_framework',

    'intranet',

    'django_jinja',
    'autoreports',
    'formadmin',
    'djorm_core',
    'lot',
    'django_extensions',
    'djmail',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


API_DEFAULT_PAGE_SIZE = 20


WORKING_HOURS_PER_DAY = 8
HOLIDAYS_PER_YEAR = 23
IVA=0.21
NEXT_INVOICE_DAYS=14
BASE_ADMIN='woper'
LOCALE = ''
GRAPPELLI_ADMIN_TITLE = 'Intranet'

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "lot.auth_backend.LOTBackend",
)

LOT = {
  'fast-login': {
      'name': _(u'Fast login'),
      'duration': 60,
      'one-time': True,
  },
  'slow-login': {
      'name': _(u'Slow login'),
      'duration': 60*60*24,
      'one-time': True,
  },
  'always-login': {
      'name': _(u'Always login'),
      'one-time': False,
      'duration': None,
  },
}

LOT_MIDDLEWARE_PARAM_NAME = 'uuid-login'

SESSION_HEADER_NAME = "HTTP_X_SESSION_TOKEN"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'intranet.api.session_authentication.SessionAuthentication',
    ),
    'FILTER_BACKEND': 'rest_framework.filters.DjangoFilterBackend',
}
