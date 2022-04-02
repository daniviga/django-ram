from django.urls import path
from consist.views import ConsistList

urlpatterns = [
    path("list", ConsistList.as_view()),
]
