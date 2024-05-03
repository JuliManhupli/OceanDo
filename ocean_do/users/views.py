from accounts.models import User
from tasks.models import Task
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from ocean_do.aws import upload_avatar_to_s3, delete_avatar_from_s3

from .forms import UserUpdateForm
from tasks.views import get_tasks, get_completed_tasks


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


def personal_stats_view(request):
    assigned_tasks, created_tasks, solo_assignee_tasks = get_tasks(request)
    completed_tasks, _, created_complete = get_completed_tasks(request)
    all_assigned_incomplete = set(list(assigned_tasks) + list(solo_assignee_tasks))
    deadlineTasks = set(list(assigned_tasks) + list(solo_assignee_tasks) + list(completed_tasks)
                        + list(created_tasks) + list(created_complete))
    return render(request, "users/personal-stats.html",
                  {'all_assigned_incomplete': all_assigned_incomplete, 'all_assigned_complete': len(completed_tasks),
                   'all_created_incomplete': created_tasks, 'all_created_complete': len(created_complete),
                   'deadlineTasks': deadlineTasks})


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
