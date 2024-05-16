import json
from datetime import datetime

from accounts.models import User, Notification
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from ocean_do.aws import upload_file_to_s3, upload_assignment_file_to_s3, delete_file_from_s3

from .form import TaskForm, CommentForm, TaskEditForm
from .models import Tag, Task, TaskAssignment, File, Folder, TaskChat, ChatComment
from .utils import send_task


def send_notification(message, assignee):
    notification = Notification.objects.create(
        message=message,
    )
    notification.users.set([assignee])
    notification.save()


def get_folders(request):
    tasks = Task.objects.filter(creator=request.user, is_completed=False)
    task_assignments = TaskAssignment.objects.filter(user=request.user, is_completed=False)
    task_folders = Folder.objects.filter(folders_tasks__in=tasks)
    task_assignments_folders = Folder.objects.filter(folders_assignments__in=task_assignments)

    all_folders = task_folders | task_assignments_folders
    return all_folders.order_by('name').distinct()


def user_folders(request):
    try:
        all_folders = get_folders(request)
        folders_data = [{'id': folder.id, 'name': folder.name} for folder in all_folders]
        return JsonResponse(folders_data, safe=False)
    except Task.DoesNotExist:
        return redirect('tasks:all_tasks')


def get_tasks(request):
    user = request.user
    assigned_query = Task.objects.filter(assignees__user=user, assignees__is_completed=False)
    created_query = Task.objects.filter(creator=user, is_completed=False)
    solo_assignee_query = created_query.annotate(assignees_count=Count('assignees')).filter(assignees_count=1).filter(
        assignees__user=user).filter(assignees__is_completed=False)

    created_query = created_query.exclude(id__in=solo_assignee_query)
    assigned_query = assigned_query.exclude(id__in=solo_assignee_query)

    if request.method == "POST":
        search_tag = request.POST.get('tag-filter')
        search_folder = request.POST.get('folder-filter')
        if search_tag:
            created_query = created_query.filter(tags__name=search_tag)
            assigned_query = assigned_query.filter(assignees__user=user, assignees__tags__name=search_tag)
            solo_assignee_query = solo_assignee_query.filter(tags__name=search_tag)

        if search_folder:
            created_query = created_query.filter(folders__name=search_folder)
            assigned_query = assigned_query.filter(assignees__user=user, assignees__folders__name=search_folder)
            solo_assignee_query = solo_assignee_query.filter(folders__name=search_folder)

    return assigned_query, created_query, solo_assignee_query


def get_tags(request):
    user = request.user
    user_tasks = Task.objects.filter(creator=user)
    user_task_assignments = TaskAssignment.objects.filter(user=user)
    task_tags = Tag.objects.filter(tags_tasks__in=user_tasks)
    task_assignment_tags = Tag.objects.filter(tags_assignments__in=user_task_assignments)
    all_tags = task_tags | task_assignment_tags
    return all_tags.order_by('name').distinct()


def get_sorting(request, created_tasks, combined_query):
    if request.method == "POST":
        sort_order = request.POST.get('sorting')
        sort_key = None
        if sort_order == 'title':
            sort_key = lambda x: x.title
        elif sort_order == 'deadline':
            sort_key = lambda x: x.deadline

        if sort_key:
            created_tasks = sorted(created_tasks, key=sort_key)
            combined_query = sorted(combined_query, key=sort_key)

    return created_tasks, combined_query


@login_required
def all_tasks(request):
    assigned_tasks, created_tasks, solo_assignee_tasks = get_tasks(request)
    combined_query = set(list(assigned_tasks) + list(solo_assignee_tasks))
    created_tasks_sorted, combined_query_sorted = get_sorting(request, created_tasks, combined_query)

    tasks_with_type = [(task, 'solo') if task in solo_assignee_tasks else (task, 'assigned') for task in
                       combined_query_sorted]
    current_time = timezone.now()
    all_user_folders = get_folders(request)
    all_user_tags = get_tags(request)
    return render(request, "tasks/all-tasks.html",
                  {'tasks_with_type': tasks_with_type, 'created_tasks': created_tasks_sorted,
                   'current_time': current_time,
                   'all_user_folders': all_user_folders, 'all_user_tags': all_user_tags})


