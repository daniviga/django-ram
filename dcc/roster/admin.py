from django.contrib import admin
from roster.models import (
    RollingStock, RollingStockImage, RollingStockDocument, Engine, Car,
    Equipment, Other)


class RollingStockDocInline(admin.TabularInline):
    model = RollingStockDocument
    min_num = 0
    extra = 0


class RollingStockImageInline(admin.TabularInline):
    model = RollingStockImage
    min_num = 0
    extra = 0
    readonly_fields = ('image_thumbnail',)


class RollingStockAdmin(admin.ModelAdmin):
    inlines = (RollingStockImageInline, RollingStockDocInline)
    readonly_fields = ('creation_time', 'updated_time',)
    list_display = ('identifier', 'manufacturer', 'sku', 'company')
    list_filter = list_display
    search_fields = list_display

    fieldsets = (
        (None, {
            'fields': ('identifier',
                       'type',
                       'tags',
                       'manufacturer',
                       'sku',
                       'decoder',
                       'address',
                       'company',
                       'epoch',
                       'production_year',
                       'purchase_date',
                       'notes')
        }),
        ('Audit', {
            'classes': ('collapse',),
            'fields': ('creation_time', 'updated_time',)
        }),
    )


@admin.register(Engine)
class Engine(RollingStockAdmin):
    list_display = ('identifier', 'address', 'manufacturer', 'sku', 'company')


@admin.register(Car)
class Car(RollingStockAdmin):
    pass


@admin.register(Equipment)
class Equipment(RollingStockAdmin):
    pass


@admin.register(Other)
class Other(RollingStockAdmin):
    pass
