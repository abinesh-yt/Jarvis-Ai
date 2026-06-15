from django import forms
from .models import PDFFile
from .models import ImageFile

class PDFUploadForm(forms.ModelForm):

    class Meta:
        model = PDFFile
        fields = ["file"]
        
class ImageUploadForm(forms.ModelForm):

    class Meta:
        model = ImageFile
        fields = ["image"]