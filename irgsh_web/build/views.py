import tempfile
try:
    import simplejson as json
except ImportError:
    import json

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

try:
    from debian.deb822 import Packages
except ImportError:
    from debian_bundle.deb822 import Packages

from . import utils, models, tasks
from .models import BuildTask, Distribution, Specification
from .forms import SpecificationForm

JSON_MIME = 'application/json'
JSON_MIME = 'plain/text'

def _task_id_required(func):
    def _func(request, task_id, *args, **kwargs):
        task = get_object_or_404(BuildTask, pk=task_id)
        return func(request, task, *args, **kwargs)
    return _func

def _spec_id_required(func):
    def _func(request, spec_id, *args, **kwargs):
        spec = get_object_or_404(Specification, pk=spec_id)
        return func(request, spec, *args, **kwargs)
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
            return HttpResponse(json.dumps(res), mimetype=JSON_MIME)
        elif type(res) == tuple:
            out, opts = res
            return HttpResponse(json.dumps(out), mimetype=JSON_MIME,
                                **opts)
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

@_spec_id_required
def show_spec(request, spec):
    return HttpResponse('show spec: %s' % spec)

@login_required
def submit(request):
    if request.method == 'POST':
        form = SpecificationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            dist = Distribution.objects.get(pk=data['distribution'])

            spec = Specification()
            spec.distribution = dist
            spec.submitter = request.user
            spec.source = data['source']
            spec.orig = data['orig']
            spec.source_type = data['source_type']
            spec.source_opts = data['source_opts']
            spec.save()

            tasks.InitSpecification.apply_async(args=(spec.id,))
            print 'task init:', data
            print '- spec:', spec

            url = reverse('build_show_spec', args=[spec.id])
            return HttpResponseRedirect(url)
    else:
        form = SpecificationForm()

    context = {'form': form}
    return render_to_response('build/submit.html', context,
                              context_instance=RequestContext(request))

def index(request):
    '''
    Show list of build tasks
    '''
    pass

