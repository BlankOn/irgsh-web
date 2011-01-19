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
                    Builder, Package, SpecificationLog
from .forms import SpecificationForm
from irgsh_web.repo.models import Package as RepoPackage

JSON_MIME = 'application/json'
JSON_MIME = 'plain/text'

def _set_spec_status(spec_id, status):
    Specification.objects.filter(pk=spec_id).update(status=status)

def _rebuild_repo(spec):
    # Start rebuilding repo if
    # all builders have uploaded their packages
    # and source package has been uploaded
    tasks = BuildTask.objects.filter(specification=spec)
    all_uploaded = all([task.status == 999 for task in tasks])

    if all_uploaded:
        # Atomicaly update spec status to building repository.
        total = Specification.objects.filter(pk=spec.id) \
                                     .filter(status=105) \
                                     .update(status=200)

        if total > 0:
            # Successfully updated the spec => got token
            specification = Specification.objects.get(pk=spec.id)
            utils.rebuild_repo(specification)

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
        _set_spec_status(spec.id, -2)
        spec.add_log(_('Package rejected (package name not found)'))
        return {'status': 'fail', 'code': 406, 'msg': _('Package name not found')}

    # Check if this package is registered
    try:
        pkg = RepoPackage.objects.get(name=name,
                                      distribution=spec.distribution.repo)
    except RepoPackage.DoesNotExist:
        _set_spec_status(spec.id, -2)
        spec.add_log(_('Package rejected (unregistered package: %(name)s)') % \
                     {'name': name})
        return {'status': 'fail', 'code': 406,
                'msg': _('Unregistered package: %(name)s') % {'name': name}}

    # Get package version
    c = Changelog(fchangelog)
    version = str(c.version)

    dist = c.distributions.split('-')[0]
    target_dist = spec.distribution.repo.name.split('-')[0]
    if dist != target_dist:
        _set_spec_status(spec.id, -2)
        spec.add_log(_('Package rejected (distribution mismatch: %(dist)s)') % \
                     {'dist': dist})
        return {'status': 'fail', 'code': 406,
                'msg': _('Distribution mismatch: %(dist)s') % {'dist': dist}}

    # Save packages info
    spec.package = pkg
    spec.version = version
    spec.save()

    utils.store_package_info(spec, info)

    return {'status': 'ok', 'package': name}

@_post_required
@_task_id_required
@_json_result
def task_log(request, task):
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
def task_status(request, task):
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
            task.assigned = datetime.now()
            task.add_log(_('Task picked up by %(builder)s') % \
                           {'builder': task.builder})
        except Builder.DoesNotExist:
            task.status = -1
            task.save()
            _set_spec_status(spec.specification.id, -1)
            task.add_log(_('Failed. Unregistered builder tried to pick the task: %(name)s') % \
                         {'name': builder_name})
            return HttpResponse(status=400)

    if task.status >= 0 and (status > task.status or status < 0):
        # Only update when the new status is larger (showing progression)
        # or failed/cancelled
        task.status = status
    task.save()

    task.add_log(status_list[status])

    if status == 999:
        # Finished
        spec = task.specification
        _rebuild_repo(task.specification)

    elif status == -1:
        # Task failed
        spec = task.specification
        _set_spec_status(spec.id, -1)

    return {'status': 'ok'}

@_task_id_required
def task_show(request, task):
    '''
    Show build task information

    - status
    - logs
    '''
    logs = BuildTaskLog.objects.filter(task=task)
    context = {'task': task,
               'build': task.specification,
               'logs': logs}
    return render_to_response('build/task_show.html', context,
                              context_instance=RequestContext(request))

@_spec_id_required
def spec_show(request, spec):
    tasks = BuildTask.objects.filter(specification=spec).select_related()
    packages = Package.objects.filter(specification=spec)

    logs = []
    logs += [(log.created, '', str(log), 'spec', log)
             for log in SpecificationLog.objects.filter(spec=spec)]
    logs += [(log.created, getattr(log.task.builder, 'name', None), str(log), 'task', log)
             for log in BuildTaskLog.objects.filter(task__specification=spec) \
                                            .select_related(depth=3)]
    logs = reversed(sorted(logs))

    task_logs = BuildTaskLog.objects.filter(task__specification=spec)

    context = {'build': spec,
               'tasks': tasks,
               'packages': packages,
               'logs': logs}
    return render_to_response('build/spec_show.html', context,
                              context_instance=RequestContext(request))

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
            _set_spec_status(spec.id, status)
            if status == 104:
                _rebuild_repo(spec)
        except ValueError:
            return HttpResponse(status=400)

    else:
        status = spec.status

    return {'status': 'ok', 'code': status, 'msg': spec.get_status_display()}

def spec_list(request):
    builds = Specification.objects.all().select_related()
    context = {'builds': builds}
    return render_to_response('build/spec_list.html', context,
                              context_instance=RequestContext(request))

@_spec_id_required
@_json_result
@_post_required
def repo_status(request, spec):
    arch = request.POST.get('arch', None)
    status = request.POST.get('status', None)

    try:
        status = int(status)
        if not status in [-1, 0, 1]:
            raise ValueError
    except ValueError:
        return HttpResponse(status=406)

    if arch is not None:
        archs = spec.distribution.repo.architectures
        arch_valid = len(archs.filter(name=arch)) > 0
        if not arch_valid:
            return HttpResponse(status=406)

    if status == -1:
        # FAIL
        _set_spec_status(spec.id, -1)

        if arch is None:
            spec.add_log('Rebuilding repository failed')
        else:
            spec.add_log('Rebuilding repository for %s failed' % arch)

    elif status == 0:
        # SUCCESS
        spec.add_log('Rebuilding repository for %s succeeded' % arch)

    elif status == 1:
        # COMPLETE
        _set_spec_status(spec.id, 999)

        spec.add_log('Repository rebuilt, all done.')

    return {'status': 'ok', 'code': status}

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
            spec.add_log('Build specification created')

            tasks.InitSpecification.apply_async(args=(spec.id,))
            print 'task init:', data
            print '- spec:', spec

            url = reverse('build_spec_show', args=[spec.id])
            return HttpResponseRedirect(url)
    else:
        form = SpecificationForm()

    context = {'form': form}
    return render_to_response('build/submit.html', context,
                              context_instance=RequestContext(request))

def summary(request):
    '''
    Show summary
    '''
    builders = Builder.objects.all().select_related()
    specs = Specification.objects.all().select_related()[:15]
    context = {'builders': builders,
               'builds': specs}
    return render_to_response('build/summary.html', context,
                              context_instance=RequestContext(request))

def index(request):
    return HttpResponse()

def builder_list(request):
    pass

def builder_show(request, name):
    builder = get_object_or_404(Builder, name=name)
    tasks = BuildTask.objects.filter(builder=builder) \
                             .order_by('-created') \
                             .select_related(depth=2)[:10]
    context = {'builder': builder,
               'tasks': tasks}
    return render_to_response('build/builder_show.html', context,
                              context_instance=RequestContext(request))

