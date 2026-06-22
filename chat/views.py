from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import (
    ChatSession,
    Message,
    PDFFile,
    PDFMessage,
    ImageFile,
    ImageMessage,
    Memory,
    YouTubeVideo,
    VideoMessage
)


import requests

from bs4 import BeautifulSoup

from .models import (
    Website,
    WebsiteMessage
)

from .models import Website, WebsiteMessage
from .models import UserXP
from .ai import get_ai_response
from .forms import PDFUploadForm
from pypdf import PdfReader
from groq import Groq
import os
from .forms import ImageUploadForm
import google.generativeai as genai
import PIL.Image
from .forms import MemoryForm
import requests
from bs4 import BeautifulSoup
from .forms import WebsiteForm
from django.shortcuts import get_object_or_404
from youtube_transcript_api import YouTubeTranscriptApi
from .forms import YouTubeForm
from django.contrib.auth.decorators import login_required
import yt_dlp
from django.http import HttpResponse

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

@login_required
def chat_home(request):

    query = request.GET.get(
        "q",
        ""
    )

    chats = ChatSession.objects.filter(
        user=request.user
    )

    if query:

        chats = chats.filter(
            title__icontains=query
        )

    pinned_chats = chats.filter(
        is_pinned=True
    ).order_by(
        "-created_at"
    )

    favorite_chats = chats.filter(
        is_favorite=True
    ).order_by(
        "-created_at"
    )

    chats = chats.order_by(
        "-is_pinned",
        "-created_at"
    )

    context = {

        "chats": chats,

        "pinned_chats":
        pinned_chats,

        "favorite_chats":
        favorite_chats,

        "query": query,

        "total_chats":
        chats.count()

    }

    return render(
        request,
        "chat/chat.html",
        context
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

    xp, created = UserXP.objects.get_or_create(
        user=request.user,
        defaults={
            "points": 0
        }
    )

    if request.method == "POST":

        content = request.POST.get(
            "message"
        )

        if not content:
            return redirect(
                f"/chat/{chat.id}/"
            )

        # Remember

        if content.lower().startswith(
            "remember"
        ):

            Memory.objects.create(
                user=request.user,
                content=content
            )

            xp.points += 5
            xp.save()

            Message.objects.create(
                chat=chat,
                role="assistant",
                content=(
                    "🧠 Memory saved successfully!\n\n"
                    "🏆 +5 XP earned!"
                )
            )

            return redirect(
                f"/chat/{chat.id}/"
            )

        # Forget

        elif content.lower().startswith(
            "forget"
        ):

            keyword = content.replace(
                "forget",
                ""
            ).strip()

            memories = Memory.objects.filter(
                user=request.user,
                content__icontains=keyword
            )

            count = memories.count()

            memories.delete()

            Message.objects.create(
                chat=chat,
                role="assistant",
                content=(
                    f"🗑️ Deleted "
                    f"{count} memory(s)."
                )
            )

            return redirect(
                f"/chat/{chat.id}/"
            )

        # Show Memories

        elif content.lower() == (
            "show memories"
        ):

            memories = Memory.objects.filter(
                user=request.user
            )

            memory_list = "\n".join(
                [
                    f"• {m.content}"
                    for m in memories
                ]
            )

            Message.objects.create(
                chat=chat,
                role="assistant",
                content=(
                    f"🧠 Your Memories:\n\n"
                    f"{memory_list}"
                )
            )

            return redirect(
                f"/chat/{chat.id}/"
            )

        # Save User Message

        Message.objects.create(
            chat=chat,
            role="user",
            content=content
        )

        xp.points += 2
        xp.save()

        # Auto Title

        if chat.title == "New Chat":

            chat.title = content[:40]

            chat.save()

        # Memories

        memories = Memory.objects.filter(
            user=request.user
        )

        memory_text = "\n".join(
            [
                memory.content
                for memory in memories
            ]
        )

        # History

        history = Message.objects.filter(
            chat=chat
        ).order_by("created_at")

        history_text = ""

        for msg in history:

            history_text += (
                f"{msg.role}: "
                f"{msg.content}\n"
            )

        prompt = f"""


    You are JARVIS AI.

    Conversation History:

    {history_text}

    User Memories:

    {memory_text}

    Current User Message:

    {content}

    Use conversation history and memories when relevant.

    """


        ai_response = get_ai_response(
            prompt
        )

        Message.objects.create(
            chat=chat,
            role="assistant",
            content=(
                ai_response
            )
        )

        return redirect(
            f"/chat/{chat.id}/"
        )

    messages = Message.objects.filter(
        chat=chat
    ).order_by("created_at")

    return render(
        request,
        "chat/chat_detail.html",
        {
            "chat": chat,
            "messages": messages
        }
    )



    
    
@login_required
def upload_pdf(request):


    if request.method == "POST":

        form = PDFUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            pdf = form.save(
                commit=False
            )

            pdf.user = request.user

            pdf.save()

            xp, created = (
                UserXP.objects.get_or_create(
                    user=request.user,
                    defaults={
                        "points": 0
                    }
                )
            )

            xp.points += 10
            xp.save()

            return redirect(
                "upload_pdf"
            )

    else:

        form = PDFUploadForm()

    pdfs = PDFFile.objects.filter(
        user=request.user
    ).order_by(
        "-uploaded_at"
    )

    return render(
        request,
        "chat/upload_pdf.html",
        {
            "form": form,
            "pdfs": pdfs
        }
    )
    

    

@login_required
def pdf_detail(request, pdf_id):

    pdf = PDFFile.objects.get(
        id=pdf_id,
        user=request.user
    )

    reader = PdfReader(
        pdf.file.path
    )

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text

    summary = None
    question = ""
    answer = None

    pdf_messages = PDFMessage.objects.filter(
        pdf=pdf
    ).order_by("created_at")

    if request.method == "POST":

        try:

            if "summarize" in request.POST:

                prompt = f"""

You are JARVIS AI.

Summarize this PDF in simple language.

PDF Content:

{text[:8000]}
"""

                summary = get_ai_response(
                    prompt
                )

            elif "ask" in request.POST:

                question = request.POST.get(
                    "question",
                    ""
                )

                history = ""

                recent_messages = PDFMessage.objects.filter(
                    pdf=pdf
                ).order_by("-created_at")[:10]

                for msg in reversed(recent_messages):

                    history += (
                        f"{msg.role}: "
                        f"{msg.content}\n"
                    )

                prompt = f"""

You are JARVIS AI.

Previous Conversation:

{history}

PDF Content:

{text[:8000]}

Current Question:

{question}

Use previous conversation
and PDF content when relevant.
"""

                PDFMessage.objects.create(
                    pdf=pdf,
                    role="user",
                    content=question
                )

                answer = get_ai_response(
                    prompt
                )

                PDFMessage.objects.create(
                    pdf=pdf,
                    role="assistant",
                    content=answer
                )

                pdf_messages = PDFMessage.objects.filter(
                    pdf=pdf
                ).order_by("created_at")

        except Exception as e:

            answer = f"""

⚠️ Unable to process this PDF.

Error:

{str(e)}

Possible reasons:

• PDF is corrupted
• PDF contains images only
• AI service unavailable

Please try again.
"""

    return render(
        request,
        "chat/pdf_detail.html",
        {
            "pdf": pdf,
            "text": text[:10000],
            "summary": summary,
            "question": question,
            "answer": answer,
            "pdf_messages": pdf_messages,
        }
    )

    
    
    

    
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)
@login_required
def upload_image(request):

    
    if request.method == "POST":

        form = ImageUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            image = form.save(
                commit=False
            )

            image.user = request.user

            image.save()

            xp, created = (
                UserXP.objects.get_or_create(
                    user=request.user,
                    defaults={
                        "points": 0
                    }
                )
            )

            xp.points += 10

            xp.save()

            return redirect(
                "image_library"
            )

    else:

        form = ImageUploadForm()

    images = ImageFile.objects.filter(
        user=request.user
    ).order_by(
        "-uploaded_at"
    )

    return render(
        request,
        "chat/upload_image.html",
        {
            "form": form,
            "images": images
        }
    )
    
    
