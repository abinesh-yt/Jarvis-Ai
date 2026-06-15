from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import (
    ChatSession,
    Message,
    PDFFile,
    ImageFile,
    Memory,
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

        if content:

            Message.objects.create(
                chat=chat,
                role="user",
                content=content
            )

            if chat.title == "New Chat":

                chat.title = content[:40]
                chat.save()

            # Load user memories
            memories = Memory.objects.filter(
                user=request.user
            )

            memory_text = "\n".join(
                [memory.content for memory in memories]
            )

            # Create memory-aware prompt
            prompt = f"""
            User Memories:

            {memory_text}

            User Message:

            {content}

            Use the memories when relevant.
            """

            ai_response = get_ai_response(prompt)

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

    reader = PdfReader(pdf.file.path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text

    summary = None
    question = ""
    answer = None

    if request.method == "POST":

        if "summarize" in request.POST:

            prompt = f"""
            Summarize this PDF in simple language:

            {text[:8000]}
            """

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            summary = (
                completion
                .choices[0]
                .message
                .content
            )

        elif "ask" in request.POST:

            question = request.POST.get(
                "question",
                ""
            )

            prompt = f"""
            Answer the question only
            using the PDF content.

            PDF:

            {text[:8000]}

            Question:

            {question}
            """

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            answer = (
                completion
                .choices[0]
                .message
                .content
            )

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

    return render(
        request,
        "chat/memories.html",
        {
            "form": form,
            "memories": memories
        }
    )
    
    
@login_required
def website_summarizer(request):

    summary = None

    if request.method == "POST":

        form = WebsiteForm(request.POST)

        if form.is_valid():

            url = form.cleaned_data["url"]

            response = requests.get(url)

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            text = soup.get_text()

            prompt = f"""
            Summarize this website:

            {text[:8000]}
            """

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            summary = (
                completion
                .choices[0]
                .message
                .content
            )

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