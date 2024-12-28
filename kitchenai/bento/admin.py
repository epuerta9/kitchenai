from django.contrib import admin

from .models import Bento


@admin.register(Bento)
class BentoAdmin(admin.ModelAdmin):
    pass