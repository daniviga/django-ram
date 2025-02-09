from django.db import models

from tinymce import models as tinymce

from ram.models import Document
from metadata.models import Decoder, Tag
from roster.models import RollingStock
from bookshelf.models import BaseBook


class GenericDocument(Document):
    notes = tinymce.HTMLField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="new_document")

    class Meta:
        verbose_name_plural = "Generic Documents"


class DecoderDocument(Document):
    decoder = models.ForeignKey(
        Decoder, on_delete=models.CASCADE, related_name="new_document"
    )

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=["decoder", "file"],
    #             name="unique_decoder_file"
    #         )
    #     ]


class BaseBookDocument(Document):
    book = models.ForeignKey(
        BaseBook, on_delete=models.CASCADE, related_name="new_document"
    )

    # class Meta:
    #     verbose_name_plural = "Documents"
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=["book", "file"],
    #             name="unique_book_file"
    #         )
    #     ]


class RollingStockDocument(Document):
    rolling_stock = models.ForeignKey(
        RollingStock, on_delete=models.CASCADE, related_name="new_document"
    )

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=["rolling_stock", "file"],
    #             name="unique_stock_file"
    #         )
    #     ]
