import html

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html, format_html_join, strip_tags

from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from ram.admin import publish, unpublish
from ram.utils import generate_csv
from repository.models import RollingStockDocument
from portal.utils import get_site_conf
from roster.models import (
    RollingClass,
    RollingClassProperty,
    RollingStock,
    RollingStockImage,
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
    list_display = ("__str__", "type", "company", "country_flag")
    list_filter = ("company", "type__category", "type")
    search_fields = (
        "identifier",
        "company__name",
        "company__slug",
        "type__type",
    )
    save_as = True

    @admin.display(description="Country")
    def country_flag(self, obj):
        return format_html(
            '<img src="{}" /> {}', obj.country.flag, obj.country.name
        )


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


@admin.register(RollingStockJournal)
class RollingJournalAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "date",
        "private",
    )
    list_filter = (
        "date",
        "private",
    )
    autocomplete_fields = ("rolling_stock",)
    search_fields = (
        "rolling_stock__rolling_class__identifier",
        "rolling_stock__road_number",
        "rolling_stock__item_number",
        "log",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "private",
                    "rolling_stock",
                    "log",
                    "date",
                )
            },
        ),
    )


@admin.register(RollingStock)
class RollingStockAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (
        RollingStockPropertyInline,
        RollingStockImageInline,
        RollingStockDocInline,
        RollingStockJournalInline,
    )
    autocomplete_fields = ("rolling_class", "shop")
    readonly_fields = ("preview", "invoices", "creation_time", "updated_time")
    list_display = (
        "__str__",
        "address",
        "manufacturer",
        "scale",
        "item_number",
        "company",
        "country_flag",
        "published",
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
        "rolling_class__company__slug",
        "manufacturer__name",
        "scale__scale",
        "road_number",
        "address",
        "item_number",
    )
    save_as = True

    @admin.display(description="Country")
    def country_flag(self, obj):
        return format_html(
            '<img src="{}" /> {}', obj.country.flag, obj.country.name
        )

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
            "Purchase data",
            {
                "fields": (
                    "shop",
                    "purchase_date",
                    "price",
                    "invoices",
                )
            },
        ),
        (
            "Notes",
            {"classes": ("collapse",), "fields": ("notes",)},
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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["price"].label = "Price ({})".format(
            get_site_conf().currency
        )
        return form

    @admin.display(description="Invoices")
    def invoices(self, obj):
        if obj.invoice.exists():
            html = format_html_join(
                "<br>",
                "<a href=\"{}\" target=\"_blank\">{}</a>",
                ((i.file.url, i) for i in obj.invoice.all())
            )
        else:
            html = "-"
        return html

    def download_csv(modeladmin, request, queryset):
        header = [
            "ID",
            "Name",
            "Class",
            "Type",
            "Company",
            "Country",
            "Road Number",
            "Manufacturer",
            "Scale",
            "Item Number",
            "Set",
            "Era",
            "Description",
            "Production Year",
            "Notes",
            "Tags",
            "Decoder Interface",
            "Decoder",
            "Address",
            "Shop",
            "Purchase Date",
            "Price ({})".format(get_site_conf().currency),
            "Properties",
        ]
        data = []
        for obj in queryset:
            properties = settings.CSV_SEPARATOR_ALT.join(
                "{}:{}".format(property.property.name, property.value)
                for property in obj.property.all()
            )
            data.append(
                [
                    obj.uuid,
                    obj.__str__(),
                    obj.rolling_class.identifier,
                    obj.rolling_class.type,
                    obj.rolling_class.company.name,
                    obj.rolling_class.company.country,
                    obj.road_number,
                    obj.manufacturer.name,
                    obj.scale.scale,
                    obj.item_number,
                    obj.set,
                    obj.era,
                    html.unescape(strip_tags(obj.description)),
                    obj.production_year,
                    html.unescape(strip_tags(obj.notes)),
                    settings.CSV_SEPARATOR_ALT.join(
                        t.name for t in obj.tags.all()
                    ),
                    obj.get_decoder_interface_display(),
                    obj.decoder,
                    obj.address,
                    obj.shop,
                    obj.purchase_date,
                    obj.price,
                    properties,
                ]
            )

        return generate_csv(header, data, "rolling_stock.csv")

    download_csv.short_description = "Download selected items as CSV"
    actions = [publish, unpublish, download_csv]