def get_completed_tasks(request):
    user = request.user
    assigned_tasks = Task.objects.filter(assignees__user=user, assignees__is_completed=True)
    created_tasks = Task.objects.filter(creator=user, is_completed=True)
    solo_assignee_tasks = created_tasks.annotate(assignees_count=Count('assignees')).filter(assignees_count=1).filter(
        assignees__user=user)
    created_tasks = created_tasks.exclude(id__in=solo_assignee_tasks)
    assigned_tasks = assigned_tasks.exclude(id__in=solo_assignee_tasks)

    if request.method == "POST":
        search_tag = request.POST.get('tag-filter')
        search_folder = request.POST.get('folder-filter')

        if search_tag:
            created_tasks = created_tasks.filter(tags__name=search_tag)
            assigned_tasks = assigned_tasks.filter(assignees__user=user, assignees__tags__name=search_tag)
            solo_assignee_tasks = solo_assignee_tasks.filter(tags__name=search_tag)

        if search_folder:
            created_tasks = created_tasks.filter(folders__name=search_folder)
            assigned_tasks = assigned_tasks.filter(assignees__user=user, assignees__folders__name=search_folder)
            solo_assignee_tasks = solo_assignee_tasks.filter(folders__name=search_folder)

    combined_query = set(list(assigned_tasks) + list(solo_assignee_tasks))

    return combined_query, solo_assignee_tasks, created_tasks, assigned_tasks


@login_required
def completed_tasks(request):
    combined_query, solo_assignee_tasks, created_tasks, _ = get_completed_tasks(request)
    created_tasks_sorted, combined_query_sorted = get_sorting(request, created_tasks, combined_query)
    tasks_with_type = [(task, 'solo') if task in solo_assignee_tasks else (task, 'assigned') for task in
                       combined_query_sorted]
    all_user_folders = get_folders(request)
    all_user_tags = get_tags(request)
    return render(request, "tasks/completed-tasks.html",
                  {'tasks_with_type': tasks_with_type, 'created_tasks': created_tasks_sorted,
                   'all_user_folders': all_user_folders, 'all_user_tags': all_user_tags})


@login_required
def folder_tasks(request, folder_id):
    user = request.user
    folder = Folder.objects.get(id=folder_id)

    task_assignments = TaskAssignment.objects.filter(folders=folder, user=user, is_completed=False)

    assigned_tasks = Task.objects.filter(assignees__in=task_assignments)
    created_tasks = Task.objects.filter(creator=user, folders=folder, is_completed=False)
    solo_assignee_tasks = created_tasks.annotate(assignees_count=Count('assignees')).filter(assignees_count=1).filter(
        assignees__user=user)
    created_tasks = created_tasks.exclude(id__in=solo_assignee_tasks)
    assigned_tasks = assigned_tasks.exclude(id__in=solo_assignee_tasks)

    if request.method == "POST":
        search_tag = request.POST.get('tag-filter')
        search_folder = request.POST.get('folder-filter')
        if search_tag:
            created_tasks = created_tasks.filter(tags__name=search_tag)
            assigned_tasks = assigned_tasks.filter(assignees__user=user, assignees__tags__name=search_tag)
            solo_assignee_tasks = solo_assignee_tasks.filter(tags__name=search_tag)

        if search_folder:
            created_tasks = created_tasks.filter(folders__name=search_folder)
            assigned_tasks = assigned_tasks.filter(assignees__user=user, assignees__folders__name=search_folder)
            solo_assignee_tasks = solo_assignee_tasks.filter(folders__name=search_folder)

    combined_query = set(list(assigned_tasks) + list(solo_assignee_tasks))
    created_tasks_sorted, combined_query_sorted = get_sorting(request, created_tasks, combined_query)
    tasks_with_type = [(task, 'solo') if task in solo_assignee_tasks else (task, 'assigned') for task in
                       combined_query_sorted]
    current_time = timezone.now()
    all_user_folders = get_folders(request)
    all_user_tags = get_tags(request)
    return render(request, "tasks/folder-tasks.html",
                  {'folder': folder, 'tasks_with_type': tasks_with_type,
                   'created_tasks': created_tasks_sorted, 'current_time': current_time,
                   'all_user_folders': all_user_folders, 'all_user_tags': all_user_tags})


