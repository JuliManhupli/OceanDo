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

from .form import TaskForm, CommentForm
from .models import Tag, Task, TaskAssignment, File, Folder, TaskChat, ChatComment


def user_folders(request):
    try:
        tasks = Task.objects.filter(creator=request.user, is_completed=False)
        task_assignments = TaskAssignment.objects.filter(user=request.user, is_completed=False)
        task_folders = Folder.objects.filter(folders_tasks__in=tasks)
        task_assignments_folders = Folder.objects.filter(folders_assignments__in=task_assignments)

        all_folders = task_folders | task_assignments_folders
        all_folders = all_folders.order_by('name').distinct()
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
    # solo_assignee_query = solo_assignee_query.filter(assignees__is_completed=False)
    return assigned_query, created_query, solo_assignee_query


@login_required
def all_tasks(request):
    assigned_tasks, created_tasks, solo_assignee_tasks = get_tasks(request)
    combined_query = set(list(assigned_tasks) + list(solo_assignee_tasks))
    tasks_with_type = [(task, 'solo') if task in solo_assignee_tasks else (task, 'assigned') for task in combined_query]
    current_time = timezone.now()
    return render(request, "tasks/all-tasks.html",
                  {'tasks_with_type': tasks_with_type, 'created_tasks': created_tasks, 'current_time': current_time})


def get_completed_tasks(request):
    user = request.user
    assigned_tasks = Task.objects.filter(assignees__user=user, assignees__is_completed=True)
    created_tasks = Task.objects.filter(creator=user, is_completed=True)
    solo_assignee_tasks = created_tasks.annotate(assignees_count=Count('assignees')).filter(assignees_count=1).filter(
        assignees__user=user)
    created_tasks = created_tasks.exclude(id__in=solo_assignee_tasks)
    assigned_tasks = assigned_tasks.exclude(id__in=solo_assignee_tasks)
    combined_query = set(list(assigned_tasks) + list(solo_assignee_tasks))
    return combined_query, solo_assignee_tasks, created_tasks


def completed_tasks(request):
    combined_query, solo_assignee_tasks, created_tasks = get_completed_tasks(request)
    tasks_with_type = [(task, 'solo') if task in solo_assignee_tasks else (task, 'assigned') for task in combined_query]
    return render(request, "tasks/completed-tasks.html",
                  {'tasks_with_type': tasks_with_type, 'created_tasks': created_tasks})


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
    combined_query = set(list(assigned_tasks) + list(solo_assignee_tasks))
    tasks_with_type = [(task, 'solo') if task in solo_assignee_tasks else (task, 'assigned') for task in combined_query]
    current_time = timezone.now()
    return render(request, "tasks/folder-tasks.html",
                  {'folder': folder, 'tasks_with_type': tasks_with_type,
                   'created_tasks': created_tasks, 'current_time': current_time})


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
                task_assignment.completion_time = datetime.now()
                task_assignment.save()
                assignees = task.assignees.all()
                all_assignees_completed = all(assignment.is_completed for assignment in assignees)
                print(all_assignees_completed)

                if all_assignees_completed:
                    task.is_completed = True
                    task.save()
                    # Створення нотифікації для кожного виконавця
                    notification_message = f"Всі учасники виконали завдання \"{task.title}\""
                    notification = Notification.objects.create(
                        message=notification_message,
                    )
                    notification.users.set([task.creator])
                    notification.save()
                    # task_url = request.build_absolute_uri(reverse('tasks:task_info', kwargs={'task_id': task.id}))
                    # print(task_url)
                    # send_task(request, assignee.email, task.title, task_url)

                else:
                    task.is_completed = False
                    task.save()
                    if not is_completed:
                        notification_message = f"Учасник {task_assignment.user.username} відмінив надсилання завдання \"{task.title}\""
                        notification = Notification.objects.create(
                            message=notification_message,
                        )
                        notification.users.set([task.creator])
                        notification.save()
                return JsonResponse({'message': 'Статус завдання успішно оновлено.'})
            else:
                return JsonResponse({'error': 'Не вдалося знайти виконавця завдання.'},
                                    status=400)
        else:
            return JsonResponse({'error': 'Не вдалося оновити статус завдання. Необхідний параметр is_completed.'},
                                status=400)

    return JsonResponse({'error': 'Метод запиту не підтримується.'}, status=405)


