from django.contrib import admin

from .models import (
    EmbedObject,
    FileObject,
    KitchenAIManagement,
    KitchenAIModule,
    KitchenAIRootModule,
)


@admin.register(KitchenAIManagement)
class KitchenAIAdmin(admin.ModelAdmin):
    pass


@admin.register(FileObject)
class FileObjectAdmin(admin.ModelAdmin):
    pass


@admin.register(EmbedObject)
class EmbedObjectAdmin(admin.ModelAdmin):
    pass


@admin.register(KitchenAIRootModule)
class KitchenAIRootModuleAdmin(admin.ModelAdmin):
    pass


@admin.register(KitchenAIModule)
class KitchenAIModuleAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "updated_at",
        "name",
        "kitchen",
        "jupyter_path",
        "file",
    )
    list_filter = ("created_at", "updated_at", "kitchen")
    search_fields = ("name",)
    date_hierarchy = "created_at"
