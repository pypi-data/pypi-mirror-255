import datetime
import io
from unittest.mock import patch

import rfc3161ng
from django.core.files.base import File
from django.core.files.storage import InMemoryStorage
from django.core.management import CommandError
from django.core.management import call_command
from django.test import TestCase

from storage_timestamps.models import Timestamp
from storage_timestamps.storage import TimestampedMixin


class TimestampedStorage(TimestampedMixin, InMemoryStorage):
    pass


class StorageTest(TestCase):
    def setUp(self):
        self.storage = TimestampedStorage()
        self.content = io.BytesIO(b'test')
        self.storage.save('foo/my_file.pdf', self.content)
        self.ts = Timestamp.objects.first()

    def test_create_timestamp(self):
        self.assertEqual(self.ts.name, 'foo/my_file.pdf')

    def test_current_time(self):
        dt = rfc3161ng.get_timestamp(self.ts.timestamp)
        self.assertEqual(datetime.date.today(), dt.date())

    def test_validation(self):
        pass  # TODO

    def test_rename(self):
        real_name = self.storage.save('foo/my_file.pdf', self.content)
        self.assertNotEqual(real_name, 'foo/my_file.pdf')
        self.assertTrue(Timestamp.objects.filter(name=real_name).exists())

    def test_deletion(self):
        self.storage.delete('foo/my_file.pdf')
        self.assertEqual(Timestamp.objects.count(), 0)


class TSDumpTest(TestCase):
    def test_ts_dump(self):
        Timestamp.objects.create(name='foo/my_file.pdf', timestamp=b'abc')
        stderr = io.StringIO()
        with patch('builtins.open') as mock_open:
            call_command('ts_dump', 'foo/my_file.pdf', stderr=stderr)
        mock_open.assert_called_once_with('my_file.pdf.ts', 'wb')
        mock_fh = mock_open.return_value.__enter__.return_value
        mock_fh.write.assert_called_once_with(b'abc')
        self.assertIn('"my_file.pdf.ts"', stderr.getvalue())


class TSCleanupTest(TestCase):
    def test_ts_cleanup(self):
        Timestamp.objects.create(name='foo/my_file.pdf', timestamp=b'abc')
        stderr = io.StringIO()
        call_command('ts_cleanup', stderr=stderr)
        self.assertIn('Cleared 1 of 1 timestamps', stderr.getvalue())
        self.assertEqual(Timestamp.objects.count(), 0)

    def test_dry_run(self):
        Timestamp.objects.create(name='foo/my_file.pdf', timestamp=b'abc')
        stderr = io.StringIO()
        call_command('ts_cleanup', '-n', stderr=stderr)
        self.assertIn('Cleared 1 of 1 timestamps', stderr.getvalue())
        self.assertEqual(Timestamp.objects.count(), 1)


class TSCreateTest(TestCase):
    def setUp(self):
        self.stderr = io.StringIO()

    def call_command(self, *args):
        s = 'storage_timestamps.management.commands.ts_create.default_storage'
        file = File(io.BytesIO(b'test'))
        with patch(s, TimestampedStorage()) as storage:
            with patch.object(storage, 'open', return_value=file):
                call_command('ts_create', *args, stderr=self.stderr)

    def test_ts_create(self):
        self.call_command('foo/my_file.pdf')
        self.assertIn('Timestamp created', self.stderr.getvalue())
        self.assertEqual(Timestamp.objects.count(), 1)

    def test_exists(self):
        Timestamp.objects.create(name='foo/my_file.pdf', timestamp=b'abc')
        with self.assertRaises(CommandError):
            self.call_command('foo/my_file.pdf')
        ts = Timestamp.objects.get()
        self.assertEqual(ts.timestamp, b'abc')

    def test_force(self):
        Timestamp.objects.create(name='foo/my_file.pdf', timestamp=b'abc')
        self.call_command('foo/my_file.pdf', '--force')
        self.assertIn('Force-overwriting existing timestamp', self.stderr.getvalue())
        self.assertIn('Timestamp created', self.stderr.getvalue())
        ts = Timestamp.objects.get()
        self.assertNotEqual(ts.timestamp, b'abc')
