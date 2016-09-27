"""
Django settings for mirage project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import markdown

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY="this is totally a secret"
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_CONTEXT_PROCESSORS = (
    "mirage.context_processors.api_host",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)
TEMPLATE_DEBUG = True
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'mirage_site/templates'),

)
ALLOWED_HOSTS = [
    '.gsa.gov',
    '127.0.0.1', 
    '.18f.us',
    'localhost',
]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'api',
    'mirage_site',
    'apple',
    'contract',
    'selenium_tests',
    'rest_framework_swagger',
    'storages',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mirage.urls'
APPEND_SLASH = True
WSGI_APPLICATION = 'mirage.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'oasis',
        'USER': 'oasis',
        'PASSWORD': '1234'
    }
}

SAM_API_KEY = ''


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


#project specific
VEHICLES = ('oasissb', 'oasis')

SAM_API_URL = "https://api.data.gov/sam/v1/registrations/"
USASPENDING_API_URL = "http://www.usaspending.gov/fpds/fpds.php"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/mirage.log'),
            'formatter': 'verbose'
        },
        'vendor_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/vendor.log'),
            'formatter': 'verbose'
        },
        'sam_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/sam.log'),
            'formatter': 'verbose'
        },
        'fpds_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/fpds.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'vendors': {
            'handlers': ['vendor_file'],
            'level': 'DEBUG',
        },
        'sam': {
            'handlers': ['sam_file'],
            'level': 'DEBUG',
        },
        'fpds': {
            'handlers': ['fpds_file'],
            'level': 'DEBUG',
        },

    },
}

try:
    from mirage.local_settings import *
except:
    pass

SWAGGER_SETTINGS = {
    "doc_expansion": "full",
    "exclude_namespaces": [], # List URL namespaces to ignore
    "api_version": '0.1',  # Specify your API's version
    "api_path": "/",  # Specify the path to your API not a root level
    #"api_host": '', #comment out until fix swagger - API_HOST, #the data.gov api host
    "enabled_methods": [  # Specify which methods to enable in Swagger UI
        'get',
    ],
    "api_key": '', #Acomment out until fix swagger PI_KEY , # An API key
    "is_authenticated": False,  # Set to True to enforce user authentication,
    "is_superuser": False,  # Set to True to enforce admin only access
    "permission_denied_handler": None, # If user has no permisssion, raise 403 error
    "info": {
        "contact": "discovery-18f@gsa.gov",
        "title": "Discovery Market Research API",
        "description": markdown.markdown("""
This API drives the [Discovery Market Research Tool](https://discovery.gsa.gov).
It contains information on the vendors that are part of the OASIS and OASIS Small Business contracting vehicles, such as their contracting history, their elligibility for contract awards, and their small business designations.
To learn more about the tool, please visit [Discovery](https://discovery.gsa.gov) or see the README on our [GitHub repository](https://github.com/18F/mirage).

**Please note that the base path for this API is `https://api.data.gov/gsa/discovery/`**

It requires an API key, obtainable at [api.data.gov](http://api.data.gov/).
It must be passed in the `api_key` parameter with each request.
        """), #converts markdown description to HTML
    },
    "template_path": "api_theme/index.html",
}


