from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin

from ram.admin import publish, unpublish
from metadata.models import (
    Property,
    Decoder,
    DecoderDocument,
    Scale,
    Manufacturer,
    Company,
    Tag,
    RollingStockType,
    GenericDocument,
)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "private")
    search_fields = ("name",)


class DecoderDocInline(admin.TabularInline):
    model = DecoderDocument
    min_num = 0
    extra = 0
    classes = ["collapse"]


@admin.register(Decoder)
class DecoderAdmin(admin.ModelAdmin):
    inlines = (DecoderDocInline,)
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


@admin.register(GenericDocument)
class GenericDocumentAdmin(admin.ModelAdmin):
    readonly_fields = ("size",)
    list_display = (
        "__str__",
        "description",
        "private",
        "size",
        "download",
    )
    search_fields = (
        "description",
        "file",
    )
    actions = [publish, unpublish]
