from django.http import HttpResponsePermanentRedirect
from django.contrib.sites.models import Site

def _redirect(path):
    site = Site.objects.get_current()
    url = 'http://%s%s' % (site.domain, path)
    return HttpResponsePermanentRedirect(url)

def redirect_spec(request, spec_id):
    return _redirect('/build/%s/' % spec_id)

def redirect_task(request, task_id):
    return _redirect('/task/%s/' % task_id)

def redirect_user(request, name):
    return _redirect('/user/%s/' % name)

