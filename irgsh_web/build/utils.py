import uuid
import gzip
import shutil
import tempfile
import urllib
import os
import tarfile
import logging
import random
import time
from datetime import datetime

from django.db import IntegrityError
from django.utils.translation import ugettext as _
from django.conf import settings

try:
    from debian.deb822 import Packages
    from debian.changelog import Changelog
except ImportError:
    from debian_bundle.deb822 import Packages
    from debian_bundle.changelog import Changelog

from bzrlib.branch import Branch
from bzrlib.export import export

def create_build_task_param(spec):
    from irgsh.specification import Specification as BuildSpecification
    from irgsh.distribution import Distribution as BuildDistribution

    spec_id = spec.id
    build_spec = BuildSpecification(spec.source, spec.orig,
                                    spec.source_type, spec.source_opts)

    dist = spec.distribution
    build_dist = BuildDistribution(dist.name, dist.mirror, dist.dist,
                                   dist.components, dist.extra)

    return spec_id, build_spec, build_dist

def baseN(num, base):
    res = []
    while True:
        res.append('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'[num%base])
        num = num // base
        if num == 0:
            break
    return ''.join(reversed(res))

def create_task_id():
    '''
    Generate task id

    The task id is a ten digits alphanumeric characters that is
    made of a random number concatenated with a timestamp.

        >>> digits = 10
        >>> min_random = (62 ** (digits-1)) >> 32
        3151848
        >>> max_random = (((62 ** digits) - 1) >> 32) - 1
        195414610
    '''
    num = random.randint(3151848, 195414610)
    num = (num << 32) + (int(time.time()) & 0xFFFFFFFF)
    return baseN(num, 62)

def get_package_info(packages):
    from .models import Package, SOURCE, BINARY

    items = []
    name = None
    for info in packages:
        pkg = {}
        if info.has_key('Source'):
            pkg['name'] = info['Source']
            pkg['type'] = SOURCE
            name = info['Source']
        else:
            pkg['name'] = info['Package']
            pkg['type'] = BINARY
            pkg['architecture'] = info['Architecture']

        items.append(pkg)

    result = {'name': name,
              'packages': items}

    return result

def store_package_info(spec, info):
    from .models import Package, BINARY

    for data in info['packages']:
        pkg = Package()
        pkg.specification = spec
        pkg.name = data['name']
        pkg.type = data['type']
        if pkg.type == BINARY:
            pkg.architecture = data['architecture']
        try:
            pkg.save()
        except IntegrityError:
            pass

def build_source_opts(source_type, source_opts):
    from .models import TARBALL, BZR

    if source_opts is None:
        source_opts = ''
    source_opts = source_opts.strip()

    if source_type == TARBALL:
        return None

    elif source_type == BZR:
        '''
        valid opts:
        - tag=a-tag
        - rev=a-rev
        '''
        if source_opts == '':
            return None

        try:
            key, value = source_opts.split('=', 1)
            key = str(key.strip())
            value = str(value.strip())
            if key in ['tag', 'rev']:
                return {key: value}

        except ValueError:
            pass

        raise ValueError(_('Invalid source options for Bazaar'))