@login_required
def calendar_view(request):
    assigned_tasks, created_tasks, solo_assignee_tasks = get_tasks(request)
    solo_assignee_tasks_transform = transform_tasks(request, solo_assignee_tasks, True, True)
    assigned_tasks_transform = transform_tasks(request, assigned_tasks, True)
    created_tasks_transform = transform_tasks(request, created_tasks, False)
    all_tasks_transform = solo_assignee_tasks_transform + assigned_tasks_transform + created_tasks_transform
    tasks_json = json.dumps(all_tasks_transform, cls=DjangoJSONEncoder)
    return render(request, "tasks/calendar.html", {'tasks_json': tasks_json})


def transform_tasks(request, task_array, assigned, solo=False):
    ukrainian_month_names = {
        1: 'січня',
        2: 'лютого',
        3: 'березня',
        4: 'квітня',
        5: 'травня',
        6: 'червня',
        7: 'липня',
        8: 'серпня',
        9: 'вересня',
        10: 'жовтня',
        11: 'листопада',
        12: 'грудня',
    }

    tasks = []

    for task in task_array:
        folders_arr = []
        tags_arr = []

        if assigned:
            for assignment in task.assignees.all():
                if assignment.user == request.user:
                    for folder in assignment.folders.all():
                        folders_arr.append(folder.name)
                    for tag in assignment.tags.all():
                        tags_arr.append(tag.name)
                    break

        tasks.append({
            'id': task.id,
            'type': 'solo' if solo else ('assigned' if assigned else 'created'),
            'category': 'Виконання' if assigned else 'Моніторинг',
            'folders': folders_arr if assigned and not solo else [folder.name for folder in task.folders.all()],
            'name': task.title,
            'tags': tags_arr if assigned and not solo else [tag.name for tag in task.tags.all()],
            'users': task.assignees.count(),
            'day': task.deadline.day,
            'month': task.deadline.month,
            'year': task.deadline.year,
            'date': task.deadline.strftime('%d ') + ukrainian_month_names.get(task.deadline.month,
                                                                              '') + task.deadline.strftime(' %Y'),
        })

    return tasks


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    files = File.objects.filter(files_tasks=task)
    for file in files:
        delete_file_from_s3(file.file)
        file.delete()

    assignees = task.assignees.all()
    for assignee in assignees:
        files = assignee.files.all()
        for file in files:
            delete_file_from_s3(file.file)
            file.delete()
        assignee.delete()
    if task.creator == request.user:
        task.delete()
        return JsonResponse({'message': 'Завдання успішно видалено'}, status=204)
    else:
        return JsonResponse({'error': 'Ви не маєте права видаляти це завдання'}, status=403)


def delete_file(request, file_id):
    if request.method == 'POST':
        file = get_object_or_404(File, id=file_id)
        file.delete()
        return JsonResponse({'message': 'Файл успішно видалено'}, status=200)
    else:
        return JsonResponse({'error': 'Метод запиту не підтримується'}, status=405)


