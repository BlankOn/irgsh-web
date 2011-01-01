import uuid
import gzip
import shutil
import tempfile
import urllib
import os
import tarfile
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

def build_task_id():
    return str(uuid.uuid4())

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
            key = key.strip()
            value = value.strip()
            if key in ['tag', 'rev']:
                return {key: value}

        except ValueError:
            pass

        raise ValueError(_('Invalid source options for Bazaar'))

class SpecInit(object):
    '''
    Prepare and distribute specification
    '''

    def __init__(self, spec_id):
        from .models import Specification

        self.spec_id = spec_id
        self.spec = Specification.objects.get(pk=spec_id)

        self.description_sent = False
        self.distributed = False

        self.source_name = None
        self.orig_name = None

    def start(self):
        init_status = self.spec.status

        try:
            self.init()
            self.source_name = self.download_source()
            self.inspect_source()
            self.orig_name = self.download_orig()
            self.distribute()
        except (ValueError, AssertionError), e:
            if init_status != self.spec.status:
                # Status has not been changed, set to failed
                self.spec.status = -1
                self.spec.save()

    def init(self):
        self.target = os.path.join(settings.DOWNLOAD_TARGET, str(self.spec_id))
        if not os.path.exists(self.target):
            os.makedirs(self.target)

    def download_source(self):
        '''
        Download source file according to the type
        '''
        from .models import SOURCE_TYPE
        types = zip(*SOURCE_TYPE)[0]

        assert self.spec.source_type in types

        func_name = '_download_source_%s' % self.spec.source_type
        assert hasattr(self, func_name)

        func = getattr(self, func_name)
        return func()

    def update_resource(self, **param):
        '''
        Update resource database associated to the specification
        '''
        from .models import SpecificationResource

        SpecificationResource.objects.get_or_create(specification=self.spec)
        SpecificationResource.objects.filter(specification=self.spec) \
                                     .update(**param)

    def _download_source_bzr(self):
        '''
        Download source from a Bazaar repository
        '''
        self.update_resource(source_started=datetime.now())

        try:
            tmpdir = tempfile.mkdtemp()

            # Get options
            source = self.spec.source
            opts = self.spec.source_opts
            if opts is None:
                opts = {}

            # Open branch
            branch = Branch.open(self.spec.source)

            # Get revision
            revid = None
            if 'revision' in opts:
                revid = branch.get_rev_id(opts['revision'])
            elif 'tag' in opts:
                revid = branch.tags.lookup_tag(opts['tag'])
            else:
                revid = branch.last_revision()

            # Get tree
            tree = branch.repository.revision_tree(revid)

            # Find debian/control and debian/changelog
            #   These two files are checked before extracting the whole files
            #   because they will determine whether this specification is
            #   allowed to proceed or not
            tree.lock_read()
            if not tree.has_filename('debian/control') or \
               not tree.has_filename('debian/changelog'):
                raise ValueError('Invalid source')

            file_id_control = None
            file_id_changelog = None
            for item in tree.list_files(from_dir='debian', recursive=False):
                if item[2] == 'file':
                    if item[0] == 'control':
                        file_id_control = item[3]
                    elif item[0] == 'changelog':
                        file_id_changelog = item[3]

            fcontrol = os.path.join(tmpdir, 'control')
            fchangelog = os.path.join(tmpdir, 'changelog')

            f = open(fcontrol, 'wb')
            f.write(tree.get_file(file_id_control).read())
            f.close()

            f = open(fchangelog, 'wb')
            f.write(tree.get_file(file_id_changelog).read())
            f.close()

            tree.unlock()

            # Get source package name
            changelog = Changelog(fchangelog)
            name = changelog.package
            version = str(changelog.version).split(':')[-1]

            # Send changelog and control
            #   send_description will raise an exception if this specification
            #   is rejected
            self.send_description(fchangelog, fcontrol)

            # Package is accepted, distribution can begin
            self.distribute()

            # Export
            #   everything looks good, continue to proceed
            source_name = '%s_%s.tar.gz' % (name, version)
            self.update_resource(source_name=source_name)

            target = os.path.join(self.target, source_name)
            export(tree, target)

            self.update_resource(source_finished=datetime.now())

            return source_name

        finally:
            shutil.rmtree(tmpdir)

    def _download_source_tarball(self):
        '''
        Download source file in an archive
        '''
        self.update_resource(source_started=datetime.now())

        try:
            source_name = os.path.basename(self.spec.source)
            self.update_resource(source_name=source_name)

            fname, http = urllib.urlretrieve(self.spec.source)
            target = os.path.join(self.target, source_name)
            shutil.move(fname, target)

            self.update_resource(source_finished=datetime.now())

            return source_name

        finally:
            if os.path.exists(fname):
                os.unlink(fname)

    def send_description(self, changelog, control):
        '''
        Send package description to the manager

        Depending on the response, this will determine whether
        this specification is allowed to proceed or not.
        '''
        from . import manager

        if self.description_sent:
            return

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
                # Package is rejected
                raise ValueError(_('Package rejected: %(msg)s') % \
                                 {'msg': res['msg']})

        finally:
            self.description_sent = True
            shutil.rmtree(tmpdir)

    def inspect_source(self):
        '''
        Extract source and send description
        '''
        # FIXME is it safe to assume that all tarball source files
        #       are in tar/gz format?
        source_name = os.path.join(self.target, self.source_name)
        tar = tarfile.open(source_name, 'r:gz')
        fchangelog = tar.extractfile('debian/changelog')
        fcontrol = tar.extractfile('debian/control')

        self.send_description(fchangelog, fcontrol)

    def download_orig(self):
        '''
        Download orig file
        '''
        if self.spec.orig is None:
            return None

        self.update_resource(orig_started=datetime.now())

        try:
            orig_name = os.path.basename(self.spec.orig)
            self.update_resource(orig_name=orig_name)

            fname, http = urllib.urlretrieve(self.spec.orig)
            target = os.path.join(self.target, orig_name)
            shutil.move(fname, target)

            self.update_resource(orig_finished=datetime.now())

            return orig_name

        finally:
            if os.path.exists(fname):
                os.unlink(fname)

    def declare_queues(self, archs):
        '''
        Declare queues, exchanges, and routing keys to the builders
        '''
        for arch in archs:
            # declare exchange, queue, and binding
            routing_key = 'builder.%s' % arch.name
            consumer = self.get_consumer()
            consumer.queue = 'builder_%s' % arch.name
            consumer.exchange = 'builder'
            consumer.exchange_type = 'topic'
            consumer.routing_key = routing_key
            consumer.declare()
            consumer.connection.close()

    def get_archs(self, spec):
        '''
        List all architectures associated to this specification
        '''
        return spec.distribution.repo.architectures.all()

    def distribute(self):
        '''
        Distribute specification to builders
        '''
        from celery.task.sets import subtask

        from .models import BuildTask
        from irgsh_node.tasks import BuildPackage
        from irgsh.specification import Specification as BuildSpecification
        from irgsh.distribution import Distribution as BuildDistribution

        if self.distributed:
            return

        # Declare queues
        archs = self.get_archs(spec)
        self.declare_queues(archs)

        # Prepare arguments
        task_name = BuildPackage.name
        args = utils.create_build_task_param(spec)

        build_spec = BuildSpecification(spec.source, spec.orig,
                                        spec.source_type, spec.source_opts)

        dist = spec.distribution
        build_dist = BuildDistribution(dist.name, dist.mirror, dist.dist,
                                       dist.components, dist.extra)

        args = [spec.id, build_spec, build_dist]
        kwargs = None

        spec_id, d, s = args
        print 'init: spec_id=%s' % spec_id
        print '- distribution: name=%s mirror=%s dist=%s comp=%s extra=%s' % (d.name, d.mirror, d.dist, repr(d.components), repr(d.extra))
        print '- spec: location=%s type=%s orig=%s opts=%s' % (s.location, repr(s.source_type), repr(s.orig), repr(s.source_opts))

        # Distribute to builder of each architecture
        subtasks = []
        for arch in archs:
            task_id = utils.build_task_id()

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

        spec.status = 3
        spec.save()

        for s in subtasks:
            print '  - subtask: %s' % s
            s.apply_async()

        self.distributed = True

