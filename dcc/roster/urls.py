from django.urls import path
from roster.views import (
    RosterList, RosterGet, RosterAddress, RosterIdentifier)

urlpatterns = [
    path('list', RosterList.as_view()),
    path('get/<str:uuid>', RosterGet.as_view()),
    path('address/<int:address>', RosterAddress.as_view()),
    path('identifier/<str:identifier>', RosterIdentifier.as_view()),
]
