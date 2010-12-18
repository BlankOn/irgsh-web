import tempfile
try:
    import simplejson as json
except ImportError:
    import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

try:
    from debian.deb822 import Packages
except ImportError:
    from debian_bundle.deb822 import Packages

from . import utils, models
from .models import BuildTask

def _task_id_required(func):
    def _func(request, task_id, *args, **kwargs):
        task = get_object_or_404(BuildTask, pk=task_id)
        return func(request, task, *args, **kwargs)
    return _func

def _post_required(func):
    def _func(request, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponse(status=405)
        return func(request, *args, **kwargs)
    return _func

def _json_result(func):
    def _func(request, *args, **kwargs):
        res = func(request, *args, **kwargs)
        if type(res) == dict:
            return HttpResponse(json.dumps(res))
        elif type(res) == tuple:
            out, opts = res
            return HttpResponse(json.dumps(out), **opts)
        return res
    return _func

@_post_required
@_task_id_required
@_json_result
def debian_info(request, task):
    '''
    [API] Update package information

    - source package
    - package list
    '''
    if not request.FILES.has_key('control'):
        return HttpResponse(status=400)

    packages = Packages.iter_paragraphs(request.FILES['control'])
    info = utils.get_package_info(packages)
    utils.store_package_info(task.specification, info)

    name = None
    names = [pkg['name'] for pkg in info if info['type'] == models.SOURCE]
    if len(names) > 0:
        name = names[0]

    return {'status': 'ok', 'package': name}

@_post_required
@_task_id_required
def report_built(request, task):
    '''
    [API] Packages have been built, ready to upload
    '''
    pass

@_post_required
@_task_id_required
def report_uploaded(request, task):
    '''
    [API] Packages have been uploaded, repository needs to be rebuilt
    '''
    pass

@_task_id_required
def show(request, task):
    '''
    Show build task information

    - status
    - logs
    '''
    pass

def index(request):
    '''
    Show list of build tasks
    '''
    pass

