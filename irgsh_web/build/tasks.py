import tempfile
import shutil
import os

from celery.task import Task

from . import utils

class InitSpecification(Task):
    '''Initialize specification.

    Get all active architecture and create build task for each of them.
    '''

    ignore_result = True

    def run(self, spec_id):
        spec = Specification.objects.get(pk=spec_id)

        task_name = BuildPackage.name # 'irgsh_node.tasks.BuildPackage'
        args = utils.create_build_task_param(spec)
        kwargs = None

        archs = Architecture.objects.filter(active=True)
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

            consumer = self.get_consumer()
            consumer.queue = 'builder_%s' % arch.name
            consumer.exchange = 'builder'
            consumer.exchange_type = 'topic'
            consumer.routing_key = routing_key
            consumer.declare()
            consumer.connection.close()

            # create build package task
            opts = {'exchange': 'builder',
                    'exchange_type': 'topic',
                    'routing_key': routing_key,
                    'task_id': task_id}

            # execute build task asynchronously
            s = subtask(task_name, args, kwargs, opts)
            s.apply_async()

        spec.save()

