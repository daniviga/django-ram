from django.contrib import admin
from solo.admin import SingletonModelAdmin

from driver.models import DriverConfiguration

admin.site.register(DriverConfiguration, SingletonModelAdmin)