@login_required
def image_detail(request, image_id):

    image = ImageFile.objects.get(
        id=image_id,
        user=request.user
    )

    image_messages = (
        ImageMessage.objects.filter(
            image=image
        ).order_by(
            "created_at"
        )
    )

    question = ""

    if request.method == "POST":

        try:

            model = genai.GenerativeModel(
                "gemini-2.5-flash"
            )

            uploaded_image = (
                PIL.Image.open(
                    image.image.path
                )
            )

            question = request.POST.get(
                "question",
                ""
            )

            history = ""

            recent_messages = (
                ImageMessage.objects.filter(
                    image=image
                )
                .order_by(
                    "-created_at"
                )[:10]
            )

            for msg in reversed(
                recent_messages
            ):

                history += (
                    f"{msg.role}: "
                    f"{msg.content}\n"
                )

            ImageMessage.objects.create(
                image=image,
                role="user",
                content=question
            )

            response = (
                model.generate_content(
                    [
                        f"""

You are JARVIS AI.

Previous Conversation:

{history}

User Question:

{question}

Use previous conversation
when relevant.
                        """,
                        uploaded_image
                    ]
                )
            )

            answer = response.text

            ImageMessage.objects.create(
                image=image,
                role="assistant",
                content=answer
            )

            image_messages = (
                ImageMessage.objects.filter(
                    image=image
                ).order_by(
                    "created_at"
                )
            )

        except Exception as e:

            ImageMessage.objects.create(
                image=image,
                role="assistant",
                content=f"""
⚠️ Error

{str(e)}
"""
            )

    return render(
        request,
        "chat/image_detail.html",
        {
            "image": image,
            "image_messages": image_messages,
        }
    )
    
    
