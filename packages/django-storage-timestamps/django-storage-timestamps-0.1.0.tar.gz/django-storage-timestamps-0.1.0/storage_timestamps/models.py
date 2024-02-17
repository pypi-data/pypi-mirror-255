from django.db import models


class Timestamp(models.Model):
    name = models.CharField(max_length=512, unique=True)
    timestamp = models.BinaryField()

    def __str__(self):
        return self.name
