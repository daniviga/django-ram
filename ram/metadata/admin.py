from django.contrib import admin
from django.utils.html import format_html
from adminsortable2.admin import SortableAdminMixin

from repository.models import DecoderDocument
from metadata.models import (
    Property,
    Decoder,
    Scale,
    Shop,
    Manufacturer,
    Company,
    Tag,
    RollingStockType,
)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "private")
    search_fields = ("name",)


class DecoderDocInline(admin.TabularInline):
    model = DecoderDocument
    min_num = 0
    extra = 1
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
    list_display = ("name", "country_flag_name")
    list_filter = ("name", "country")
    search_fields = ("name",)

    @admin.display(description="Country")
    def country_flag_name(self, obj):
        return format_html(
            '<img src="{}" /> {}', obj.country.flag, obj.country.name
        )


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    readonly_fields = ("logo_thumbnail",)
    list_display = ("name", "category", "country_flag_name")
    list_filter = ("category",)
    search_fields = ("name",)

    @admin.display(description="Country")
    def country_flag_name(self, obj):
        return format_html(
            '<img src="{}" /> {}', obj.country.flag, obj.country.name
        )


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


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("name", "on_line", "active", "country_flag_name")
    list_filter = ("on_line", "active")
    search_fields = ("name",)

    @admin.display(description="Country")
    def country_flag_name(self, obj):
        return format_html(
            '<img src="{}" /> {}', obj.country.flag, obj.country.name
        )
