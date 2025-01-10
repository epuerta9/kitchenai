from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("file", views.file, name="file"),
    path("file/delete/<int:file_id>", views.delete_file, name="delete_file"),
    path("labels", views.labels, name="labels"),
    path("embeddings", views.embeddings, name="embeddings"),    
    path("embeddings/delete/<int:embedding_id>", views.delete_embedding, name="delete_embedding"),
    path("chat", views.chat, name="chat"),
    path("chat/<int:chat_id>", views.chat_session, name="chat_session"),
    path("chat/<int:chat_id>/send", views.chat_send, name="chat_send"),
    path("chat/<int:chat_id>/aggregated", views.aggregated_metrics, name="aggregated_metrics"),
    path("chat/<int:chat_id>/delete", views.chat_delete, name="chat_delete"),
    path("chat/<int:chat_id>/settings", views.chat_settings, name="chat_settings"),
    path("settings", views.settings_view, name="settings"),
]
