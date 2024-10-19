from django.contrib import admin

from .models import KitchenAIManagement
from .models import KitchenAIModules

@admin.register(KitchenAIManagement)
class KitchenAIAdmin(admin.ModelAdmin):
    pass



@admin.register(KitchenAIModules)
class KitchenAIModuleAdmin(admin.ModelAdmin):
    pass
