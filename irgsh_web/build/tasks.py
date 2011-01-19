import tempfile
import shutil
import os
from subprocess import Popen, PIPE

from django.conf import settings

from celery.task import Task

from . import utils
from .models import Specification

class InitSpecification(Task):
    '''Initialize specification.

    Get all active architecture and create build task for each of them.
    '''

    ignore_result = True

    def run(self, spec_id):
        spec = Specification.objects.get(pk=spec_id)

        # Declare queues
        archs = spec.distribution.repo.architectures.all()
        self.declare_queues(archs)

        # Initialize spec
        init = utils.SpecInit(spec)
        init.start()

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

class UploadSource(Task):
    '''Upload source package to repository.
    '''

    ignore_result = True

    def run(self, spec_id, files):
        spec = Specification.objects.get(pk=spec_id)

        path = os.path.join(settings.DOWNLOAD_TARGET, str(spec_id))
        files = [os.path.join(path, fname) for fname in files]

        self.upload(files)

        self.set_status(spec_id, 105)
        spec.add_log('Source package uploaded')

    def upload(self, files):
        target = '%s@%s:%s' % (settings.SOURCE_UPLOAD_USER,
                               settings.SOURCE_UPLOAD_HOST,
                               settings.SOURCE_UPLOAD_PATH)
        cmd = 'scp -P %s %s %s' % (settings.SOURCE_UPLOAD_PORT,
                                   ' '.join(files),
                                   target)

        p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        p.communicate()

        assert p.returncode == 0

    def on_failure(self, exc, task_id, args, kwargs, einfo=None):
        spec_id = args[0]
        self.set_status(spec_id, -1)

    def set_status(self, spec_id, status):
        Specification.objects.filter(pk=spec_id).update(status=status)

