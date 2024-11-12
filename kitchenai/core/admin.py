from django.contrib import admin

from .models import KitchenAIManagement
from .models import FileObject, KitchenAIRootModule

@admin.register(KitchenAIManagement)
class KitchenAIAdmin(admin.ModelAdmin):
    pass


@admin.register(FileObject)
class FileObjectAdmin(admin.ModelAdmin):
    pass

@admin.register(KitchenAIRootModule)
class KitchenAIRootModuleAdmin(admin.ModelAdmin):
    pass