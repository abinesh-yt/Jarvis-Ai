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

    is_favorite = models.BooleanField(
        default=False
    )

    is_pinned = models.BooleanField(
        default=False
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
    
    
class PDFFile(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to="pdfs/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )
    

class ImageFile(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    image = models.ImageField(
        upload_to="images/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )
    
class Memory(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.content[:50]
    
    
class YouTubeVideo(models.Model):


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=500
    )

    url = models.URLField()

    channel = models.CharField(
        max_length=255
    )

    thumbnail = models.URLField()

    transcript = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.title



class PDFMessage(models.Model):


    pdf = models.ForeignKey(
        PDFFile,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(
        max_length=20
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.role}: "
            f"{self.content[:30]}"
        )


class VideoMessage(models.Model):


    video = models.ForeignKey(
        YouTubeVideo,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(
        max_length=20
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.role}: "
            f"{self.content[:30]}"
        )
        
        
        
        
class UserXP(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    points = models.IntegerField(
        default=0
    )

    streak = models.IntegerField(
        default=0
    )

    best_streak = models.IntegerField(
        default=0
    )

    last_login_date = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.points} XP"
        )    
    


class ImageMessage(models.Model):

    image = models.ForeignKey(
        ImageFile,
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

        return (
            f"{self.role}: "
            f"{self.content[:30]}"
        )
        
        
        
        
class Website(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    url = models.URLField()

    title = models.CharField(
        max_length=500
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.title


class WebsiteMessage(models.Model):

    website = models.ForeignKey(
        Website,
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

        return (
            f"{self.role}: "
            f"{self.content[:30]}"
        )

