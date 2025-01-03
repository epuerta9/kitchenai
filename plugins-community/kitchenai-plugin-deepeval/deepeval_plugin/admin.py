from django.contrib import admin

# Register your models here.
from .models import DataSet, Data, AnswerRelevance, Faithfulness, ContextualRelevancy, Hallucination, Toxicity

@admin.register(DataSet)
class DataSetAdmin(admin.ModelAdmin):
    pass

@admin.register(Data) 
class DataAdmin(admin.ModelAdmin):
    pass

@admin.register(AnswerRelevance)
class AnswerRelevanceAdmin(admin.ModelAdmin):
    pass

@admin.register(Faithfulness)
class FaithfulnessAdmin(admin.ModelAdmin):
    pass

@admin.register(ContextualRelevancy)
class ContextualRelevancyAdmin(admin.ModelAdmin):
    pass

@admin.register(Hallucination)
class HallucinationAdmin(admin.ModelAdmin):
    pass

@admin.register(Toxicity)
class ToxicityAdmin(admin.ModelAdmin):
    pass