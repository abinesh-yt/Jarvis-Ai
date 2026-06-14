from django.urls import path
from .views import (
    chat_home,
    new_chat,
    chat_detail
)

urlpatterns = [
    path('', chat_home, name='chat_home'),
    path('new/', new_chat, name='new_chat'),
    path('<int:chat_id>/', chat_detail, name='chat_detail'),
]