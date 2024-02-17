from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.translation import gettext_lazy as _
from omni_pro_base.admin import MixinSaveAdmin
from omni_pro_base.models import User


@admin.register(User)
class UserAdmin(MixinSaveAdmin, AuthUserAdmin):
    list_display = (
        "email",
        "username",
        "name",
        "date_joined",
        "last_login",
        "is_staff",
        "is_active",
        "created_by",
        "updated_by",
    )
    list_filter = (
        "last_login",
        "date_joined",
        "is_active",
        "is_staff",
    )
    fieldsets = (
        (_("Primary info"), {"fields": ("email", "username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "is_staff", "is_active", "groups"),
            },
        ),
    )
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)
