from django.urls import path

from . import views

app_name = "deepeval"

urlpatterns = [
    path("", views.home, name="home"),
    path("chat_widget/<int:source_id>/", views.chat_widget_for_source, name="chat_widget_for_source"),
]
