import json

from django.conf import settings
from django.core.urlresolvers import reverse

from irgsh_web import utils

def send_spec_description(spec_id, changelog, control):
    host = settings.SERVER.rstrip('/')
    path = reverse('build_spec_description', args=[str(spec_id)])
    url = '%s%s' % (host, path)

    param = {'changelog': open(changelog, 'rb'),
             'control': open(control, 'rb')}
    return json.loads(utils.send_message(url, param))

