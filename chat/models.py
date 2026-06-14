from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255,
        default="New Chat"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class Message(models.Model):

    chat = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.role}: {self.content[:30]}"