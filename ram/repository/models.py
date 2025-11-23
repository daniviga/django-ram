from django.db import models

from tinymce import models as tinymce

from ram.models import PrivateDocument
from metadata.models import Decoder, Shop, Tag
from roster.models import RollingStock
from bookshelf.models import Book, Catalog, Issue


class GenericDocument(PrivateDocument):
    notes = tinymce.HTMLField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="document")

    class Meta:
        verbose_name_plural = "Generic documents"


class InvoiceDocument(PrivateDocument):
    private = models.BooleanField(default=True, editable=False)
    rolling_stock = models.ManyToManyField(
        RollingStock, related_name="invoice", blank=True
    )
    book = models.ManyToManyField(Book, related_name="invoice", blank=True)
    catalog = models.ManyToManyField(
        Catalog, related_name="invoice", blank=True
    )
    date = models.DateField()
    shop = models.ForeignKey(
        Shop, on_delete=models.SET_NULL, null=True, blank=True
    )
    file = models.FileField(
        upload_to="files/invoices/",
    )
    notes = tinymce.HTMLField(blank=True)


class DecoderDocument(PrivateDocument):
    decoder = models.ForeignKey(
        Decoder, on_delete=models.CASCADE, related_name="document"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["decoder", "file"], name="unique_decoder_file"
            )
        ]


class BookDocument(PrivateDocument):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="document"
    )

    class Meta:
        verbose_name_plural = "Book documents"
        constraints = [
            models.UniqueConstraint(
                fields=["book", "file"], name="unique_book_file"
            )
        ]


class CatalogDocument(PrivateDocument):
    catalog = models.ForeignKey(
        Catalog, on_delete=models.CASCADE, related_name="document"
    )

    class Meta:
        verbose_name_plural = "Catalog documents"
        constraints = [
            models.UniqueConstraint(
                fields=["catalog", "file"], name="unique_catalog_file"
            )
        ]


class MagazineIssueDocument(PrivateDocument):
    issue = models.ForeignKey(
        Issue, on_delete=models.CASCADE, related_name="document"
    )

    class Meta:
        verbose_name_plural = "Magazines documents"
        constraints = [
            models.UniqueConstraint(
                fields=["issue", "file"], name="unique_issue_file"
            )
        ]


class RollingStockDocument(PrivateDocument):
    rolling_stock = models.ForeignKey(
        RollingStock, on_delete=models.CASCADE, related_name="document"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["rolling_stock", "file"], name="unique_stock_file"
            )
        ]
