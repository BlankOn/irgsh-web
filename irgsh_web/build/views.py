import tempfile
import os
import gzip
import shutil
from datetime import datetime
import mimetypes
import stat
try:
    import simplejson as json
except ImportError:
    import json

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.views.static import was_modified_since
from django.utils.http import http_date

try:
    from debian.deb822 import Packages, Sources
    from debian.changelog import Changelog
except ImportError:
    from debian_bundle.deb822 import Packages, Sources
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

def _paginate(queryset, total, page):
    try:
        page = int(page)
        if page < 0: page = 1
    except ValueError:
        page = 1

    paginator = Paginator(queryset, total)

    try:
        items = paginator.page(page)
    except (EmptyPage, InvalidPage):
        items = paginator.page(paginator.num_pages)

    return items

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

def _builder_name_required(func):
    def _func(request, name, *args, **kwargs):
        builder = get_object_or_404(Builder, name=name)
        return func(request, builder, *args, **kwargs)
    return _func

def _username_required(func):
    def _func(request, name, *args, **kwargs):
        user = get_object_or_404(User, username=name)
        return func(request, user, *args, **kwargs)
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

    # Get last changelog content
    last_changelog = None
    if len(c._blocks) > 0:
        last_changelog = str(c._blocks[0]).replace('\n\n', '\n').strip()

    # Save packages info
    spec.package = pkg
    spec.version = version
    spec.changelog = last_changelog
    spec.save()

    utils.store_package_info(spec, info)

    return {'status': 'ok', 'package': name}

@_task_id_required
def task_build_log(request, task):
    fullpath = os.path.join(settings.LOG_PATH, 'task',
                            task.task_id, 'build.log.gz')
    if not os.path.exists(fullpath):
        raise Http404()

    # From Django source code: django/views/static.py
    statobj = os.stat(fullpath)
    mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified(mimetype=mimetype)
    contents = open(fullpath, 'rb').read()
    response = HttpResponse(contents, mimetype=mimetype)
    response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    response["Content-Length"] = len(contents)
    return response

@_post_required
@_task_id_required
@_json_result
def task_log(request, task):
    # TODO access should be limited from client authenticated HTTPS only
    '''
    [API] Set build log
    '''
    if not request.FILES.has_key('log'):
        return HttpResponse(status=400)

    fin = request.FILES['log']

    logdir = os.path.join(settings.LOG_PATH, 'task', task.task_id)
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    target = os.path.join(logdir, 'build.log.gz')

    fout = open(target, 'wb')
    fout.write(fin.read())
    fout.close()

    task.build_log = datetime.now()
    task.save()

    task.add_log(_('Build log added'))

    task.update_builder()

    return {'status': 'ok'}

@_post_required
@_task_id_required
@_json_result
def task_status(request, task):
    # TODO access should be limited from client authenticated HTTPS only
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
        spec.add_log(_('Builder %(builder)s finished') % \
                       {'builder': task.builder})
        _rebuild_repo(task.specification)

    elif status == -1:
        # Task failed
        spec = task.specification
        spec.add_log(_('Builder %(builder)s failed') % \
                       {'builder': task.builder})
        _set_spec_status(spec.id, -1)

    task.update_builder()

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

    # Combined build and task logs
    logs = []
    logs += [(log.created, '', str(log), 'spec', log)
             for log in SpecificationLog.objects.filter(spec=spec)]
    logs += [(log.created, getattr(log.task.builder, 'name', None), str(log), 'task', log)
             for log in BuildTaskLog.objects.filter(task__specification=spec) \
                                            .select_related(depth=3)]
    logs = reversed(sorted(logs))

    task_logs = BuildTaskLog.objects.filter(task__specification=spec)

    # Source files
    sources = []
    dsc = spec.dsc()
    if dsc is not None:
        dsc_path = os.path.join(settings.DOWNLOAD_TARGET,
                                str(spec.id), dsc)
        if os.path.exists(dsc_path):
            sources.append((reverse('build_spec_source',
                                    args=[spec.id, dsc]), dsc))

            src = Sources(open(dsc_path))
            for info in src['Files']:
                fname = info['name']
                path = os.path.join(settings.DOWNLOAD_TARGET,
                                    str(spec.id), fname)
                if os.path.exists(path):
                    sources.append((reverse('build_spec_source',
                                            args=[spec.id, fname]), fname))

    context = {'build': spec,
               'tasks': tasks,
               'packages': packages,
               'logs': logs,
               'sources': sources}
    return render_to_response('build/spec_show.html', context,
                              context_instance=RequestContext(request))

