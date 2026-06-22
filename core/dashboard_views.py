from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from chat.models import (
    ChatSession,
    Message,
    PDFFile,
    ImageFile,
    Memory,
    YouTubeVideo,
    Website,
    UserXP
)


@login_required
def dashboard(request):

    chat_count = ChatSession.objects.filter(
        user=request.user
    ).count()

    total_messages = Message.objects.filter(
        chat__user=request.user
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
        user=request.user,
        defaults={
            "points": 0
        }
    )

    xp_points = xp.points

    if xp_points < 100:

        level = 1
        next_level_xp = 100
        current_level_start = 0

    elif xp_points < 250:

        level = 2
        next_level_xp = 250
        current_level_start = 100

    elif xp_points < 500:

        level = 3
        next_level_xp = 500
        current_level_start = 250

    elif xp_points < 1000:

        level = 4
        next_level_xp = 1000
        current_level_start = 500

    else:

        level = 5
        next_level_xp = xp_points
        current_level_start = 1000

    if level < 5:

        progress_percent = int(
            (
                (xp_points - current_level_start)
                /
                (
                    next_level_xp
                    - current_level_start
                )
            ) * 100
        )

    else:

        progress_percent = 100

    tool_stats = {

        "PDF Assistant": pdf_count,
        "Vision AI": image_count,
        "Website AI": website_count,
        "YouTube AI": video_count,
        "Memory AI": memory_count

    }

    most_used_tool = max(
        tool_stats,
        key=tool_stats.get
    )

    recent_chats = ChatSession.objects.filter(
        user=request.user
    ).order_by("-created_at")[:5]

    recent_pdfs = PDFFile.objects.filter(
        user=request.user
    ).order_by("-uploaded_at")[:5]

    recent_images = ImageFile.objects.filter(
        user=request.user
    ).order_by("-uploaded_at")[:5]

    recent_videos = YouTubeVideo.objects.filter(
        user=request.user
    ).order_by("-created_at")[:5]

    recent_websites = Website.objects.filter(
        user=request.user
    ).order_by("-created_at")[:5]

    context = {

        "chat_count": chat_count,
        "total_messages": total_messages,

        "pdf_count": pdf_count,
        "image_count": image_count,
        "memory_count": memory_count,
        "video_count": video_count,
        "website_count": website_count,

        "xp_points": xp_points,
        "level": level,
        "next_level_xp": next_level_xp,
        "progress_percent": progress_percent,

        "most_used_tool": most_used_tool,

        "recent_chats": recent_chats,
        "recent_pdfs": recent_pdfs,
        "recent_images": recent_images,
        "recent_videos": recent_videos,
        "recent_websites": recent_websites,
    }

    return render(
        request,
        "dashboard.html",
        context
    )