from django.db import models
from django.contrib.auth.models import User


class VerifiedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verified = models.BooleanField()

    def __str__(self):
        return self.user.username
