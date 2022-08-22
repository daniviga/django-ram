from django.db import models
from django.contrib import admin
from solo.admin import SingletonModelAdmin
from martor.widgets import AdminMartorWidget

from portal.models import SiteConfiguration, Flatpage

admin.site.register(SiteConfiguration, SingletonModelAdmin)


@admin.register(Flatpage)
class FlatpageAdmin(admin.ModelAdmin):
    readonly_fields = ("path", "creation_time", "updated_time")
    list_display = ("name", "path")
    search_fields = ("name",)

    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "path",
                    "content",
                    "draft",
                )
            },
        ),
        (
            "Audit",
            {
                "classes": ("collapse",),
                "fields": (
                    "creation_time",
                    "updated_time",
                ),
            },
        ),
    )
