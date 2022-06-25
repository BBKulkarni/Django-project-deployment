from django.db import models
from django.contrib import auth

# Create your models here.
class User(auth.models.User, auth.models.PermissionsMixin):
    """docstring for ."""

    def __str__(self):
        return "@{}".format(self.username)
