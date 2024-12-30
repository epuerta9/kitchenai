from django.contrib import admin

from .models import Bento, LoadedBento


@admin.register(Bento)
class BentoAdmin(admin.ModelAdmin):
    pass

@admin.register(LoadedBento)
class LoadedBentoAdmin(admin.ModelAdmin):
    pass
