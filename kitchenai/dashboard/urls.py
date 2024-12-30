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
]
