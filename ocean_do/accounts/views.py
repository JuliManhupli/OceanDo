from datetime import datetime

import pyotp
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import User
from .forms import RegisterForm, LoginForm, ChangePasswordForm
from .utils import send_otp


def login_view(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponse(f"Ви вже авторизовані як {user.username}.")

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_verified:
                    login(request, user)
                    messages.success(request, f"Вітаємо {user.username}!")
                    return redirect('main')
                else:
                    request.session['email'] = email
                    send_otp(request)
                    messages.error(request, "Підтвердіть свою пошту.")
                    return redirect('accounts:code-verification')
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
            user = form.save()
            email = form.cleaned_data.get('email')
            request.session['email'] = email
            send_otp(request)
            return redirect('accounts:code-verification')
    else:
        form = RegisterForm()

    context = {'form': form}
    return render(request, "accounts/register.html", context)


def code_verification_view(request):
    if request.method == 'POST':
        otp_code = ''.join(request.POST.get(f'otp_digit_{i + 1}') for i in range(6))
        print(otp_code)
        email = request.session.get('email')
        print(email)
        otp_secret_key = request.session.get('otp_secret_key')
        otp_valid_date = request.session.get('otp_valid_date')
        type = request.session.get('type')
        print(otp_secret_key, otp_valid_date, type)

        if otp_secret_key and otp_valid_date is not None:
            valid_date = datetime.fromisoformat(otp_valid_date)
            if datetime.now() < valid_date:
                totp = pyotp.TOTP(otp_secret_key, interval=300)

                print(otp_code, totp.verify(otp_code))
                if totp.verify(otp_code):
                    print("222")
                    try:
                        user = User.objects.get(email=email)
                        user.is_verified = True
                        user.save()

                        del request.session['otp_secret_key']
                        del request.session['otp_valid_date']
                        if type == 'new-password':
                            return redirect('accounts:new-password')
                        else:
                            messages.success(request, f"Вітаємо {user.username}! Ви підтвердили свою пошту.")
                            return redirect('accounts:login')
                    except User.DoesNotExist:
                        messages.error(request, "Користувача з такою поштою не знайдено.")
                        return redirect('accounts:register')
                else:
                    print("Ваш код неправильний.")
                    messages.error(request, "Ваш код неправильний.")
                    return redirect('accounts:code-verification')

            else:
                print("Ваш код більше не діє.")
                messages.error(request, "Ваш код більше не діє.")
                return redirect('accounts:code-verification')

    return render(request, "accounts/code-verification.html")


def resend_otp(request):
    if request.method == 'POST':
        email = request.session.get('email')
        if email:
            send_otp(request)  # Відправити новий OTP код
            messages.success(request, "Новий код було відправлено.")
        else:
            messages.error(request, "Користувача з такою поштою не знайдено.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def email_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print(email)
        try:
            user = User.objects.get(email=email)
            request.session['email'] = email
            request.session['type'] = "new-password"
            send_otp(request)
            return redirect('accounts:code-verification')
        except User.DoesNotExist:
            messages.error(request, 'Користувача з такою поштою не знайдено.')
            return redirect('accounts:email')
    return render(request, "accounts/email.html")


def change_password_view(request):
    email = request.session.get('email')
    print(email)
    try:
        user = User.objects.get(email=email)
        if request.method == 'POST':
            form = ChangePasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                confirm_new_password = form.cleaned_data['confirm_new_password']
                if new_password == confirm_new_password:
                    user.password = make_password(new_password)
                    user.save()
                    messages.success(request, 'Ваш пароль успішно змінено.')
                    return redirect('accounts:login')
                else:
                    form.add_error('confirm_new_password', 'Паролі не співпадають.')
        else:
            form = ChangePasswordForm()
    except User.DoesNotExist:
        messages.error(request, 'Користувача з такою поштою не знайдено.')
        return redirect('accounts:email')
    return render(request, 'accounts/new-password.html', {'form': form})
