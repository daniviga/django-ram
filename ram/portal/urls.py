from django.urls import path

from portal.views import GetHome

urlpatterns = [
    path("<int:page>", GetHome.as_view(), name='index_pagination'),
]
