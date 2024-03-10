from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import RegisterForm, LoginForm


def login_view(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponse(f"Ви вже авторизовані як {user.username}.")

    print("1")
    if request.method == 'POST':
        print("2")
        form = LoginForm(data=request.POST)
        print("3")
        if form.is_valid():
            print("4")
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            print("e")
            if user is not None:
                login(request, user)
                messages.success(request, f"Вітаємо {user.username}!")
                return redirect('main')
        else:
            print(form.errors)
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return HttpResponse(f"Ви вже авторизовані як {user.username}.")

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            messages.success(request, f"Вітаємо {username}! Ваш акаунт успішно створено.")
            return redirect('main')
    else:
        form = RegisterForm()

    context = {'form': form}
    return render(request, "accounts/register.html", context)
