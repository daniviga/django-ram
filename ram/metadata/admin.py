from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin

from metadata.models import (
    Property,
    Decoder,
    Scale,
    Manufacturer,
    Company,
    Tag,
    RollingStockType,
)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "private")
    search_fields = ("name",)


@admin.register(Decoder)
class DecoderAdmin(admin.ModelAdmin):
    readonly_fields = ("image_thumbnail",)
    list_display = ("__str__", "sound")
    list_filter = ("manufacturer", "sound")
    search_fields = ("name", "manufacturer__name")


@admin.register(Scale)
class ScaleAdmin(admin.ModelAdmin):
    list_display = ("scale", "ratio", "gauge", "tracks")
    list_filter = ("ratio", "gauge", "tracks")
    search_fields = list_display


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    readonly_fields = ("logo_thumbnail",)
    list_display = ("name", "country")
    list_filter = list_display
    search_fields = ("name",)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    readonly_fields = ("logo_thumbnail",)
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    readonly_fields = ("slug",)
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(RollingStockType)
class RollingStockTypeAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("__str__",)
    list_filter = ("type", "category")
    search_fields = ("type", "category")
