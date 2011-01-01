from irgsh_web.basesettings import *
ROOT_URLCONF = 'irgsh_web.urls'

XMLRPC_METHODS = ()

import djcelery
djcelery.setup_loader()

CELERY_QUEUES = {
    'celery': {
        'exchange': 'celery',
        'exchange_type': 'direct',
    },
    'specinit': {
        'exchange': 'specinit',
        'exchange_type': 'direct',
    },
}
CELERY_DEFAULT_QUEUE = 'celery'
CELERY_DEFAULT_EXCHANGE = 'celery'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'

BROKER_HOST = '192.168.56.180'
BROKER_PORT = 5672
BROKER_USER = 'irgsh'
BROKER_PASSWORD = 'irgsh'
BROKER_VHOST = 'irgsh'

BROKER_HOST = '127.0.0.1'

import os
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_TARGET = 'static/assets/'
if not os.path.exists(DOWNLOAD_TARGET):
    os.makedirs(DOWNLOAD_TARGET)

SERVER = 'http://localhost:8000/'

