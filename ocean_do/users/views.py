from accounts.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from ocean_do.aws import upload_avatar_to_s3

from .forms import UserUpdateForm


def profile_view(request):
    return render(request, "users/profile.html")


def edit_profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            user_email = request.user.email
            user = User.objects.get(email=user_email)

            avatar_file = form.cleaned_data.get('file')
            username = form.cleaned_data.get('username')

            if avatar_file:
                avatar_url = upload_avatar_to_s3(user_email, avatar_file)
                if avatar_url:
                    user.photo_url = avatar_url

            if username:
                user.username = username

            user.save()

            messages.success(request, 'Ваш профіль було успішно оновлено.')
            return redirect('users:edit-profile')
        else:
            messages.error(request, 'Форма недійсна. Будь ласка, перевірте дані.')
    else:
        form = UserUpdateForm()
    return render(request, 'users/edit-profile.html', {'form': form})
