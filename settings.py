import os
import os.path
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
# Django settings for web_builder project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'web-builder.db'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = unicode(os.path.join(PROJECT_PATH, 'media')) 

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'i6$x6c38p5#8a^qj6_j^@3@32pz!7k$ed2s+qebqa^yp=xxc1o'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'web_builder.urls'

TEMPLATE_DIRS = (
     os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django_openid_auth',
    'django_xmlrpc',
    'jobs',
)

AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

OPENID_CREATE_USERS = True
OPENID_UPDATE_DETAILS_FROM_SREG = True
LOGIN_URL = '/o/login'
LOGIN_REDIRECT_URL = '/o'
OPENID_SSO_SERVER_URL = "http://82.181.46.34:8081/o/"
FULL_LOGOUT_URL = "http://82.181.46.34:8081/logout"
OPENID_USE_AS_ADMIN_LOGIN = True

XMLRPC_METHODS = (
    ('jobs.views.get_new_tasks', 'get_new_tasks'),
    ('jobs.views.get_task_info', 'get_task_info'),
    ('jobs.views.populate_debian_info', 'populate_debian_info'),
    ('jobs.views.set_debian_copy', 'set_debian_copy'),
    ('jobs.views.set_orig_copy', 'set_orig_copy'),
    ('jobs.views.start_running', 'start_running'),
    ('jobs.views.start_assigning', 'start_assigning'),
    ('jobs.views.set_orig_copy', 'set_orig_copy'),
    ('jobs.views.task_init_failed', 'task_init_failed'),
    ('jobs.views.start_running', 'start_running'),
    ('jobs.views.assign_task', 'assign_task'),
    ('jobs.views.assignment_download', 'assignment_download'),
    ('jobs.views.assignment_environment', 'assignment_environment'),
    ('jobs.views.assignment_building', 'assignment_building'),
    ('jobs.views.assignment_upload', 'assignment_upload'),
    ('jobs.views.assignment_complete', 'assignment_complete'),
    ('jobs.views.assignment_fail', 'assignment_fail'),
    ('jobs.views.assignment_set_log_url', 'assignment_set_log_url'),
)
