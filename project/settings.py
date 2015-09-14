"""
Django settings for this project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, ldap, logging, urllib.request, shutil
from django_auth_ldap.config import LDAPSearch, PosixGroupType

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# The SECRET_KEY is provided via an environment variable in OpenShift
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    # safe value used for development when DJANGO_SECRET_KEY might not be set
    '9e4@&tw46$l31)zrqe3wi+-slqm(ruvz&se0^%9#6(_w3ui!c0'
)

# SECURITY WARNING: don't run with debug turned on in production!
# For testing set Debug to True and SECURE_SSL_REDIRECT to False
# DEBUG = False
DEBUG = True
SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.auth.backends',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.auth.decorators',
    'django.contrib.auth.urls',
    'debug_toolbar',
    'autopatch',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
    )

LOGIN_REDIRECT_URL = "/autopatch/profile/"
LOGIN_URL = "/autopatch/login/"

LDAP_HOST = os.getenv('LDAP_HOST')
LDAP_BASEDN = os.getenv('LDAP_BASEDN')

AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 600

if not LDAP_HOST:
    LDAP_HOST = ""
else:
    pass
if not LDAP_BASEDN:
    LDAP_BASEDN = ""
else:
    LDAP_BASEDN = LDAP_BASEDN.replace(" ",",")
    pass

print("LDAP URL and basedn:", LDAP_HOST, LDAP_BASEDN)

# LDAP CA cert
LDAP_CACERTFILE = "autopatch/ca.crt"
if not os.path.exists(LDAP_CACERTFILE):
    AUTH_LDAP_START_TLS = True
    LDAP_CACERT_URL = os.getenv('LDAP_CACERT_URL')
    print("This is the CACERT URL:", LDAP_CACERT_URL)
    if LDAP_CACERT_URL:
        with urllib.request.urlopen(LDAP_CACERT_URL) as response, open(LDAP_CACERTFILE, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    else:
        print("No LDAP_CACERT_URL")
        pass
elif os.path.exists(LDAP_CACERTFILE):
    AUTH_LDAP_START_TLS = True
else:
    AUTH_LDAP_START_TLS = False

print("this is the AUTH_LDAP_START_TLS:", AUTH_LDAP_START_TLS)

if os.path.exists(LDAP_CACERTFILE):
    AUTH_LDAP_GLOBAL_OPTIONS = {
        ldap.OPT_X_TLS_CACERTFILE: LDAP_CACERTFILE
    }
else:
    pass
    # AUTH_LDAP_CONNECTION_OPTIONS = {
    #     ldap.OPT_REFERRALS: 0
    # }

AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_REFERRALS: 0
}

AUTH_LDAP_GROUP_TYPE = PosixGroupType()
# LDAP authentication configuration
AUTH_LDAP_SERVER_URI = "ldap://"+LDAP_HOST
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,"+LDAP_BASEDN,
                                   ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,"+LDAP_BASEDN,
                                    ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
)

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'openshift/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

from . import database

DATABASES = {
    'default': database.config()
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS =( os.path.join(STATIC_ROOT, 'css/'),
                    os.path.join(STATIC_ROOT, 'javascript/'),
                    os.path.join(STATIC_ROOT, 'images/'),
                    os.path.join(STATIC_ROOT, 'autopatch/')
)
