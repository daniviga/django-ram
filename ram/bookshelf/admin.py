import html

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html, format_html_join, strip_tags
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from ram.admin import publish, unpublish
from ram.utils import generate_csv
from portal.utils import get_site_conf
from repository.models import (
    BookDocument,
    CatalogDocument,
    MagazineIssueDocument
)
from bookshelf.models import (
    BaseBookProperty,
    BaseBookImage,
    Book,
    Author,
    Publisher,
    Catalog,
    Magazine,
    MagazineIssue,
)


class BookImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = BaseBookImage
    min_num = 0
    extra = 0
    readonly_fields = ("image_thumbnail",)
    classes = ["collapse"]
    verbose_name = "Image"


class BookPropertyInline(admin.TabularInline):
    model = BaseBookProperty
    min_num = 0
    extra = 0
    autocomplete_fields = ("property",)
    verbose_name = "Property"
    verbose_name_plural = "Properties"


class BookDocInline(admin.TabularInline):
    model = BookDocument
    min_num = 0
    extra = 0
    classes = ["collapse"]


class CatalogDocInline(BookDocInline):
    model = CatalogDocument


class MagazineIssueDocInline(BookDocInline):
    model = MagazineIssueDocument


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
    readonly_fields = ("invoices", "creation_time", "updated_time")
    search_fields = ("title", "publisher__name", "authors__last_name")
    list_filter = ("publisher__name", "authors", "published")

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
            '<img src="{}" /> {}', obj.country.flag, obj.country.name
        )


@admin.register(Catalog)
class CatalogAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (
        BookPropertyInline,
        BookImageInline,
        CatalogDocInline,
    )
    list_display = (
        "__str__",
        "manufacturer",
        "years",
        "get_scales",
        "published",
    )
    autocomplete_fields = ("manufacturer",)
    readonly_fields = ("invoices", "creation_time", "updated_time")
    search_fields = ("manufacturer__name", "years", "scales__scale")
    list_filter = (
        "manufacturer__name",
        "publication_year",
        "scales__scale",
        "published",
    )

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


@admin.register(MagazineIssue)
class MagazineIssueAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (
        BookPropertyInline,
        BookImageInline,
        MagazineIssueDocInline,
    )
    list_display = (
        "__str__",
        "issue_number",
        "published",
    )
    autocomplete_fields = ("shop",)
    readonly_fields = ("magazine", "creation_time", "updated_time")

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "published",
                    "magazine",
                    "issue_number",
                    "publication_year",
                    "publication_month",
                    "ISBN",
                    "language",
                    "number_of_pages",
                    "description",
                    "tags",
                )
            },
        ),
        (
            "Purchase data",
            {
                "classes": ("collapse",),
                "fields": (
                    "shop",
                    "purchase_date",
                    "price",
                ),
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
    actions = [publish, unpublish]


class MagazineIssueInline(admin.TabularInline):
    model = MagazineIssue
    min_num = 0
    extra = 0
    autocomplete_fields = ("shop",)
    show_change_link = True
    fields = (
        "preview",
        "published",
        "issue_number",
        "publication_year",
        "publication_month",
        "number_of_pages",
        "language",
    )
    readonly_fields = ("preview",)

    class Media:
        js = ('admin/js/magazine_issue_defaults.js',)


@admin.register(Magazine)
class MagazineAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = (
        MagazineIssueInline,
    )

    list_display = (
        "__str__",
        "publisher",
        "published",
    )
    autocomplete_fields = ("publisher",)
    readonly_fields = ("creation_time", "updated_time")
    search_fields = ("name", "publisher__name")
    list_filter = ("publisher__name", "published")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "published",
                    "name",
                    "website",
                    "publisher",
                    "ISBN",
                    "language",
                    "description",
                    "image",
                    "tags",
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
    actions = [publish, unpublish]
