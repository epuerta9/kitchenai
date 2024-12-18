from django.contrib import admin

from .models import CodeFunction, CodeImport, CodeSetup, Notebook
    

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