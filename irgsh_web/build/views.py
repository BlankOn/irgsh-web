import tempfile
import os
import gzip
import shutil
from datetime import datetime
try:
    import simplejson as json
except ImportError:
    import json

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.conf import settings
from django.utils.translation import ugettext as _

try:
    from debian.deb822 import Packages
    from debian.changelog import Changelog
except ImportError:
    from debian_bundle.deb822 import Packages
    from debian_bundle.changelog import Changelog

from . import utils, models, tasks
from .models import BuildTask, Distribution, Specification, BuildTaskLog, \
                    Builder
from .forms import SpecificationForm
from irgsh_web.repo.models import Package as RepoPackage

JSON_MIME = 'application/json'
JSON_MIME = 'plain/text'

def _task_id_required(func):
    def _func(request, task_id, *args, **kwargs):
        task = get_object_or_404(BuildTask, task_id=task_id)
        return func(request, task, *args, **kwargs)
    return _func

def _spec_id_required(func):
    def _func(request, spec_id, *args, **kwargs):
        spec = get_object_or_404(Specification, pk=int(spec_id))
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

def _set_description(spec, fcontrol, fchangelog):
    # Get packages info
    packages = Packages.iter_paragraphs(fcontrol)
    info = utils.get_package_info(packages)
    name = info['name']

    # The package must have a name
    if name is None:
        spec.status = -2
        spec.save()
        return {'status': 'fail', 'code': 406, 'msg': _('Package name not found')}

    # Check if this package is registered
    try:
        pkg = RepoPackage.objects.get(name=name,
                                      distribution=spec.distribution.repo)
    except RepoPackage.DoesNotExist:
        spec.status = -2
        spec.save()
        return {'status': 'fail', 'code': 406,
                'msg': _('Unregistered package: %(name)s') % {'name': name}}

    # Get package version
    c = Changelog(fchangelog)
    version = str(c.version)

    # Save packages info
    spec.package = pkg
    spec.version = version
    spec.save()

    utils.store_package_info(spec, info)

    return {'status': 'ok', 'package': name}

@_post_required
@_task_id_required
@_json_result
def build_log(request, task):
    '''
    [API] Set build log
    '''
    if not request.FILES.has_key('log'):
        return HttpResponse(status=400)

    fin = request.FILES['log']

    logdir = os.path.join(settings.LOG_PATH, task.task_id)
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    target = os.path.join(logdir, 'build.log.gz')

    fout = open(target, 'wb')
    fout.write(fin.read())
    fout.close()

    task.build_log = datetime.now()
    task.save()

    task.add_log(_('Build log added'))

    return {'status': 'ok'}

@_post_required
@_task_id_required
@_json_result
def update_status(request, task):
    '''
    [API] Update task status
    '''
    try:
        status = int(request.POST['status'])
        builder_name = request.POST['builder']
    except (ValueError, KeyError):
        return HttpResponse(status=400)

    status_list = dict(models.BUILD_TASK_STATUS)
    if not status in status_list:
        return HttpResponse(status=400)

    if task.builder is None:
        try:
            task.builder = Builder.objects.get(name=builder_name)
            task.add_log(_('Task picked up by %(builder)s') % \
                           {'builder': task.builder})
        except Builder.DoesNotExist:
            # TODO: fatal error
            pass

    task.status = status
    task.save()

    task.add_log(status_list[status])

    if status == 202: # Package uploaded
        # TODO: Start rebuilding repo if packages
        #       from all builders (archs) have been uploaded
        pass

    elif status == -1: # Failed
        spec = task.specification
        spec.status = -1
        spec.save()

    return {'status': 'ok'}

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

@_post_required
@_spec_id_required
@_json_result
def spec_description(request, spec):
    '''
    [API] Update package information

    - source package
    - package list
    '''
    if not request.FILES.has_key('control') or \
       not request.FILES.has_key('changelog'):
        return HttpResponse(status=400)

    files = ['control', 'changelog']

    try:
        tmpdir = tempfile.mkdtemp()

        for fname in files:
            fin = request.FILES[fname]
            f = open(os.path.join(tmpdir, '%s.gz' % fname), 'wb')
            f.write(fin.read())
            f.close()

        gz = [gzip.open(os.path.join(tmpdir, '%s.gz' % fname))
              for fname in files]
        return _set_description(spec, gz[0], gz[1])

    finally:
        shutil.rmtree(tmpdir)

@_spec_id_required
@_json_result
def spec_status(request, spec):
    if request.method == 'POST':
        try:
            status = int(request.POST['status'])
            spec.status = status
            spec.save()
        except ValueError:
            return HttpResponse(status=400)

    return {'status': 'ok', 'code': spec.status, 'msg': spec.get_status_display()}

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

