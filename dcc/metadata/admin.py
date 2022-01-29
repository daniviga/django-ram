from django.contrib import admin
from metadata.models import Decoder, Manufacturer, Company


@admin.register(Decoder)
class DecoderAdmin(admin.ModelAdmin):
    readonly_fields = ('image_thumbnail',)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    readonly_fields = ('logo_thumbnail',)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    readonly_fields = ('logo_thumbnail',)
