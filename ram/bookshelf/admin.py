import html

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html, strip_tags
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from ram.admin import publish, unpublish
from ram.utils import generate_csv
from portal.utils import get_site_conf
from bookshelf.models import (
    BaseBookProperty,
    BaseBookImage,
    BaseBookDocument,
    Book,
    Author,
    Publisher,
    Catalog,
)


class BookImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = BaseBookImage
    min_num = 0
    extra = 0
    readonly_fields = ("image_thumbnail",)
    classes = ["collapse"]
    verbose_name = "Image"


class BookDocInline(admin.TabularInline):
    model = BaseBookDocument
    min_num = 0
    extra = 0
    classes = ["collapse"]


class BookPropertyInline(admin.TabularInline):
    model = BaseBookProperty
    min_num = 0
    extra = 0
    autocomplete_fields = ("property",)
    verbose_name = "Property"
    verbose_name_plural = "Properties"


@admin.register(Book)
class BookAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (
        BookPropertyInline,
        BookImageInline,
        BookDocInline,
    )
    list_display = (
        "title",
        "get_authors",
        "get_publisher",
        "publication_year",
        "number_of_pages",
        "published",
    )
    autocomplete_fields = ("authors", "publisher", "shop")
    readonly_fields = ("creation_time", "updated_time")
    search_fields = ("title", "publisher__name", "authors__last_name")
    list_filter = ("publisher__name", "authors")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "published",
                    "title",
                    "authors",
                    "publisher",
                    "ISBN",
                    "language",
                    "number_of_pages",
                    "publication_year",
                    "description",
                    "tags",
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

    @admin.display(description="Publisher")
    def get_publisher(self, obj):
        return obj.publisher.name

    @admin.display(description="Authors")
    def get_authors(self, obj):
        return obj.authors_list

    def download_csv(modeladmin, request, queryset):
        header = [
            "Title",
            "Authors",
            "Publisher",
            "ISBN",
            "Language",
            "Number of Pages",
            "Publication Year",
            "Description",
            "Tags",
            "Shop",
            "Purchase Date",
            "Price ({})".format(get_site_conf().currency),
            "Notes",
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
                    obj.title,
                    obj.authors_list.replace(",", settings.CSV_SEPARATOR_ALT),
                    obj.publisher.name,
                    obj.ISBN,
                    dict(settings.LANGUAGES)[obj.language],
                    obj.number_of_pages,
                    obj.publication_year,
                    html.unescape(strip_tags(obj.description)),
                    settings.CSV_SEPARATOR_ALT.join(
                        t.name for t in obj.tags.all()
                    ),
                    obj.shop,
                    obj.purchase_date,
                    obj.price,
                    html.unescape(strip_tags(obj.notes)),
                    properties,
                ]
            )

        return generate_csv(header, data, "bookshelf_books.csv")

    download_csv.short_description = "Download selected items as CSV"
    actions = [publish, unpublish, download_csv]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = (
        "first_name",
        "last_name",
    )
    list_filter = ("last_name",)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "country_flag")
    search_fields = ("name",)

    @admin.display(description="Country")
    def country_flag(self, obj):
        return format_html(
            '<img src="{}" /> {}'.format(obj.country.flag, obj.country.name)
        )


@admin.register(Catalog)
class CatalogAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (
        BookPropertyInline,
        BookImageInline,
        BookDocInline,
    )
    list_display = (
        "__str__",
        "manufacturer",
        "years",
        "get_scales",
        "published",
    )
    autocomplete_fields = ("manufacturer",)
    readonly_fields = ("creation_time", "updated_time")
    search_fields = ("manufacturer__name", "years", "scales__scale")
    list_filter = ("manufacturer__name", "publication_year", "scales__scale")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "published",
                    "manufacturer",
                    "years",
                    "scales",
                    "ISBN",
                    "language",
                    "number_of_pages",
                    "publication_year",
                    "description",
                    "tags",
                )
            },
        ),
        (
            "Purchase data",
            {
                "fields": (
                    "purchase_date",
                    "price",
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

    def download_csv(modeladmin, request, queryset):
        header = [
            "Catalog",
            "Manufacturer",
            "Years",
            "Scales",
            "ISBN",
            "Language",
            "Number of Pages",
            "Publication Year",
            "Description",
            "Tags",
            "Purchase Date",
            "Shop",
            "Price ({})".format(get_site_conf().currency),
            "Notes",
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
                    obj.__str__(),
                    obj.manufacturer.name,
                    obj.years,
                    obj.get_scales(),
                    obj.ISBN,
                    dict(settings.LANGUAGES)[obj.language],
                    obj.number_of_pages,
                    obj.publication_year,
                    html.unescape(strip_tags(obj.description)),
                    settings.CSV_SEPARATOR_ALT.join(
                        t.name for t in obj.tags.all()
                    ),
                    obj.shop,
                    obj.purchase_date,
                    obj.price,
                    html.unescape(strip_tags(obj.notes)),
                    properties,
                ]
            )

        return generate_csv(header, data, "bookshelf_catalogs.csv")

    download_csv.short_description = "Download selected items as CSV"
    actions = [publish, unpublish, download_csv]
