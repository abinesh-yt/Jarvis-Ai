from django.urls import path
from .views import (
    chat_home,
    chat_detail,
    new_chat,
    delete_chat,
    youtube_history,
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
    
    path(
    "youtube/history/",
    views.youtube_history,
    name="youtube_history"
),
    
    path(
    "youtube/video/<int:video_id>/",
    views.youtube_video_detail,
    name="youtube_video_detail"
),
    
    path(
    "pdf/library/",
    views.pdf_library,
    name="pdf_library"
),
    
    
    

    
    path(
    "image/library/",
    views.image_library,
    name="image_library"
),

path(
    "image/delete/<int:image_id>/",
    views.delete_image,
    name="delete_image"
),
path(
    "website/library/",
    views.website_library,
    name="website_library"
),




path(
    "website/<int:website_id>/",
    views.website_detail,
    name="website_detail"
),



path(
    "pdf/delete/<int:pdf_id>/",
    views.delete_pdf,
    name="delete_pdf"
),

path(
    "video/delete/<int:video_id>/",
    views.delete_video,
    name="delete_video"
),

path(
    "website/delete/<int:website_id>/",
    views.delete_website,
    name="delete_website"
),

path(
    "favorite/<int:chat_id>/",
    views.toggle_favorite,
    name="toggle_favorite"
),

path(
    "pin/<int:chat_id>/",
    views.toggle_pin,
    name="toggle_pin"
),

path(
    "export/chat/<int:chat_id>/",
    views.export_chat_pdf,
    name="export_chat_pdf"
),
path(
    "<int:chat_id>/",
    chat_detail,
    name="chat_detail"
),
    
]

