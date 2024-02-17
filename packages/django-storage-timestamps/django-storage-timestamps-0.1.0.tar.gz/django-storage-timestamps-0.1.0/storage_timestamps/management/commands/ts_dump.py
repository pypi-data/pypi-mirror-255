from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Timestamp


class Command(BaseCommand):
    help = 'Dump the timestamp for a file into a file for verification.'

    def add_arguments(self, parser):
        parser.add_argument('name')
        parser.add_argument('out', nargs='?')

    def handle(self, *args, **options):
        path = Path(settings.MEDIA_ROOT) / options['name']
        out = options['out'] or path.name + '.ts'

        ts = Timestamp.objects.get(name=options['name'])
        with open(out, 'wb') as fh:
            fh.write(ts.timestamp)

        if options['verbosity'] >= 1:
            self.stderr.write(
                f'TimeStampToken was written to "{out}".\n\n'
                'inspect:\n  '
                f'openssl ts -reply -in "{out}" -token_in -text\n'
                'verify:\n  '
                f'openssl ts -verify -in "{out}" -token_in -data "{path}" '
                '-CAfile "/etc/ssl/certs/ca-certificates.crt"\n'
            )
