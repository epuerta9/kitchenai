from django import forms

from .models import KitchenAIModule


class KitchenAIModuleForm(forms.ModelForm):
    class Meta:
        model = KitchenAIModule
        fields = ("name", "kitchen", "jupyter_path", "file")
