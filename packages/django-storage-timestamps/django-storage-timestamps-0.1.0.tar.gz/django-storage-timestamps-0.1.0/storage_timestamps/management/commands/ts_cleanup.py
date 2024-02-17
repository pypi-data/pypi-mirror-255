from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from ...models import Timestamp


class Command(BaseCommand):
    help = 'Delete timestamps for files that no longer exist.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', '-n', action='store_true')

    def handle(self, *args, **options):
        count = 0
        total = 0
        for ts in Timestamp.objects.all():
            total += 1
            if not default_storage.exists(ts.name):
                count += 1
                if not options['dry_run']:
                    ts.delete()
                if options['verbosity'] >= 1:
                    self.stderr.write(f'Delete timestamp for {ts}')

        if options['verbosity'] >= 1:
            self.stderr.write(f'\nCleared {count} of {total} timestamps''')
