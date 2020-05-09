#  settings for  project.

import os
from environs import Env
import json
import uuid
from halo_flask.const import LOC,DEV,TST,PRD

print("start base")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print('BASE_DIR : {}'.format(BASE_DIR))

env = Env()
THE_ENV=os.path.join(BASE_DIR,'env','.env')
env.read_env(path=THE_ENV)
print('The .env file has been loaded. env: '+str(THE_ENV))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)
print("DEBUG=" + str(DEBUG))

ENV = env.str('FLASK_ENV', default='production') # development,testing, production
SQLALCHEMY_DATABASE_URI = env.str('DATABASE_URL')
SECRET_KEY = env.str('SECRET_KEY')
BCRYPT_LOG_ROUNDS = env.int('BCRYPT_LOG_ROUNDS', default=13)
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = env.bool('DEBUG_TB_INTERCEPT_REDIRECTS', default=False)
CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = env.bool('SQLALCHEMY_TRACK_MODIFICATIONS', default=False)
WEBPACK_MANIFEST_PATH = 'webpack/manifest.json'


###### setup environment for testing

ENV_TYPE = LOC
#os.environ["HALO_TYPE"] = ENV_TYPE

ENV_NAME = LOC  # env.str('ENV_NAME')
#os.environ["HALO_STAGE"] = ENV_NAME  # done in settings json file

FUNC_NAME = env.str('FUNC_NAME', 'halo_flask')
#os.environ['HALO_FUNC_NAME'] = FUNC_NAME  # done in settings json file
#os.environ['HALO_APP_NAME'] = 'app'  #done in settings json file
APP_NAME = env.str('APP_NAME', 'halo')

SERVER_LOCAL = env.bool('SERVER_LOCAL', default=True)

# SECURITY WARNING: keep the secret key used in production secret!
# Make this unique, and don't share it with anybody.
SECRET_KEY = env('SECRET_KEY')


###
# Given a version number MAJOR.MINOR.PATCH, increment the:
#
# MAJOR version when you make incompatible  changes,
# MINOR version when you add functionality in a backwards-compatible manner, and
# PATCH version when you make backwards-compatible bug fixes.
###

title = 'webfront'
author = 'Author'
copyright = 'Copyright 2017-2018 ' + author
major = '1'
minor = '1'
patch = '52'
version = major + '.' + minor + '.' + patch
# year.month.day.optional_revision  i.e 2016.05.03 for today
rev = 1
build = '2018.10.10.' + str(rev)
generate = '2018.10.13.19:06:07'
print("generate=" + generate)


def get_version():
    """
    Return package version as listed in  env file
    """
    return version + "/" + build + ' (' + ENV_NAME + ')'


VERSION = get_version()
print(VERSION)

APPEND_SLASH = True

SERVER = env('SERVER_NAME')
HALO_HOST = 'halo_flask'
ALLOWED_HOSTS = ['*','127.0.0.1',SERVER]

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DB_VER = env('DB_VER')
PAGE_SIZE = env.int('PAGE_SIZE', default=5)
#DATABASES = {
#   'default': env.db(),
#}

def get_cache():
  return {
      'default': env.cache()
    }

#CACHES = get_cache()

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LOCALE_CODE = 'en-US'
LANGUAGE_CODE = 'en'

LANGUAGES = (
    #('en', _('English')),
    #('nl', _('Dutch')),
    #('he', _('Hebrew')),
)

GET_LANGUAGE = True

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'


PROJECT_APPS = (
    'api',
)

CORS_ORIGIN_ALLOW_ALL = True
#change to proper site in production
#HOME_DOMAIN = env('HOME_DOMAIN')#'amazon.com'
#CORS_ORIGIN_WHITELIST = (
#    HOME_DOMAIN,
#    'localhost:8000',
#    '127.0.0.1:9000'
#)

STATIC_URL = '/static1/'

