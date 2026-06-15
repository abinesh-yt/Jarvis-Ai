from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from chat.models import (
    ChatSession,
    PDFFile,
    ImageFile,
    Memory
)


@login_required
def dashboard(request):

    chat_count = ChatSession.objects.filter(
        user=request.user
    ).count()

    pdf_count = PDFFile.objects.filter(
        user=request.user
    ).count()

    image_count = ImageFile.objects.filter(
        user=request.user
    ).count()

    memory_count = Memory.objects.filter(
        user=request.user
    ).count()

    recent_chats = ChatSession.objects.filter(
        user=request.user
    ).order_by("-created_at")[:5]

    recent_pdfs = PDFFile.objects.filter(
        user=request.user
    ).order_by("-uploaded_at")[:5]

    context = {

        "chat_count": chat_count,
        "pdf_count": pdf_count,
        "image_count": image_count,
        "memory_count": memory_count,

        "recent_chats": recent_chats,
        "recent_pdfs": recent_pdfs,

    }

    return render(
        request,
        "dashboard.html",
        context
    )