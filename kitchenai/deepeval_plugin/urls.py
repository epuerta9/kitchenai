from django.urls import path

from . import views

app_name = "deepeval"

urlpatterns = [
    path("", views.home, name="home"),
    path("dataset/<int:dataset_id>/", views.dataset, name="dataset"),
    path("chat_widget/<int:source_id>/", views.chat_widget_for_source, name="chat_widget_for_source"),
    path("check_results/<int:source_id>/<str:test_name>/", views.check_results, name="check_results"),
    path("settings/", views.settings, name="settings"),
]
