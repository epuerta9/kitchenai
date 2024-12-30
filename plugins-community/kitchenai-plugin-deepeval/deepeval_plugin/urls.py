from django.urls import path

from . import views

app_name = "deepeval"

urlpatterns = [
    path("", views.home, name="home"),
]
