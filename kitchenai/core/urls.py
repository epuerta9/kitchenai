from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
]

urlpatterns += [
    path(
        "kitchen-ai-modules/", views.kitchenaimodule_list, name="kitchenaimodule_list"
    ),
    path(
        "kitchen-ai-modules/create/",
        views.kitchenaimodule_create,
        name="kitchenaimodule_create",
    ),
    path(
        "kitchen-ai-modules/<int:pk>/",
        views.kitchenaimodule_detail,
        name="kitchenaimodule_detail",
    ),
    path(
        "kitchen-ai-modules/<int:pk>/update/",
        views.kitchenaimodule_update,
        name="kitchenaimodule_update",
    ),
    path(
        "kitchen-ai-modules/<int:pk>/delete/",
        views.kitchenaimodule_delete,
        name="kitchenaimodule_delete",
    ),
]
