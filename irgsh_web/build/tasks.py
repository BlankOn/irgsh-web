from celery.decorators import task as celery_task
from celery.task.sets import subtask

from . import utils
from .models import Architecture, Specification, BuildTask

@celery_task
def init_specification(spec_id):
    '''
    Initialize specification.

    Get all active architecture and create build task for each of them.
    '''
    spec = Specification.objects.get(pk=spec_id)

    task_name = 'irgsh_node.tasks.BuildPackage'
    args = utils.create_build_task_param(spec)
    kwargs = None

    archs = Architecture.objects.filter(active=True)
    for arch in archs:
        task_id = utils.build_task_id()

        # store task info
        task = BuildTask()
        task.task_id = task_id
        task.specification = spec
        task.arch = arch
        task.save()

        # create build package task
        opts = {'routing_key': 'builder.%s' % arch.name,
                'task_id': task_id}

        # execute build task asynchronously
        s = subtask(task_name, args, kwargs, opts)
        s.apply_async()

    spec.save()

