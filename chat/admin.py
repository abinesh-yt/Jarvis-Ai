from django.contrib import admin
from .models import ChatSession, Message

admin.site.register(ChatSession)
admin.site.register(Message)

from .models import PDFFile

admin.site.register(PDFFile)


from .models import ImageFile

admin.site.register(ImageFile)

from .models import Memory

admin.site.register(Memory)