from django.shortcuts import render


def login(request):
    return render(request, "accounts/auth/login.html")

def register(request):
    return render(request, "accounts/auth/register.html")

def password_reset(request):
    return render(request, "accounts/auth/password_reset.html")