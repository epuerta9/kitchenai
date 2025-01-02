from django.contrib import admin

# Register your models here.
from .models import DataSet, Data, AnswerRelevance

@admin.register(DataSet)
class DataSetAdmin(admin.ModelAdmin):
    pass

@admin.register(Data) 
class DataAdmin(admin.ModelAdmin):
    pass

@admin.register(AnswerRelevance)
class AnswerRelevanceAdmin(admin.ModelAdmin):
    pass
