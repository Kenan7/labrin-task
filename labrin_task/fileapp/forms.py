from django import forms

from .models import FileModel


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileModel
        fields = [
            "name",
            "description",
            "file_itself",
        ]
