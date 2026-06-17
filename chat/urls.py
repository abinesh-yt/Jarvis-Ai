from django.urls import path
from .views import (
    chat_home,
    chat_detail,
    new_chat,
    delete_chat,
    rename_chat,
    profile,
    delete_memory
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
    path(
    "website/",
    views.website_summarizer,
    name="website_summarizer"
),
    
    path(
    "youtube/",
    views.youtube_summarizer,
    name="youtube_summarizer"
),
    path(
    "delete/<int:chat_id>/",
    views.delete_chat,
    name="delete_chat"
),
    
    path(
    "rename/<int:chat_id>/",
    rename_chat,
    name="rename_chat"
),
    
    path(
    "profile/",
    profile,
    name="profile"
),
    
    path(
    "memory/delete/<int:memory_id>/",
    delete_memory,
    name="delete_memory"
),
    
]

