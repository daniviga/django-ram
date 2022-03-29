from django.contrib import admin
from metadata.models import Decoder, Manufacturer, Company, Tag


@admin.register(Decoder)
class DecoderAdmin(admin.ModelAdmin):
    readonly_fields = ('image_thumbnail',)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    readonly_fields = ('logo_thumbnail',)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    readonly_fields = ('logo_thumbnail',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)
