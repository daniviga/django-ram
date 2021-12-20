from django.contrib import admin
from metadata.models import Decoder, Manufacturer, Company

admin.site.register(Decoder)
admin.site.register(Company)
admin.site.register(Manufacturer)
