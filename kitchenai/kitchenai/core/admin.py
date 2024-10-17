from django.contrib import admin

from .models import Core

@admin.register(Core)
class WorkbookAdmin(admin.ModelAdmin):
    pass