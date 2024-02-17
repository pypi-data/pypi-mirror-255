from django.core.files.storage import default_storage
from django.core.management import BaseCommand
from django.core.management import CommandError

from ...models import Timestamp


class Command(BaseCommand):
    help = 'Create a Timestamp for an existing file.'

    def add_arguments(self, parser):
        parser.add_argument('name')
        parser.add_argument('--force', action='store_true')

    def handle(self, *args, **options):
        if Timestamp.objects.filter(name=options['name']).exists():
            if options['force']:
                if options['verbosity'] >= 1:
                    self.stderr.write('Force-overwriting existing timestamp')
            else:
                raise CommandError('Timestamp exists. Use --force to overwrite anyway.')

        Timestamp.objects.update_or_create(name=options['name'], defaults={
            'timestamp': default_storage.timestamp(options['name'])
        })

        if options['verbosity'] >= 1:
            self.stderr.write('Timestamp created')
