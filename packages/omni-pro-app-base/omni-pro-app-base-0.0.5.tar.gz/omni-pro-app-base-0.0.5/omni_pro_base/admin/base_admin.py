from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class MixinSaveAdmin(object):
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class BaseAdmin(MixinSaveAdmin, admin.ModelAdmin):
    exclude = ("created_at", "updated_at")
    fieldsets = (
        (_("Audit Info"), {"fields": ("is_active","created_by", "updated_by", )}),
    )
