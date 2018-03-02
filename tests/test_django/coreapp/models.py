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
    kind = models.CharField(
        max_length=1,
        choices=(
            ('A', 'Display for A'),
            ('B', 'Display for B'),
            ('C', 'Display for C'),
        ),
        default='A'
    )
