from django.core.management.base import BaseCommand, CommandError

from irgsh_web.builder import utils

class Command(BaseCommand):
    help = 'Send ping message to all workers'

    def handle(self, *args, **options):
        utils.ping_workers()

