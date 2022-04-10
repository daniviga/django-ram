from django.urls import path
from driver.views import SendCommand, Function, Cab, Emergency, Infra, Test

urlpatterns = [
    path("test", Test.as_view()),
    path("emergency", Emergency.as_view()),
    path("infra", Infra.as_view()),
    path("command", SendCommand.as_view()),
    path("<int:address>/cab", Cab.as_view()),
    path("<int:address>/function", Function.as_view()),
]
