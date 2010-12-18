from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import BuildTask

def _task_id_required(func):
    def _func(request, task_id, *args):
        task = get_object_or_404(BuildTask, pk=task_id)
        return func(request, task, *args)
    return _func

def _post_required(func):
    def _func(request, *args):
        if request.method != 'POST':
            return HttpResponse(status=405)
        return func(request, *args)
    return _func

@_post_required
@_task_id_required
def debian_info(request, task):
    '''
    [API] Update package information

    - source package
    - package list
    '''
    pass

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

