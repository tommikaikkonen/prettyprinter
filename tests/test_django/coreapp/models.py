from django.db import models


class MyModel(models.Model):
    name = models.CharField(max_length=128, blank=True)
    slug = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        unique=True
    )
    version = models.IntegerField(default=1)
