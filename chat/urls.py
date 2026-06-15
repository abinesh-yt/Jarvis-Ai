from django.urls import path
from .views import (
    chat_home,
    new_chat,
    chat_detail
)
from . import views

urlpatterns = [
    path('', chat_home, name='chat_home'),
    path('new/', new_chat, name='new_chat'),
    path('<int:chat_id>/', chat_detail, name='chat_detail'),
    path(
    "pdfs/",
    views.upload_pdf,
    name="upload_pdf"
),
    
  
    path(
    "pdf/<int:pdf_id>/",
    views.pdf_detail,
    name="pdf_detail"
),
    
    path(
    "images/",
    views.upload_image,
    name="upload_image"
),
    
    path(
    "image/<int:image_id>/",
    views.image_detail,
    name="image_detail"
),
    
    path(
    "memories/",
    views.memories,
    name="memories"
),
    
]

