from accounts.models import User
from tasks.models import Task
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Count
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


def personal_stats_view(request):
    user = request.user
    assigned_tasks = Task.objects.filter(assignees__user=user, assignees__is_completed=False)
    created_tasks = Task.objects.filter(creator=user, is_completed=False)
    solo_assignee_tasks = created_tasks.annotate(assignees_count=Count('assignees')).filter(assignees_count=1).filter(
        assignees__user=user).filter(assignees__is_completed=False)

    created_tasks = created_tasks.exclude(id__in=solo_assignee_tasks)
    assigned_tasks = assigned_tasks.exclude(id__in=solo_assignee_tasks)
    combined_query = set(list(assigned_tasks) + list(solo_assignee_tasks))
    tasks_with_type = [(task, 'solo') if task in solo_assignee_tasks else (task, 'assigned') for task in combined_query]
    count_by_type = {'solo': 0, 'assigned': 0, 'created': 0}
    for task, task_type in tasks_with_type:
        if task_type in count_by_type:
            count_by_type[task_type] += 1
        else:
            count_by_type[task_type] = 1

    return render(request, "users/personal-stats.html",
                  {'tasks_with_type': tasks_with_type, 'created_tasks': created_tasks})


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