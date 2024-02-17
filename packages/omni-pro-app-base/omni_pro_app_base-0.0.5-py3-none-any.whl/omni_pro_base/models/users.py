from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from omni_pro_base.models.base_model import OmniModel


class User(AbstractUser, OmniModel):
    email = models.EmailField(_("email address"), unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    @property
    def name(self):
        return self.get_full_name()

    def __str__(self):
        return self.username
