from django.contrib import admin
from roster.models import RollingStock


@admin.register(RollingStock)
class RollingStockAdmin(admin.ModelAdmin):
    readonly_fields = ('image_thumbnail', 'creation_time', 'updated_time',)
    list_display = ('identifier', 'address', 'manufacturer', 'company')
    list_filter = list_display
    search_fields = list_display

    fieldsets = (
        (None, {
            'fields': ('identifier',
                       'tags',
                       'address',
                       'manufacturer',
                       'decoder',
                       'company',
                       'epoch',
                       'production_year',
                       'purchase_date',
                       'image',
                       'image_thumbnail',
                       'notes')
        }),
        ('Audit', {
            'classes': ('collapse',),
            'fields': ('creation_time', 'updated_time',)
        }),
    )
