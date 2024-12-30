from django import forms
from kitchenai.core.models import FileObject, EmbedObject

class FileUploadForm(forms.ModelForm):
    metadata = forms.JSONField(required=False, widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = FileObject
        fields = ['file', 'name', 'ingest_label', 'metadata']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'ingest_label': forms.TextInput(attrs={'class': 'input input-bordered w-full'})
        }
        labels = {
            'file': 'File',
            'ingest_label': 'Ingest Label'
        }
        help_texts = {
            'file': 'Select a file to upload',
            'ingest_label': 'Enter a label to identify this file ingestion'
        }
        error_messages = {
            'file': {
                'required': 'Please select a file to upload', 
                'invalid': 'Please upload a valid file'
            },
            'ingest_label': {
                'required': 'Please enter an ingest label',
                'max_length': 'Ingest label must be less than 255 characters'
            }
        }


class EmbeddingForm(forms.ModelForm):
    metadata = forms.JSONField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = EmbedObject
        fields = ['text', 'ingest_label', 'metadata']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full'}),
            'ingest_label': forms.TextInput(attrs={'class': 'input input-bordered w-full'})
        }
        labels = {
            'text': 'Text to Embed',
            'ingest_label': 'Ingest Label'
        }
        help_texts = {
            'text': 'Enter the text you want to embed',
            'ingest_label': 'Enter a label to identify this embedding'
        }
        error_messages = {
            'text': {
                'required': 'Please enter text to embed',
                'max_length': 'Text must be less than 255 characters'
            },
            'ingest_label': {
                'required': 'Please enter an ingest label',
                'max_length': 'Ingest label must be less than 255 characters'
            }
        }

