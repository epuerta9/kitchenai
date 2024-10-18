from django.contrib import admin

from .models import KitchenAIManagement, KitchenAIModules

@admin.register(KitchenAIManagement)
class KitchenAIAdmin(admin.ModelAdmin):
    pass



@admin.register(KitchenAIModules)
class KitchenAIModuleAdmin(admin.ModelAdmin):
    pass