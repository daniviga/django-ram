import csv
import html
import locale

from django.http import HttpResponse
from django.contrib import admin
from django.utils.html import strip_tags

from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from roster.models import (
    RollingClass,
    RollingClassProperty,
    RollingStock,
    RollingStockImage,
    RollingStockDocument,
    RollingStockProperty,
    RollingStockJournal,
)


class RollingClassPropertyInline(admin.TabularInline):
    model = RollingClassProperty
    min_num = 0
    extra = 0
    autocomplete_fields = ("property",)


@admin.register(RollingClass)
class RollingClass(admin.ModelAdmin):
    inlines = (RollingClassPropertyInline,)
    autocomplete_fields = ("manufacturer",)
    list_display = ("__str__", "type", "company")
    list_filter = ("company", "type__category", "type")
    search_fields = (
        "identifier",
        "company__name",
        "type__type",
    )
    save_as = True


class RollingStockDocInline(admin.TabularInline):
    model = RollingStockDocument
    min_num = 0
    extra = 0
    classes = ["collapse"]


class RollingStockImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = RollingStockImage
    min_num = 0
    extra = 0
    readonly_fields = ("image_thumbnail",)
    classes = ["collapse"]


class RollingStockPropertyInline(admin.TabularInline):
    model = RollingStockProperty
    min_num = 0
    extra = 0
    autocomplete_fields = ("property",)


class RollingStockJournalInline(admin.TabularInline):
    model = RollingStockJournal
    min_num = 0
    extra = 0
    classes = ["collapse"]


@admin.register(RollingStockDocument)
class RollingStockDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "rolling_stock",
        "description",
        "private",
        "download",
    )
    search_fields = (
        "rolling_stock__rolling_class__identifier",
        "rolling_stock__item_number",
        "description",
        "file",
    )


@admin.register(RollingStockJournal)
class RollingJournalDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "date",
        "rolling_stock",
        "private",
    )
    list_filter = (
        "date",
        "private",
    )
    search_fields = (
        "rolling_stock__rolling_class__identifier",
        "rolling_stock__road_number",
        "rolling_stock__item_number",
        "log",
    )


@admin.register(RollingStock)
class RollingStockAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (
        RollingStockPropertyInline,
        RollingStockImageInline,
        RollingStockDocInline,
        RollingStockJournalInline,
    )
    autocomplete_fields = ("rolling_class",)
    readonly_fields = ("preview", "creation_time", "updated_time")
    list_display = (
        "__str__",
        "published",
        "address",
        "manufacturer",
        "scale",
        "item_number",
        "company",
        "country",
    )
    list_filter = (
        "rolling_class__type__category",
        "rolling_class__type",
        "rolling_class__company__name",
        "scale",
        "manufacturer",
    )
    search_fields = (
        "rolling_class__identifier",
        "rolling_class__company__name",
        "manufacturer__name",
        "road_number",
        "address",
        "item_number",
    )
    save_as = True

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "preview",
                    "published",
                    "rolling_class",
                    "road_number",
                    "scale",
                    "manufacturer",
                    "item_number",
                    "set",
                    "era",
                    "description",
                    "production_year",
                    "purchase_date",
                    "notes",
                    "tags",
                )
            },
        ),
        (
            "DCC",
            {
                "fields": (
                    "decoder_interface",
                    "decoder",
                    "address",
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

    def download_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="rolling_stock.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(
            [
                "Identifier",
                "Company",
                "Manufacturer",
                "Scale",
                "Item Number",
                "Road Number",
                "Set",
                "Era",
                "Description",
                "Production Year",
                "Purchase Date",
                "Notes",
                "Tags",
                "Decoder Interface",
                "Decoder",
                "Address",
                "Properties",
                "Price",
            ]
        )
        for obj in queryset:
            properties = obj.property.exclude(
                property__name__icontains="price"
            )
            properties_str = ""
            for property in properties:
                properties_str = ",".join(
                    ("{}:{}".format(property.property.name, property.value),)
                )

            prices = obj.property.filter(property__name__icontains="price")

            price = 0.00
            for p in prices:
                price += locale.atof(p.value)

            writer.writerow(
                [
                    obj.rolling_class.identifier,
                    obj.rolling_class.company.name,
                    obj.manufacturer.name,
                    obj.scale,
                    obj.item_number,
                    obj.road_number,
                    obj.set,
                    obj.era,
                    html.unescape(strip_tags(obj.description)),
                    obj.production_year,
                    obj.purchase_date,
                    html.unescape(strip_tags(obj.notes)),
                    ",".join(t.name for t in obj.tags.all()),
                    obj.decoder_interface,
                    obj.decoder,
                    obj.address,
                    properties_str,
                    price if price > 0 else None,
                ]
            )
        return response

    download_csv.short_description = "Download selected items as CSV"
    actions = [download_csv]
