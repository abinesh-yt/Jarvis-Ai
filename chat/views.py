from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import (
    ChatSession,
    Message,
    PDFFile,
    ImageFile,
    Memory,
    YouTubeVideo
)
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

        if not content:
            return redirect(f"/chat/{chat.id}/")

        # Remember
        if content.lower().startswith("remember"):

            Memory.objects.create(
                user=request.user,
                content=content
            )

            Message.objects.create(
                chat=chat,
                role="assistant",
                content="🧠 Memory saved successfully!"
            )

            return redirect(f"/chat/{chat.id}/")

        # Forget
        elif content.lower().startswith("forget"):

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
                content=f"🗑️ Deleted {count} memory(s)."
            )

            return redirect(f"/chat/{chat.id}/")

        # Show Memories
        elif content.lower() == "show memories":

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
                content=f"🧠 Your Memories:\n\n{memory_list}"
            )

            return redirect(f"/chat/{chat.id}/")

        # Save User Message
        Message.objects.create(
            chat=chat,
            role="user",
            content=content
        )

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

        # Conversation History
        history = Message.objects.filter(
            chat=chat
        ).order_by("created_at")

        history_text = ""

        for msg in history:

            history_text += (
                f"{msg.role}: "
                f"{msg.content}\n"
            )

        # AI Prompt
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
            content=ai_response
        )

        return redirect(f"/chat/{chat.id}/")

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

            pdf = form.save(commit=False)

            pdf.user = request.user

            pdf.save()

            return redirect("upload_pdf")

    else:

        form = PDFUploadForm()

    pdfs = PDFFile.objects.filter(
        user=request.user
    ).order_by("-uploaded_at")

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

                prompt = f"""


    You are JARVIS AI.

    Answer the question using only
    the PDF content.

    PDF Content:

    {text[:8000]}

    Question:

    {question}
    """


                answer = get_ai_response(
                    prompt
                )

        except Exception:

            answer = """


    ⚠️ Unable to process this PDF.

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

            image = form.save(commit=False)

            image.user = request.user

            image.save()

            return redirect("upload_image")

    else:

        form = ImageUploadForm()

    images = ImageFile.objects.filter(
        user=request.user
    ).order_by("-uploaded_at")

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

    analysis = None
    question = ""
    answer = None

    if request.method == "POST":

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        uploaded_image = PIL.Image.open(
            image.image.path
        )

        if "analyze" in request.POST:

            response = model.generate_content([
                "Describe this image in detail.",
                uploaded_image
            ])

            analysis = response.text

        elif "ask" in request.POST:

            question = request.POST.get(
                "question",
                ""
            )

            response = model.generate_content([
                f"""
                Answer the user's question
                about this image.

                Question:
                {question}
                """,
                uploaded_image
            ])

            answer = response.text

    return render(
    request,
    "chat/image_detail.html",
    {
        "image": image,
        "analysis": analysis,
        "question": question,
        "answer": answer,
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

                response = requests.get(
                    url,
                    timeout=10
                )

                soup = BeautifulSoup(
                    response.text,
                    "html.parser"
                )

                text = soup.get_text(
                    separator=" ",
                    strip=True
                )

                prompt = f"""


    You are JARVIS AI.

    Analyze and summarize this website.

    Website Content:

    {text[:8000]}

    Provide:

    1. Main purpose
    2. Key information
    3. Important takeaways
    4. Short summary
    """

    
                summary = get_ai_response(
                    prompt
                )

            except Exception:

                summary = """
    

    ⚠️ Unable to access this website.

    Possible reasons:

    • Invalid URL
    • Website blocked requests
    • Website unavailable

    Try another website.
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


    summary = None
    video_info = None

    if request.method == "POST":

        form = YouTubeForm(request.POST)

        if form.is_valid():

            url = form.cleaned_data["url"]

            question = request.POST.get(
                "question"
            )

            saved_video = (
                YouTubeVideo.objects.filter(
                    user=request.user,
                    url=url
                ).first()
            )

            if saved_video:

                transcript_text = (
                    saved_video.transcript
                )

                video_info = {
                    "title":
                    saved_video.title,

                    "channel":
                    saved_video.channel,

                    "thumbnail":
                    saved_video.thumbnail
                }

            else:

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

                    save_or_get_video(
                        request.user,
                        url,
                        video_info,
                        transcript_text
                    )

                except Exception:

                    summary = """


    ⚠️ Transcript unavailable.

    Possible reasons:

    • Captions disabled
    • Auto captions unavailable
    • Live stream
    • Private video

    Try another video.
    """


                    return render(
                        request,
                        "chat/youtube.html",
                        {
                            "form": form,
                            "summary": summary,
                            "video_info": video_info
                        }
                    )

            if not question:

                question = (
                    "Summarize this video"
                )

            prompt = f"""


    You are JARVIS AI.

    Video Title:
    {video_info['title']}

    Channel:
    {video_info['channel']}

    Transcript:

    {transcript_text[:8000]}

    User Question:

    {question}

    Answer only using
    the video content.
    """


            summary = get_ai_response(
                prompt
            )

    else:

        form = YouTubeForm()

    return render(
        request,
        "chat/youtube.html",
        {
            "form": form,
            "summary": summary,
            "video_info": video_info
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

    context = {

        "chat_count": chat_count,
        "pdf_count": pdf_count,
        "image_count": image_count,
        "memory_count": memory_count,

    }

    return render(
        request,
        "profile.html",
        context
    )