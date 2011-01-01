import tempfile
import shutil
import os

from celery.task import Task

from . import utils

class InitSpecification(Task):
    '''Initialize specification.

    Get all active architecture and create build task for each of them.
    '''

    exchange = 'specinit'
    ignore_result = True

    def run(self, spec_id):
        init = utils.SpecInit(spec_id)
        init.start()

