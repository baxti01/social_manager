from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from user.managers import MyUserManager


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=40, blank=False, unique=True, verbose_name="username")
    email = models.EmailField(max_length=100, unique=True, verbose_name="email")

    first_name = models.CharField(max_length=100, blank=True, verbose_name="first name")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="last name")

    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="date joined")
    is_active = models.BooleanField(default=True, verbose_name="is active")
    is_staff = models.BooleanField(default=False, verbose_name="is staff")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyUserManager()

    def __str__(self):
        return self.email

