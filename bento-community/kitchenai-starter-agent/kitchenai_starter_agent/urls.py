from django.urls import path

from . import views

app_name = "rag_simple"

urlpatterns = [
    path("", views.home, name="home"),
    path('<str:bento_name>/settings/', views.settings_view, name='settings'),

]
