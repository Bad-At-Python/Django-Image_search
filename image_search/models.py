from django.db import models
from django.utils.crypto import get_random_string


class Tag(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Image(models.Model):
    name = models.CharField(max_length=200, default=f"IMG_{get_random_string(length=12)}")
    s3_url = models.URLField(default="MISSINGURL")
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return str(self.name)
