from django import forms
from .models import PDFFile
from .models import ImageFile
from .models import Memory

class PDFUploadForm(forms.ModelForm):

    class Meta:
        model = PDFFile
        fields = ["file"]
        
class ImageUploadForm(forms.ModelForm):

    class Meta:
        model = ImageFile
        fields = ["image"]
        
class MemoryForm(forms.ModelForm):

    class Meta:
        model = Memory
        fields = ["content"]