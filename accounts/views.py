from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from chat.models import UserXP


def register(request):

    error = None

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():

            error = "Username already exists"

        else:

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            UserXP.objects.create(
                user=user,
                points=0
            )

            return redirect(
                "/accounts/login/"
            )

    return render(
        request,
        "accounts/register.html",
        {
            "error": error
        }
    )


def login_view(request):

    error = None

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            UserXP.objects.get_or_create(
                user=user,
                defaults={
                    "points": 0
                }
            )

            login(request, user)

            return redirect(
                "/dashboard/"
            )

        else:

            error = (
                "Invalid username "
                "or password"
            )

    return render(
        request,
        "accounts/login.html",
        {
            "error": error
        }
    )


def logout_view(request):

    logout(request)

    return redirect("/")