@_post_required
@_spec_id_required
@_json_result
def spec_description(request, spec):
    # TODO access should be limited from client authenticated HTTPS only
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
    # TODO access should be limited from client authenticated HTTPS only
    if request.method == 'POST':
        try:
            status = int(request.POST['status'])

            status_list = dict(models.SPECIFICATION_STATUS)
            assert status in status_list

            _set_spec_status(spec.id, status)
            spec.add_log(status_list[status])

            if status == 104:
                _rebuild_repo(spec)
        except (ValueError, AssertionError):
            return HttpResponse(status=400)

    else:
        status = spec.status

    return {'status': 'ok', 'code': status, 'msg': spec.get_status_display()}

def spec_list(request):
    build_list = Specification.objects.all().select_related()
    builds = _paginate(build_list, 50, request.GET.get('page', 1))
    context = {'builds': builds}
    return render_to_response('build/spec_list.html', context,
                              context_instance=RequestContext(request))

@_spec_id_required
def spec_source(request, spec, path):
    fullpath = os.path.join(settings.DOWNLOAD_TARGET,
                            str(spec.id), path)
    if not os.path.exists(fullpath):
        raise Http404()

    # From Django source code: django/views/static.py
    statobj = os.stat(fullpath)
    mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified(mimetype=mimetype)
    contents = open(fullpath, 'rb').read()
    response = HttpResponse(contents, mimetype=mimetype)
    response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    response["Content-Length"] = len(contents)
    return response

@_spec_id_required
@_json_result
@_post_required
def repo_status(request, spec):
    # TODO access should be limited from client authenticated HTTPS only
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
            spec.source_opts_raw = data['source_opts']
            spec.source_opts = utils.build_source_opts(data['source_type'],
                                                       data['source_opts'])
            spec.save()
            spec.add_log('Build specification created')

            tasks.InitSpecification.apply_async(args=(spec.id,))
            print 'task init:', data
            print '- spec:', spec

            url = reverse('build_spec_show', args=[spec.id])
            return HttpResponseRedirect(url)
    else:
        initial = {}
        if request.GET.has_key('copy'):
            try:
                spec_id = int(request.GET['copy'])
                spec = Specification.objects.get(pk=spec_id)
                initial = {'distribution': spec.distribution.id,
                           'source': spec.source,
                           'source_opts': spec.source_opts_raw,
                           'source_type': spec.source_type,
                           'orig': spec.orig}
            except (ValueError, Specification.DoesNotExist):
                return HttpResponseRedirect(reverse(submit))
        form = SpecificationForm(initial=initial)

    context = {'form': form}
    return render_to_response('build/submit.html', context,
                              context_instance=RequestContext(request))

def summary(request):
    '''
    Show summary
    '''
    builders = Builder.objects.all().select_related()

    spec_limit = 15
    all_specs = Specification.objects.all()
    specs = all_specs.select_related()[:spec_limit]

    context = {'builders': builders,
               'builds': specs,
               'more_builds': len(all_specs) > spec_limit}
    return render_to_response('build/summary.html', context,
                              context_instance=RequestContext(request))

def index(request):
    return HttpResponse()

def builder_list(request):
    pass

@_builder_name_required
def builder_show(request, builder):
    limit = 10
    all_tasks = BuildTask.objects.filter(builder=builder)
    tasks = all_tasks.select_related(depth=2)[:limit]
    context = {'builder': builder,
               'tasks': tasks,
               'more_tasks': len(all_tasks) > limit}
    return render_to_response('build/builder_show.html', context,
                              context_instance=RequestContext(request))

@_builder_name_required
def builder_task(request, builder):
    task_list = BuildTask.objects.filter(builder=builder)
    tasks = _paginate(task_list, 50, request.GET.get('page', 1))

    context = {'builder': builder,
               'tasks': tasks}
    return render_to_response('build/builder_task.html', context,
                              context_instance=RequestContext(request))

@_username_required
def user_show(request, user):
    builds = Specification.objects.filter(submitter=user)

    # Last build
    last_build = None
    if len(builds) > 0:
        last_build = builds[0]

    # First
    first_build = None
    builds_reversed = builds.order_by('created')
    if len(builds_reversed):
        first_build = builds_reversed[0]

    # Recent builds
    recent = builds[:10]

    # Statistics
    stat = {'running': len(builds.filter(status__gte=0, status__lt=999)),
            'failed': len(builds.filter(status__lt=0)),
            'finished': len(builds.filter(status=999))}
    stat['done'] = stat['failed'] + stat['finished']
    stat['total'] = stat['done'] + stat['running']
    if stat['done'] > 0:
        stat['ratio'] = stat['finished'] / float(stat['done']) * 100


    context = {'packager': user,
               'first': first_build,
               'last': last_build,
               'builds': recent,
               'stat': stat}
    return render_to_response('build/user_show.html', context,
                              context_instance=RequestContext(request))