STATIC_ROOT = os.path.join(BASE_DIR, "halo_flask/api/static")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    '/var/www/static/',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'main_formatter': {
            'format': '%(levelname)s:%(name)s: %(message)s '
                      '%(asctime)s; %(filename)s:%(lineno)d',
            'datefmt': "%Y-%m-%d %H:%M:%S",
            'class': "pythonjsonlogger.jsonlogger.JsonFormatter",
        },
        'main_formatter_old': {
            'format': '%(levelname)s:%(name)s: %(message)s '
                      '(%(asctime)s; %(filename)s:%(lineno)d)',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
    #    'file': {
    #        'level': 'DEBUG',
    #        'class': 'logging.FileHandler',
    #        'filename': '/path/to/django/debug.log',
    #    },
        #    'console': {
        #        'level': 'ERROR',
        #        'filters': ['require_debug_false'],
        #        'class': 'logging.StreamHandler',
        #        'formatter': 'main_formatter',
        #    },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'console_debug_false': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': True,
        },
        'halo_flask.halo_flask.views': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.halo_flask.apis': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.halo_flask.events': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.halo_flask.mixin': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.halo_flask.models': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.halo_flask.util': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.halo_flask.ssm': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
    },
}

USER_HEADERS = 'Mozilla/5.0'

MIXIN_HANDLER = 'loader1service.api.mixin.mixin_handler'

SERVICE_READ_TIMEOUT_IN_SC = 3  # in seconds = 300 ms

SERVICE_CONNECT_TIMEOUT_IN_SC = 3  # in seconds = 300 ms

RECOVER_TIMEOUT_IN_SC = 0.5  # in seconds = 500 ms

MINIMUM_SERVICE_TIMEOUT_IN_SC = 0.1  # in seconds = 100 ms

HTTP_MAX_RETRY = 4

THRIFT_MAX_RETRY = 4

HTTP_RETRY_SLEEP = 10 #0.100  # in seconds = 100 ms

FRONT_WEB = False

FRONT_API = False

INSTANCE_ID = uuid.uuid4().__str__()[0:4]

LOG_SAMPLE_RATE = 0.05  # 5%

ERR_MSG_CLASS = 'halo_flask.mixin_err_msg'

SSM_TYPE = env.str('SSM_TYPE',default='NONE')
print('SSM_TYPE='+SSM_TYPE)

EVENTS_INGESTED = env.int('EVENTS_INGESTED',default=50)

EVENTS_INGESTED_SLEEP = env.int('EVENTS_INGESTED_SLEEP',default=5)

file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir, 'halo_flask','schema',"saga_schema.json")
with open(file_path) as f1:
    SAGA_SCHEMA = json.load(f1)

#######################################################################################3


API_CONFIG = None
API_SETTINGS = ENV_NAME + '_api_settings.json'

file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir, 'env','api',API_SETTINGS)
with open(file_path, 'r') as fi:
    API_CONFIG = json.load(fi)
    print("api_config:" + str(API_CONFIG))

file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir, 'env','loc_settings.json')
with open(file_path, 'r') as fi:
    LOC_TABLE = json.load(fi)
    print("loc_settings:" + str(LOC_TABLE))


BUSINESS_EVENT_MAP = None
EVENT_SETTINGS = ENV_NAME + '_event_settings.json'
file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir,'env','config', EVENT_SETTINGS)
with open(file_path, 'r') as fi:
    map = json.load(fi)
    BUSINESS_EVENT_MAP = {}
    for clazz in map:
        bqs = map[clazz]
        dictx = {}
        for bq in bqs:
            BUSINESS_EVENT_MAP[clazz] = bq
            val = bqs[bq]
            dict = {}
            for action in val:
                item = val[action]
                file_path_data = os.path.join(file_dir,'env','config', item['url'])
                print(file_path_data)
                with open(file_path_data, 'r') as fx:
                     data = json.load(fx)
                     dict[action] = { item['type'] : data }
            dictx[bq] = dict
        BUSINESS_EVENT_MAP[clazz] = dictx

MAPPING = None
file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir, 'env','config','mapping.json')
with open(file_path, 'r') as fi:
    MAPPING = json.load(fi)
    print("mapping:" + str(MAPPING))


HALO_CONTEXT_LIST = []
HALO_CONTEXT_CLASS = None
REQUEST_FILTER_CLASS = None
REQUEST_FILTER_CLEAR_CLASS = None
CIRCUIT_BREAKER = False

print('The settings file has been loaded.')
