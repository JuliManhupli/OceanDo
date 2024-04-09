from accounts.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from ocean_do.aws import upload_avatar_to_s3, delete_avatar_from_s3

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
                    user.photo = avatar_url

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


@require_http_methods(["DELETE"])
def delete_avatar_view(request):
    if request.user.is_authenticated:
        user = request.user
        if user.photo:
            delete_avatar_from_s3(user.photo.name)  # Видалення файлу з AWS S3
            user.photo.delete()  # Видалення посилання на файл з бази даних
            return JsonResponse({'message': 'Аватар було успішно видалено.'}, status=204)
        else:
            return JsonResponse({'error': 'Аватар відсутній.'}, status=404)
    else:
        return JsonResponse({'error': 'Необхідна аутентифікація.'}, status=401)