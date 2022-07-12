from django.urls import path
from roster.views import RosterList, RosterGet, RosterAddress, RosterClass

urlpatterns = [
    path("list", RosterList.as_view()),
    path("get/<str:uuid>", RosterGet.as_view()),
    path("address/<int:address>", RosterAddress.as_view()),
    path("class/<str:class>", RosterClass.as_view()),
]
