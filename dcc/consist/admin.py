from django.contrib import admin
from adminsortable2.admin import SortableInlineAdminMixin

from consist.models import Consist, ConsistItem


class ConsistItemInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ConsistItem
    min_num = 1
    extra = 0
    readonly_fields = ('address', 'company', 'epoch')


@admin.register(Consist)
class ConsistAdmin(admin.ModelAdmin):
    inlines = (ConsistItemInline,)
    readonly_fields = ('creation_time', 'updated_time',)
    list_display = ('identifier', 'company', 'epoch')
    list_filter = list_display
    search_fields = list_display

    fieldsets = (
        (None, {
            'fields': ('identifier',
                       'address',
                       'tags',
                       'company',
                       'epoch',
                       'notes')
        }),
        ('Audit', {
            'classes': ('collapse',),
            'fields': ('creation_time', 'updated_time',)
        }),
    )
