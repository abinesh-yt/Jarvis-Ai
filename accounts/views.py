from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

def register(request):

    error = None

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            error = "Username already exists"

        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            return redirect('/accounts/login/')

    return render(
        request,
        'accounts/register.html',
        {'error': error}
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
            login(request, user)
            return redirect('/dashboard/')

        else:
            error = "Invalid username or password"

    return render(
        request,
        'accounts/login.html',
        {'error': error}
    )
    
def logout_view(request):
    logout(request)
    return redirect('/')