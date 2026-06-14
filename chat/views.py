from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatSession
from .models import ChatSession, Message
from .ai import get_ai_response


@login_required
def chat_home(request):

    chats = ChatSession.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'chat/chat.html',
        {'chats': chats}
    )


@login_required
def new_chat(request):

    chat = ChatSession.objects.create(
        user=request.user,
        title="New Chat"
    )

    return redirect(f'/chat/{chat.id}/')

@login_required
def chat_detail(request, chat_id):

    chat = ChatSession.objects.get(
        id=chat_id,
        user=request.user
    )

    if request.method == "POST":

        content = request.POST.get("message")

        if content:

            Message.objects.create(
                chat=chat,
                role="user",
                content=content
            )
            
            if chat.title == "New Chat":

                chat.title = content[:40]
                chat.save()

            ai_response = get_ai_response(content)

            Message.objects.create(
                chat=chat,
                role="assistant",
                content=ai_response
            )

        return redirect(f"/chat/{chat.id}/")

    messages = Message.objects.filter(
        chat=chat
    ).order_by('created_at')

    return render(
        request,
        'chat/chat_detail.html',
        {
            'chat': chat,
            'messages': messages
        }
    )