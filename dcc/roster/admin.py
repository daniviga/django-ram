from django.contrib import admin
from roster.models import (
    RollingClass, RollingStock, RollingStockImage, RollingStockDocument)


@admin.register(RollingClass)
class RollingClass(admin.ModelAdmin):
    list_display = ('__str__', 'type', 'company')
    list_filter = ('type', 'company')
    search_fields = list_display


class RollingStockDocInline(admin.TabularInline):
    model = RollingStockDocument
    min_num = 0
    extra = 0


class RollingStockImageInline(admin.TabularInline):
    model = RollingStockImage
    min_num = 0
    extra = 0
    readonly_fields = ('image_thumbnail',)


@admin.register(RollingStock)
class RollingStockAdmin(admin.ModelAdmin):
    inlines = (RollingStockImageInline, RollingStockDocInline)
    readonly_fields = ('creation_time', 'updated_time')
    list_display = (
        '__str__', 'manufacturer', 'scale', 'sku', 'company', 'country')
    list_filter = ('manufacturer', 'scale')
    search_fields = list_display

    fieldsets = (
        (None, {
            'fields': ('rolling_class',
                       'road_number',
                       'manufacturer',
                       'scale',
                       'sku',
                       'decoder',
                       'address',
                       'era',
                       'production_year',
                       'purchase_date',
                       'notes',
                       'tags')
        }),
        ('Audit', {
            'classes': ('collapse',),
            'fields': ('creation_time', 'updated_time',)
        }),
    )
