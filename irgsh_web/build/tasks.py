import tempfile
import shutil
import os

from celery.task import Task

from . import utils
from .models import Specification

class InitSpecification(Task):
    '''Initialize specification.

    Get all active architecture and create build task for each of them.
    '''

    exchange = 'specinit'
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

