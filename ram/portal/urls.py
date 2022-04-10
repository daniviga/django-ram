from django.urls import path

from portal.views import GetHome, GetRollingStock

urlpatterns = [
    path("<int:page>", GetHome.as_view(), name='index_pagination'),
    path("<uuid:uuid>", GetRollingStock.as_view(), name='rollig_stock'),
]
