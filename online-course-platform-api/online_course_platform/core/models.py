from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext as _

class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        STUDENT = settings.USER_ROLE_STUDENT, 'Student'
        TEACHER = settings.USER_ROLE_TEACHER, 'Teacher'
        ADMIN = settings.USER_ROLE_ADMIN, 'Admin'

    first_name = models.CharField(_("first name"), max_length=255, null=False, blank=False)
    last_name = models.CharField(_("last name"), max_length=255, null=False, blank=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=2, choices=RoleChoices.choices, default='ST')