def update_task_status(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        is_completed = body_data.get('is_completed')
        if is_completed is not None:
            task_assignment = task.assignees.filter(user=request.user).first()
            if task_assignment:
                task_assignment.is_completed = is_completed
                if is_completed:
                    task_assignment.completion_time = datetime.now()
                    send_notification(
                        f"Учасник {task_assignment.user.username} виконав завдання \"{task.title}\"",
                        task.creator)
                else:
                    task_assignment.completion_time = None
                # task_assignment.completion_time = datetime.now()
                task_assignment.save()
                assignees = task.assignees.all()
                all_assignees_completed = all(assignment.is_completed for assignment in assignees)

                if all_assignees_completed:
                    task.is_completed = True
                    task.save()
                    # Створення нотифікації для кожного виконавця
                    send_notification(f"Всі учасники виконали завдання \"{task.title}\"", task.creator)


                else:
                    task.is_completed = False
                    task.save()
                    if not is_completed:
                        send_notification(
                            f"Учасник {task_assignment.user.username} відмінив надсилання завдання \"{task.title}\"",
                            task.creator)
                return JsonResponse({'message': 'Статус завдання успішно оновлено.'})
            else:
                return JsonResponse({'error': 'Не вдалося знайти виконавця завдання.'},
                                    status=400)
        else:
            return JsonResponse({'error': 'Не вдалося оновити статус завдання. Необхідний параметр is_completed.'},
                                status=400)

    return JsonResponse({'error': 'Метод запиту не підтримується.'}, status=405)


def save_tags_folders_files(task, tags, folders, files):
    # Save tags
    for tag_name in tags:
        tag_name = tag_name.strip()
        if tag_name:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            task.tags.add(tag)

    # Save folders
    for folder_name in folders:
        folder_name = folder_name.strip()
        if folder_name:
            folder, _ = Folder.objects.get_or_create(name=folder_name)
            task.folders.add(folder)

    # Save files
    for file in files:
        if file:
            upload_file_to_s3(file, task.id)


def save_task(request, form, old_files=None):
    creator = request.user
    tags = request.POST.getlist('tags')
    folders = request.POST.getlist('folders')

    files = request.FILES.getlist('files')
    task = form.save(commit=False)
    task.creator = creator
    task.save()
    if old_files:
        for old_file in old_files:
            task.files.add(old_file)

    save_tags_folders_files(task, tags, folders, files)

    assignees = request.POST.getlist('assignees')[0].split(',')
    for assignee_email in assignees:
        assignee = User.objects.get(email=assignee_email)
        task_assignment = TaskAssignment.objects.create(
            user=assignee,
            is_completed=False,
            completion_time=None,
        )
        task.assignees.add(task_assignment)
        send_notification(f"Вам призначено завдання \"{task.title}\"", assignee)
        task_url = request.build_absolute_uri(reverse('tasks:task_info', kwargs={'task_id': task.id}))
        send_task(request, assignee.email, task.title, task_url)
    return task


def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            save_task(request, form)
            return redirect('tasks:all_tasks')
    else:
        form = TaskForm()
    return render(request, "tasks/create-task.html", {'form': form})


def derivative_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    files = task.files.all()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            save_task(request, form, files)
            return redirect('tasks:all_tasks')
    else:
        form = TaskForm(instance=task)
    return render(request, "tasks/create-task.html", {'form': form, 'task': task, 'files': files})


def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    old_files = task.files.all()
    assignees = task.assignees.all()

    if request.method == 'POST':
        form = TaskEditForm(request.POST, instance=task)

        if form.is_valid():
            tags = request.POST.getlist('tags')
            folders = request.POST.getlist('folders')
            files = request.FILES.getlist('files')
            task = form.save(commit=False)
            task.tags.clear()
            task.folders.clear()

            save_tags_folders_files(task, tags, folders, files)

            new_assignees = request.POST.getlist('assignees')[0].split(',')
            existing_assignees_emails = [assignee.user.email for assignee in assignees]
            TaskAssignment.objects.filter(user__email__in=existing_assignees_emails).exclude(
                user__email__in=new_assignees).delete()

            for assignee_email in new_assignees:
                assignee = User.objects.get(email=assignee_email)
                if assignee_email not in existing_assignees_emails:
                    task_assignment = TaskAssignment.objects.create(
                        user=assignee,
                        is_completed=False,
                        completion_time=None,
                    )
                    task.assignees.add(task_assignment)
                    task.is_completed = False
                    task.save()
                    send_notification(f"Вам призначено завдання \"{task.title}\"", assignee)
                    task_url = request.build_absolute_uri(reverse('tasks:task_info', kwargs={'task_id': task.id}))
                    send_task(request, assignee.email, task.title, task_url)
                else:
                    send_notification(f"Завдання \"{task.title}\" було оновлено", assignee)

            task.is_completed = False

            task.save()
            return redirect('tasks:all_tasks')
    else:
        form = TaskEditForm(instance=task)
    return render(request, "tasks/edit-task.html",
                  {'form': form, 'task': task, 'files': old_files})


def assign_edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task_assignment = get_object_or_404(TaskAssignment, user=request.user, assigned_tasks=task)

    if request.method == 'POST':

        tags = request.POST.getlist('tags')  # Отримання списку тегів
        folders = request.POST.getlist('folders')  # Отримання списку папок

        task_assignment.tags.clear()
        task_assignment.folders.clear()

        # Додавання тегів до task assignment
        if tags:
            for tag_name in tags:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    task_assignment.tags.add(tag)

        # Додавання папок до task assignment
        if folders:
            for folder_name in folders:
                folder_name = folder_name.strip()
                if folder_name:
                    folder, _ = Folder.objects.get_or_create(name=folder_name)
                    task_assignment.folders.add(folder)
        return redirect('tasks:all_tasks')
    return render(request, "tasks/assign-edit-task.html", {'task': task, 'task_assignment': task_assignment})


def get_users(request, template_name):
    if 'term' in request.GET:
        term = request.GET.get('term')
        users = User.objects.filter(
            Q(email__icontains=term) | Q(username__icontains=term)
        )
        users_data = list(users.values('email', 'username', 'role'))
        print(users_data)
        return JsonResponse(users_data, safe=False)
    return render(request, template_name)


def users_for_create(request):
    return get_users(request, "tasks/create-task.html")


def users_for_edit(request):
    return get_users(request, "tasks/edit-task.html")


def task_info(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        task_chat, created = TaskChat.create_or_get_private(task, task.creator, request.user)
        task_assignment = get_object_or_404(TaskAssignment, user=request.user, assigned_tasks=task)
        comments = ChatComment.objects.filter(task_chat=task_chat).order_by('-created')
        form = CommentForm()

        if request.method == 'POST' and request.FILES:
            files = request.FILES.getlist('files')
            for file in files:
                upload_assignment_file_to_s3(file, task.id, request.user.id, task_assignment.id)
                task_assignment.is_completed = True
                task_assignment.completion_time = datetime.now()
                task_assignment.save()
            return redirect('tasks:task_info', task_id=task_id)

    except Task.DoesNotExist:
        return redirect('tasks:all_tasks')

    return render(request, "tasks/task-info.html",
                  {'task': task, 'comments': comments, 'task_chat': task_chat, 'form': form,
                   'task_assignment': task_assignment})


def creator_task_view(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        assignment = task.assignees.all()
        assignee_data = []
        for assignee in assignment:
            task_chat, created = TaskChat.create_or_get_private(task, task.creator, assignee.user)
            comments = ChatComment.objects.filter(task_chat=task_chat).order_by('-created')
            assignee_data.append((assignee, comments, task_chat))
        form = CommentForm()
    except Task.DoesNotExist:
        return redirect('tasks:all_tasks')
    return render(request, "tasks/creator-task-view.html",
                  {'task': task, 'form': form, "assignments": assignment, 'assignee_data': assignee_data})