@login_required
def memories(request):


    if request.method == "POST":

        form = MemoryForm(request.POST)

        if form.is_valid():

            memory = form.save(commit=False)

            memory.user = request.user

            memory.save()

            return redirect("memories")

    else:

        form = MemoryForm()

    memories = Memory.objects.filter(
        user=request.user
    ).order_by("-created_at")

    insight = None

    if memories.exists():

        memory_text = "\n".join(
            [
                memory.content
                for memory in memories
            ]
        )

        prompt = f"""


    You are JARVIS AI.

    Read the user's memories below.

    Create a short personal profile.

    Include:

    • Name (if known)
    • Goals
    • Interests
    • Skills
    • Important facts

    Keep it under 100 words.

    Memories:

    {memory_text}
    """


        try:

            insight = get_ai_response(
                prompt
            )

        except Exception:

            insight = (
                "Unable to generate "
                "memory insights right now."
            )

    return render(
        request,
        "chat/memories.html",
        {
            "form": form,
            "memories": memories,
            "insight": insight
        }
    )


    
    
@login_required
def delete_memory(request, memory_id):


    memory = Memory.objects.get(
        id=memory_id,
        user=request.user
    )

    memory.delete()

    return redirect("memories")


    
    
@login_required
def website_summarizer(request):

    summary = None

    if request.method == "POST":

        form = WebsiteForm(request.POST)

        if form.is_valid():

            try:

                url = form.cleaned_data["url"]

                existing = Website.objects.filter(
                    user=request.user,
                    url=url
                ).first()

                if existing:

                    return redirect(
                        "website_detail",
                        existing.id
                    )

                headers = {
                    "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }

                response = requests.get(
                    url,
                    headers=headers,
                    timeout=15
                )

                response.raise_for_status()

                soup = BeautifulSoup(
                    response.text,
                    "html.parser"
                )

                text = soup.get_text(
                    separator=" ",
                    strip=True
                )

                title = (
                    soup.title.string.strip()
                    if soup.title and soup.title.string
                    else url
                )

                website = Website.objects.create(
                    user=request.user,
                    url=url,
                    title=title,
                    content=text[:50000]
                )

                xp, created = UserXP.objects.get_or_create(
                    user=request.user,
                    defaults={
                        "points": 0
                    }
                )

                xp.points += 10
                xp.save()

                return redirect(
                    "website_detail",
                    website.id
                )

            except Exception as e:

                summary = f"""
⚠️ Website Error

{str(e)}
"""

    else:

        form = WebsiteForm()

    return render(
        request,
        "chat/website.html",
        {
            "form": form,
            "summary": summary
        }
    )    
    
def get_video_id(url):

    if "v=" in url:
        return url.split("v=")[1].split("&")[0]

    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]

    return None