def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():
            creator = request.user
            tags = request.POST.getlist('tags')  # Отримання списку тегів
            folders = request.POST.getlist('folders')  # Отримання списку папок
            task = form.save(commit=False)
            task.creator = creator
            task.save()  # Збереження завдання без тегів

            # Додавання тегів до завдання
            if tags:
                for tag_name in tags:
                    tag_name = tag_name.strip()
                    if tag_name:
                        tag, _ = Tag.objects.get_or_create(name=tag_name)
                        task.tags.add(tag)

            # Додавання папок до завдання
            if folders:
                for folder_name in folders:
                    folder_name = folder_name.strip()
                    if folder_name:
                        folder, _ = Folder.objects.get_or_create(name=folder_name)
                        task.folders.add(folder)

            # Збереження виконавців у TaskAssignment
            assignees = request.POST.getlist('assignees')[0].split(',')
            for assignee_email in assignees:
                assignee = User.objects.get(email=assignee_email)
                task_assignment = TaskAssignment.objects.create(
                    user=assignee,
                    is_completed=False,
                    completion_time=None,
                )
                task.assignees.add(task_assignment)

                # Створення нотифікації для кожного виконавця
                notification_message = f"Вам призначено завдання \"{task.title}\""
                notification = Notification.objects.create(
                    message=notification_message,
                )
                notification.users.set([assignee])
                notification.save()
                task_url = request.build_absolute_uri(reverse('tasks:task_info', kwargs={'task_id': task.id}))
                print(task_url)
                # send_task(request, assignee.email, task.title, task_url)

            # Завантаження файлів
            for file in request.FILES.getlist('files'):
                upload_file_to_s3(file, task.id)
            return redirect('tasks:all_tasks')
    else:
        form = TaskForm()
    return render(request, "tasks/create-task.html", {'form': form})


def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    files = task.files.all()
    tags = task.tags.all()
    folders = task.folders.all()
    assignees = task.assignees.all()

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            tags = request.POST.getlist('tags')
            folders = request.POST.getlist('folders')
            task = form.save(commit=False)

            task.tags.clear()
            task.folders.clear()

            # Додавання тегів до завдання
            for tag_name in tags:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    task.tags.add(tag)

            for folder_name in folders:
                folder_name = folder_name.strip()
                if folder_name:
                    folder, _ = Folder.objects.get_or_create(name=folder_name)
                    task.folders.add(folder)

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
                # Створення нотифікації для кожного нового виконавця
                notification_message = f"Завдання \"{task.title}\" було оновлено"
                notification = Notification.objects.create(
                    message=notification_message,
                )
                notification.users.set([assignee])
                notification.save()

            for file in request.FILES.getlist('files'):
                upload_file_to_s3(file, task.id)

            task.save()
            return redirect('tasks:all_tasks')
    else:
        form = TaskForm(instance=task)
    return render(request, "tasks/edit-task.html",
                  {'form': form, 'task': task, 'folders': folders, 'files': files, 'tags': tags,
                   'assignees': assignees})


def assign_edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task_assignment = get_object_or_404(TaskAssignment, user=request.user, assigned_tasks=task)

    print(task_assignment)
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
            Q(email__istartswith=term) | Q(username__istartswith=term)
        )
        users_data = list(users.values('email', 'username'))
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

        if request.method == 'POST' and request.FILES:
            files = request.FILES.getlist('files')
            for file in files:
                upload_assignment_file_to_s3(file, task.id, request.user.id, task_assignment.id)
                task_assignment.is_completed = True
                task_assignment.completion_time = datetime.now()
                task_assignment.save()
            return redirect('tasks:task_info', task_id=task_id)

        if request.headers.get('HX-Request'):
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.task_chat = task_chat
                comment.save()

                context = {'comment': comment}
                return render(request, "tasks/partials/task-comment.html", context)
        if task_chat:
            comments = ChatComment.objects.filter(task_chat=task_chat).order_by('-created')
        else:
            comments = None

        form = CommentForm()
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
            if request.headers.get('HX-Request'):
                form = CommentForm(request.POST)
                if form.is_valid():
                    comment = form.save(commit=False)
                    comment.user = request.user
                    comment.task_chat = task_chat
                    comment.save()
                    comments = ChatComment.objects.filter(task_chat=task_chat).order_by('-created')
            else:
                comments = ChatComment.objects.filter(task_chat=task_chat).order_by('-created')
            assignee_data.append((assignee, comments, task_chat))
        form = CommentForm()
    except Task.DoesNotExist:
        return redirect('tasks:all_tasks')
    return render(request, "tasks/creator-task-view.html",
                  {'task': task, 'form': form, "assignments": assignment, 'assignee_data': assignee_data})

