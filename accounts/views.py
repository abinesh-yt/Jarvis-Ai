from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from chat.models import UserXP

from datetime import date, timedelta


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
                points=0,
                streak=0,
                best_streak=0
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

            xp, created = UserXP.objects.get_or_create(
                user=user,
                defaults={
                    "points": 0,
                    "streak": 0,
                    "best_streak": 0
                }
            )

            today = date.today()

            if xp.last_login_date:

                if xp.last_login_date == today:

                    pass

                elif xp.last_login_date == (
                    today - timedelta(days=1)
                ):

                    xp.streak += 1
                    xp.points += 10

                else:

                    xp.streak = 1
                    xp.points += 10

            else:

                xp.streak = 1
                xp.points += 10

            if xp.streak > xp.best_streak:

                xp.best_streak = xp.streak

            xp.last_login_date = today

            xp.save()

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