def get_video_info(url):

    try:

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True
        }

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

            return {
                "title":
                info.get(
                    "title",
                    "Unknown Video"
                ),

                "channel":
                info.get(
                    "channel",
                    "Unknown Channel"
                ),

                "thumbnail":
                info.get(
                    "thumbnail",
                    ""
                )
            }

    except Exception:

        return {
            "title":
            "YouTube Video",

            "channel":
            "Unknown Channel",

            "thumbnail":
            ""
        }

def save_or_get_video(
    user,
    url,
    video_info,
    transcript_text
    ):


    video = YouTubeVideo.objects.filter(
        user=user,
        url=url
    ).first()

    if video:

        return video

    return YouTubeVideo.objects.create(
        user=user,
        title=video_info["title"],
        url=url,
        channel=video_info["channel"],
        thumbnail=video_info["thumbnail"],
        transcript=transcript_text
    )




@login_required
def youtube_summarizer(request):

    if request.method == "POST":

        form = YouTubeForm(request.POST)

        if form.is_valid():

            url = form.cleaned_data["url"]

            saved_video = (
                YouTubeVideo.objects.filter(
                    user=request.user,
                    url=url
                ).first()
            )

            if saved_video:

                return redirect(
                    "youtube_video_detail",
                    saved_video.id
                )

            video_info = get_video_info(
                url
            )

            video_id = get_video_id(
                url
            )

            try:

                ytt_api = (
                    YouTubeTranscriptApi()
                )

                transcript = (
                    ytt_api.fetch(
                        video_id
                    )
                )

                transcript_text = (
                    " ".join(
                        [
                            item.text
                            for item in transcript
                        ]
                    )
                )

                video = save_or_get_video(
                    request.user,
                    url,
                    video_info,
                    transcript_text
                )

                xp, created = UserXP.objects.get_or_create(
                    user=request.user,
                    defaults={
                        "points": 0
                    }
                )

                xp.points += 10
                xp.save()

                return redirect(
                    "youtube_video_detail",
                    video.id
                )

            except Exception:

                return render(
                    request,
                    "chat/youtube.html",
                    {
                        "form": form,
                        "summary": """

⚠️ Transcript unavailable.

Possible reasons:

• Captions disabled
• Auto captions unavailable
• Live stream
• Private video

Try another video.
"""
                    }
                )

    else:

        form = YouTubeForm()

    return render(
        request,
        "chat/youtube.html",
        {
            "form": form
        }
    )
    
    
        
@login_required
def youtube_history(request):

    query = request.GET.get(
        "q",
        ""
    )

    videos = (
        YouTubeVideo.objects
        .filter(
            user=request.user
        )
        .order_by("-created_at")
    )

    if query:

        videos = videos.filter(
            title__icontains=query
        )

    return render(
        request,
        "chat/youtube_history.html",
        {
            "videos": videos,
            "query": query,
            "total_videos": videos.count()
        }
    )





    
@login_required
def delete_chat(request, chat_id):

    chat = ChatSession.objects.get(
        id=chat_id,
        user=request.user
    )

    chat.delete()

    return redirect("/chat/")


