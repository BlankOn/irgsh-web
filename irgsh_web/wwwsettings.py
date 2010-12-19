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
}
CELERY_DEFAULT_QUEUE = 'celery'
CELERY_DEFAULT_EXCHANGE = 'celery'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'

BROKER_HOST = '192.168.56.180'
BROKER_PORT = 5672
BROKER_USER = 'irgsh'
BROKER_PASSWORD = 'irgsh'
BROKER_VHOST = 'irgsh'