class SpecInit(object):
    '''
    Prepare and distribute specification
    '''

    def __init__(self, spec):
        self.spec_id = spec.id
        self.spec = spec

        self.description_sent = False
        self.distributed = False

        self.source_name = None
        self.orig_name = None

        self.log = logging.getLogger('irgsh_web.specinit')

    def start(self):
        from .models import Specification

        self.log.debug('[%s] Initializing specification' % self.spec_id)

        try:
            self.init()
            files = self.download()
            self.distribute()
            self.upload(files)
        except (ValueError, AssertionError, TypeError, IOError), e:
            self.log.error('[%s] Error! %s' % (self.spec_id, e))
            current_status = Specification.objects.get(pk=self.spec_id).status
            print 'current status: %s' % current_status
            if current_status >= 0:
                self.set_status(-1)

    def init(self):
        # Prepare source directory
        self.target = os.path.join(settings.DOWNLOAD_TARGET, str(self.spec_id))
        if not os.path.exists(self.target):
            os.makedirs(self.target)

        self.log.debug('[%s] Resource directory: %s' % (self.spec_id, self.target))

    def download(self):
        # Prepare source package builder
        from irgsh.packager import Packager
        from irgsh.utils import find_changelog
        from irgsh.specification import Specification as BuildSpecification

        spec = self.spec
        build_spec = BuildSpecification(spec.source, spec.orig,
                                        spec.source_type, spec.source_opts)
        packager = Packager(build_spec, None, None)

        orig_path = None

        try:
            # Download source and build source package
            build_dir = tempfile.mkdtemp()
            source_dir = tempfile.mkdtemp()

            self.set_status(101)
            packager.export_source(source_dir)

            self.set_status(102)
            orig_path = packager.retrieve_orig()

            self.set_status(103)
            self.dsc = packager.generate_dsc(build_dir, source_dir, orig_path)

            # Copy source packages
            dsc_file = os.path.join(build_dir, self.dsc)
            started = False
            files = [self.dsc]
            for line in open(dsc_file):
                if line.startswith('Files:'):
                    started = True
                elif started:
                    if not line.startswith(' '):
                        break
                    p = line.strip().split()
                    files.append(p[2])
            for fname in files:
                shutil.copyfile(os.path.join(build_dir, fname),
                                os.path.join(self.target, fname))

            # Send description
            dirname = find_changelog(source_dir)
            changelog = os.path.join(dirname, 'debian', 'changelog')
            control = os.path.join(dirname, 'debian', 'control')
            self.send_description(changelog, control)

            return files

        finally:
            shutil.rmtree(build_dir)
            shutil.rmtree(source_dir)
            if orig_path is not None:
                os.unlink(orig_path)

    def send_description(self, changelog, control):
        '''
        Send package description to the manager

        Depending on the response, this will determine whether
        this specification is allowed to proceed or not.
        '''
        from . import manager

        if self.description_sent:
            return

        self.log.debug('[%s] Sending description' % (self.spec_id,))

        try:
            tmpdir = tempfile.mkdtemp()
            gzchangelog = os.path.join(tmpdir, 'changelog.gz')
            gzcontrol = os.path.join(tmpdir, 'control.gz')

            gz = gzip.GzipFile(gzchangelog, 'wb')
            if hasattr(changelog, 'read'):
                gz.write(changelog.read())
            else:
                gz.write(open(changelog, 'rb').read())
            gz.close()

            gz = gzip.GzipFile(gzcontrol, 'wb')
            if hasattr(control, 'read'):
                gz.write(control.read())
            else:
                gz.write(open(control, 'rb').read())
            gz.close()

            res = manager.send_spec_description(self.spec.id,
                                                gzchangelog, gzcontrol)
            if res['status'] != 'ok':
                self.log.debug('[%s] Package is rejected: %s' % (self.spec_id, res))

                # Package is rejected
                raise ValueError(_('Package rejected: %(msg)s') % \
                                 {'msg': res['msg']})

            self.log.debug('[%s] Package is accepted: %s' % \
                           (self.spec_id, res['package']))

        finally:
            self.description_sent = True
            shutil.rmtree(tmpdir)

    def get_archs(self, spec):
        '''
        List all architectures associated to this specification
        '''
        return spec.distribution.repo.architectures.all()

    def distribute(self):
        '''
        Distribute specification to builders
        '''
        self.log.debug('[%s] Distributing tasks' % self.spec_id)

        from celery.task.sets import subtask

        from .models import BuildTask
        from irgsh_node.tasks import BuildPackage
        from irgsh.specification import Specification as BuildSpecification
        from irgsh.distribution import Distribution as BuildDistribution

        if self.distributed:
            return

        spec = self.spec
        spec_id = self.spec_id

        # Prepare arguments
        task_name = BuildPackage.name
        args = create_build_task_param(spec)

        build_spec = BuildSpecification(spec.source, spec.orig,
                                        spec.source_type, spec.source_opts)

        dist = spec.distribution
        build_dist = BuildDistribution(dist.name(), dist.mirror, dist.dist,
                                       dist.components, dist.extra)

        args = [self.spec_id, build_spec, build_dist]
        kwargs = None

        spec_id, s, d = args

        # Distribute to builder of each architecture
        subtasks = []
        archs = self.get_archs(spec)
        for arch in archs:
            task_id = create_task_id()

            # store task info
            task = BuildTask()
            task.task_id = task_id
            task.specification = spec
            task.architecture = arch
            task.save()

            # declare exchange, queue, and binding
            routing_key = 'builder.%s' % arch.name

            # create build package task
            opts = {'exchange': 'builder',
                    'exchange_type': 'topic',
                    'routing_key': routing_key,
                    'task_id': task_id}

            # execute build task asynchronously
            s = subtask(task_name, args, kwargs, opts)
            subtasks.append(s)

        self.set_status(104)

        for s in subtasks:
            s.apply_async()

        self.distributed = True

    def set_status(self, status):
        from .models import Specification
        Specification.objects.filter(pk=self.spec.id).update(status=status)

    def build_source(self):
        from irgsh.packages.source import SourcePackage

        pkg = SourcePackage(source_dir, orig_path)
        return pkg.generate_dsc(target)

    def upload(self, files):
        self.log.debug('[%s] Scheduling source package upload' % self.spec_id)

        from .tasks import UploadSource
        UploadSource.apply_async(args=(self.spec_id, files))

def rebuild_repo(spec):
    from celery.task.sets import subtask

    from .models import BuildTask
    from irgsh_repo.tasks import RebuildRepo

    tasks = BuildTask.objects.filter(specification=spec) \
                             .select_related()
    task_arch_list = [(task.task_id, task.architecture.name)
                      for task in tasks]

    task_name = RebuildRepo.name
    args = [spec.id, spec.package.name, spec.version,
            spec.package.distribution.name,
            spec.package.component.name,
            task_arch_list]
    kwargs = None
    opts = {'exchange': 'repo',
            'exchange_type': 'direct',
            'routing_key': 'repo'}

    s = subtask(task_name, args, kwargs, opts)
    return s.apply_async()

