from django.contrib import admin

from .models import (
    EmbedObject,
    FileObject,
    KitchenAIManagement,
    KitchenAIRootModule,
    EmbedFunctionTokenCounts,
    StorageFunctionTokenCounts
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


@admin.register(EmbedFunctionTokenCounts)
class EmbedFunctionTokenCountsAdmin(admin.ModelAdmin):
    pass


@admin.register(StorageFunctionTokenCounts)
class StorageFunctionTokenCountsAdmin(admin.ModelAdmin):
    pass
