from django.db import models

from tinymce import models as tinymce

from ram.models import PrivateDocument
from metadata.models import Decoder, Tag
from roster.models import RollingStock
from bookshelf.models import Book, Catalog, BaseBook


class GenericDocument(PrivateDocument):
    notes = tinymce.HTMLField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="document")

    class Meta:
        verbose_name_plural = "Generic documents"


class InvoiceDocument(PrivateDocument):
    private = models.BooleanField(default=True, editable=False)
    rolling_stock = models.ManyToManyField(
        RollingStock, related_name="invoice",
        blank=True
    )
    book = models.ManyToManyField(
        Book, related_name="invoice",
        blank=True
    )
    catalog = models.ManyToManyField(
        Catalog, related_name="invoice",
        blank=True
    )
    notes = tinymce.HTMLField(blank=True)

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"


class DecoderDocument(PrivateDocument):
    decoder = models.ForeignKey(
        Decoder, on_delete=models.CASCADE, related_name="document"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["decoder", "file"],
                name="unique_decoder_file"
            )
        ]


class BaseBookDocument(PrivateDocument):
    book = models.ForeignKey(
        BaseBook, on_delete=models.CASCADE, related_name="document"
    )

    class Meta:
        verbose_name_plural = "Bookshelf Documents"
        constraints = [
            models.UniqueConstraint(
                fields=["book", "file"],
                name="unique_book_file"
            )
        ]


class RollingStockDocument(PrivateDocument):
    rolling_stock = models.ForeignKey(
        RollingStock, on_delete=models.CASCADE, related_name="document"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["rolling_stock", "file"],
                name="unique_stock_file"
            )
        ]
