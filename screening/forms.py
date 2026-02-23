from django import forms
from .models import Resume

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file'] # We only ask the user for the file; AI extracts the rest!