from django.core.management.base import BaseCommand, CommandError

from irgsh_web.build import utils

class Command(BaseCommand):
    help = 'Send ping message to all workers'

    def handle(self, *args, **options):
        utils.ping_workers()

