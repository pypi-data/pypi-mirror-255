from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ActivateManager(models.Manager):
    def get_queryset(self):
        return super(ActivateManager, self).get_queryset().filter(is_active=True)


class OmniModel(models.Model):
    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True,
        help_text=_("Date time on which the object was created"),
    )

    updated_at = models.DateTimeField(
        _("updated by"),
        auto_now=True,
        help_text=_("Date time on which the object was last modified"),
    )

    is_active = models.BooleanField(
        _("is active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(app_label)s_%(class)s_created_by",
        verbose_name=_("created by"),
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(app_label)s_%(class)s_updated_by",
        verbose_name=_("updated by"),
    )

    objects = models.Manager()
    active_objects = ActivateManager()

    class Meta:
        """Meta options."""

        abstract = True
        get_latest_by = "created_at"
        ordering = ["-created_at", "-updated_at"]

    def save(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        if self._state.adding and user:
            self.created_by = user
        if user:
            self.updated_by = user
        super().save(*args, **kwargs)
