from django.contrib import admin

from .models import (
    EmbedObject,
    FileObject,
    KitchenAIManagement,
    KitchenAIModule,
    KitchenAIRootModule,
    CodeFunction,
    CodeImport,
    CodeSetup,
    Notebook
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

@admin.register(CodeFunction)
class CodeFunctionAdmin(admin.ModelAdmin):
    pass


@admin.register(CodeImport)
class CodeImportAdmin(admin.ModelAdmin):
    pass

@admin.register(CodeSetup)
class CodeSetupAdmin(admin.ModelAdmin):
    pass


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
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
