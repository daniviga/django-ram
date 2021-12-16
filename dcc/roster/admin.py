from django.contrib import admin
from roster.models import Cab, Decoder, Manufacturer


@admin.register(Cab)
class CabAdmin(admin.ModelAdmin):
    readonly_fields = ('image_thumbnail', 'creation_time', 'updated_time',)
    list_display = ('identifier', 'manufacturer', 'address')
    list_filter = list_display
    search_fields = list_display

    fieldsets = (
        (None, {
            'fields': ('identifier',
                       'address',
                       'manufacturer',
                       'decoder',
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


admin.site.register(Decoder)
admin.site.register(Manufacturer)
