from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatSession
from .models import ChatSession, Message
from .ai import get_ai_response
from .models import PDFFile
from .forms import PDFUploadForm
from pypdf import PdfReader
from groq import Groq
import os



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