@login_required
def rename_chat(request, chat_id):

    chat = get_object_or_404(
        ChatSession,
        id=chat_id,
        user=request.user
    )

    if request.method == "POST":

        new_title = request.POST.get(
            "title"
        )

        if new_title:

            chat.title = new_title

            chat.save()

        return redirect("/chat/")

    return render(
        request,
        "rename_chat.html",
        {
            "chat": chat
        }
    )
    
    
@login_required
def profile(request):

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

    video_count = YouTubeVideo.objects.filter(
        user=request.user
    ).count()

    website_count = Website.objects.filter(
        user=request.user
    ).count()

    xp, created = UserXP.objects.get_or_create(
        user=request.user
    )

    context = {

        "chat_count": chat_count,
        "pdf_count": pdf_count,
        "image_count": image_count,
        "memory_count": memory_count,
        "video_count": video_count,
        "website_count": website_count,
        "xp_points": xp.points,
    }

    return render(
        request,
        "profile.html",
        context
    )    
    
    
@login_required
def youtube_video_detail(
    request,
    video_id
):

    video = get_object_or_404(
        YouTubeVideo,
        id=video_id,
        user=request.user
    )
    xp, created = UserXP.objects.get_or_create(
    user=request.user
)

    answer = None
    question = ""

    video_messages = VideoMessage.objects.filter(
        video=video
    ).order_by("created_at")

    if request.method == "POST":

        question = request.POST.get(
            "question",
            ""
        )

        history = ""

        recent_messages = VideoMessage.objects.filter(
            video=video
        ).order_by("-created_at")[:10]

        for msg in reversed(
            recent_messages
        ):

            history += (
                f"{msg.role}: "
                f"{msg.content}\n"
            )

        prompt = f"""
You are JARVIS AI.

Previous Conversation:

{history}

Video Title:
{video.title}

Channel:
{video.channel}

Transcript:

{video.transcript[:8000]}

Current Question:

{question}

Use previous conversation
and video content when relevant.
"""

        VideoMessage.objects.create(
            video=video,
            role="user",
            content=question
        )

        answer = get_ai_response(
            prompt
        )
        
        if (
        "correct" in answer.lower()
        or "well done" in answer.lower()
        or "good job" in answer.lower()
    ):

            xp.points += 10
            xp.save()

        VideoMessage.objects.create(
            video=video,
            role="assistant",
            content=answer
        )

        video_messages = VideoMessage.objects.filter(
            video=video
        ).order_by("created_at")

    return render(
        request,
        "chat/youtube_video_detail.html",
        {
            "video": video,
            "question": question,
            "answer": answer,
            "video_messages": video_messages
        }
    )
    
        
@login_required
def pdf_library(request):

    query = request.GET.get(
        "q",
        ""
    )

    pdfs = (
        PDFFile.objects
        .filter(
            user=request.user
        )
        .order_by("-uploaded_at")
    )

    if query:

        pdfs = pdfs.filter(
            file__icontains=query
        )

    return render(
        request,
        "chat/pdf_library.html",
        {
            "pdfs": pdfs,
            "query": query,
            "total_pdfs": pdfs.count()
        }
    )    
    
    
    
    
    
    
    
    
    
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

@login_required
def image_library(request):

    query = request.GET.get("q", "")

    images = ImageFile.objects.filter(
        user=request.user
    )

    if query:

        images = images.filter(
            image__icontains=query
        )

    images = images.order_by(
        "-uploaded_at"
    )

    return render(
        request,
        "chat/image_library.html",
        {
            "images": images,
            "query": query,
            "total_images": images.count()
        }
    )


@login_required
def delete_image(
    request,
    image_id
):

    image = get_object_or_404(
        ImageFile,
        id=image_id,
        user=request.user
    )

    if image.image:
        image.image.delete(
            save=False
        )

    image.delete()

    return redirect(
        "image_library"
    )    
    
    
    
