from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from ocean_do.aws import upload_avatar_to_s3, delete_avatar_from_s3
from tasks.views import get_tasks, get_completed_tasks

from .forms import UserUpdateForm, GroupForm
from accounts.models import Group, User


@login_required
def profile_view(request):
    return render(request, "users/profile.html")


def group_view(request):
    user = request.user
    print(user)
    groups = Group.objects.filter(owner=user)
    print(groups)
    return render(request, "users/group.html", {'groups': groups})


def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            print(form)
            group = form.save(commit=False)
            group.owner = request.user
            group.save()

            members = request.POST.getlist('assignees')[0].split(',')
            print(members)
            for members_email in members:
                member = User.objects.get(email=members_email)
                group.members.add(member)

            return redirect('users:groups')
    else:
        form = GroupForm()
    return render(request, "users/create-group.html", {'form': form})


def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.members.all()

    print(members)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)

        if form.is_valid():
            group.members.clear()
            group = form.save(commit=False)
            group.save()

            members = request.POST.getlist('assignees')[0].split(',')
            print(members)
            for members_email in members:
                member = User.objects.get(email=members_email)
                group.members.add(member)

            return redirect('users:groups')
    else:
        form = GroupForm(instance=group)
    return render(request, "users/edit-group.html",
                  {'form': form, 'group': group})


def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if group.owner == request.user:
        group.delete()
        return JsonResponse({'message': 'Група успішно видалена'}, status=204)
    else:
        return JsonResponse({'error': 'Ви не маєте права видаляти цю групу'}, status=403)


def get_all_groups(request):
    user = request.user
    print(user)
    groups = Group.objects.filter(owner=user)
    print(groups)
    # users_data = list(groups.members.values('email', 'username'))
    users_data = list(groups.values('id', 'name', 'members__email', 'members__username'))
    # print(users_data)
    return JsonResponse(users_data, safe=False)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            user_email = request.user.email
            user = User.objects.get(email=user_email)

            avatar_file = form.cleaned_data.get('file')
            username = form.cleaned_data.get('username')
            role = form.cleaned_data.get('role')

            if avatar_file:
                avatar_url = upload_avatar_to_s3(user_email, avatar_file)
                if avatar_url:
                    user.photo = avatar_url

            if username:
                user.username = username

            if role:
                user.role = role

            user.save()

            messages.success(request, 'Ваш профіль було успішно оновлено.')
            return redirect('users:edit-profile')
        else:
            messages.error(request, 'Форма недійсна. Будь ласка, перевірте дані.')
    else:
        user = request.user
        initial_data = {
            'username': user.username,
            'role': user.role,
        }
        form = UserUpdateForm(initial=initial_data)

    return render(request, 'users/edit-profile.html', {'form': form})


def personal_stats_view(request):
    assigned_tasks, created_tasks, solo_assignee_tasks = get_tasks(request)
    completed_tasks, _, created_complete, _ = get_completed_tasks(request)
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
