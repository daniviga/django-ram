from django.contrib import admin
from django.db.utils import OperationalError
from portal.utils import get_site_conf

try:
    site_name = get_site_conf().site_name
except OperationalError:
    site_name = "Train Assets Manager"

admin.site.site_header = site_name