@login_required
def website_library(request):

    query = request.GET.get(
        "q",
        ""
    )

    websites = Website.objects.filter(
        user=request.user
    )

    if query:

        websites = websites.filter(
            title__icontains=query
        )

    websites = websites.order_by(
        "-created_at"
    )

    return render(
        request,
        "chat/website_library.html",
        {
            "websites": websites,
            "query": query,
            "total_websites":
            websites.count()
        }
    )
    
    
@login_required
def delete_pdf(
    request,
    pdf_id
):

    pdf = get_object_or_404(
        PDFFile,
        id=pdf_id,
        user=request.user
    )

    if request.method == "POST":

        pdf.delete()

    return redirect(
        "pdf_library"
    )


@login_required
def delete_video(
    request,
    video_id
):

    video = get_object_or_404(
        YouTubeVideo,
        id=video_id,
        user=request.user
    )

    if request.method == "POST":

        video.delete()

    return redirect(
        "youtube_history"
    )




@login_required
def delete_website(
    request,
    website_id
):

    website = get_object_or_404(
        Website,
        id=website_id,
        user=request.user
    )

    if request.method == "POST":

        website.delete()

    return redirect(
        "website_library"
    )


@login_required
def website_detail(
    request,
    website_id
):

    website = Website.objects.get(
        id=website_id,
        user=request.user
    )

    website_messages = (
        WebsiteMessage.objects.filter(
            website=website
        )
        .order_by("created_at")
    )

    if request.method == "POST":

        question = request.POST.get(
            "question",
            ""
        )

        WebsiteMessage.objects.create(
            website=website,
            role="user",
            content=question
        )

        history = ""

        recent_messages = (
            WebsiteMessage.objects
            .filter(
                website=website
            )
            .order_by("-created_at")[:10]
        )

        for msg in reversed(
            recent_messages
        ):

            history += (
                f"{msg.role}: "
                f"{msg.content}\n"
            )

        prompt = f"""

You are JARVIS AI.

Website Title:

{website.title}

Website Content:

{website.content[:8000]}

Previous Conversation:

{history}

Current Question:

{question}

Use the website content
and previous conversation
when relevant.
"""

        answer = get_ai_response(
            prompt
        )

        WebsiteMessage.objects.create(
            website=website,
            role="assistant",
            content=answer
        )

        return redirect(
            "website_detail",
            website.id
        )

    return render(
        request,
        "chat/website_detail.html",
        {
            "website": website,
            "website_messages":
            website_messages
        }
    )
    
@login_required
def toggle_favorite(request, chat_id):

    chat = get_object_or_404(
        ChatSession,
        id=chat_id,
        user=request.user
    )

    chat.is_favorite = (
        not chat.is_favorite
    )

    chat.save()

    return redirect("chat_home")


@login_required
def toggle_pin(request, chat_id):

    chat = get_object_or_404(
        ChatSession,
        id=chat_id,
        user=request.user
    )

    chat.is_pinned = (
        not chat.is_pinned
    )

    chat.save()

    return redirect("chat_home")




@login_required
def export_chat_pdf(
    request,
    chat_id
):

    chat = get_object_or_404(
        ChatSession,
        id=chat_id,
        user=request.user
    )

    messages = Message.objects.filter(
        chat=chat
    ).order_by(
        "created_at"
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="{chat.title}.pdf"'
    )

    pdf = SimpleDocTemplate(
        response
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            f"JARVIS AI Chat Export",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            chat.title,
            styles["Heading2"]
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    for msg in messages:

        role = (
            "👤 User"
            if msg.role == "user"
            else "🤖 JARVIS"
        )

        text = (
            f"<b>{role}</b><br/>"
            f"{msg.content}"
        )

        elements.append(
            Paragraph(
                text,
                styles["BodyText"]
            )
        )

        elements.append(
            Spacer(1, 10)
        )

    pdf.build(
        elements
    )

    return response