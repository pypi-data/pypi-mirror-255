import hashlib

import rfc3161ng
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .models import Timestamp

timestamper = rfc3161ng.RemoteTimestamper(
    settings.TIMESTAMP_AUTHORITY,
    include_tsa_certificate=True,
    hashname='sha512',
)


def file_digest(fh, hashname, bufsize=2**18):
    # backported from python 3.11
    hashobj = hashlib.new(hashname)

    buf = bytearray(bufsize)
    view = memoryview(buf)
    while True:
        size = fh.readinto(buf)
        if size == 0:
            break
        hashobj.update(view[:size])

    return hashobj.digest()


class TimestampedMixin:
    def timestamp(self, name):
        with self.open(name, 'rb') as fh:
            digest = file_digest(fh, 'sha512')
        return timestamper.timestamp(digest=digest)

    def save(self, name, content, max_length=None):
        real_name = super().save(name, content, max_length)
        ts = self.timestamp(real_name)
        Timestamp.objects.create(name=real_name, timestamp=ts)
        return real_name

    def delete(self, name):
        Timestamp.objects.filter(name=name).delete()
        return super().delete(name)


class TimestampedFileSystemStorage(TimestampedMixin, FileSystemStorage):
    pass
