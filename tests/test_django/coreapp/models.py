from uuid import uuid4
from django.db import models


class MyModel(models.Model):
    name = models.CharField(max_length=128, blank=True)
    uuid = models.UUIDField(default=uuid4, unique=True)
    version = models.IntegerField(default=1)
