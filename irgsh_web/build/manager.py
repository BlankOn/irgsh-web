import json

from django.conf import settings
from django.core.urlresolvers import reverse

from irgsh_web import utils

def send_control(task_id, fname):
    host = settings.SERVER.rstrip('/')
    url = URL_CONTROL % {'host': host, 'task_id': task_id}

    param = {'control': open(fname, 'rb'),
             'builder': settings.NODE_NAME}
    utils.send_message(url, param)

def send_spec_description(spec_id, changelog, control):
    host = settings.SERVER.rstrip('/')
    path = reverse('build_spec_description', args=[str(spec_id)])
    url = '%s%s' % (host, path)

    param = {'changelog': open(changelog, 'rb'),
             'control': open(control, 'rb')}
    return json.loads(utils.send_message(url, param))

import urllib2

from .conf import settings
from .utils import send_message

FAILED = -1
WAITING = 0
PREPARING = 100
DOWNLOADING_SOURCE = 101
DOWNLOADING_ORIG = 102
BUILDING = 102
BUILT = 104
UPLOADING = 201
UPLOADED = 202
FINISHED = 999

URL_UPDATE_STATUS = '%(host)s/build/%(task_id)s/status/'
URL_BUILD_LOG = '%(host)s/build/%(task_id)s/log/'
URL_CONTROL = '%(host)s/build/%(task_id)s/info/'

def update_status(task_id, status):
    host = settings.SERVER.rstrip('/')
    url = URL_UPDATE_STATUS % {'host': host, 'task_id': task_id}

    param = {'status': status,
             'builder': settings.NODE_NAME}
    send_message(url, param)

def send_log(task_id, fname):
    host = settings.SERVER.rstrip('/')
    url = URL_BUILD_LOG % {'host': host, 'task_id': task_id}

    param = {'log': open(fname, 'rb'),
             'builder': settings.NODE_NAME}
    send_message(url, param)

def send_control(task_id, fname):
    host = settings.SERVER.rstrip('/')
    url = URL_CONTROL % {'host': host, 'task_id': task_id}

    param = {'control': open(fname, 'rb'),
             'builder': settings.NODE_NAME}
    send_message(url, param)

