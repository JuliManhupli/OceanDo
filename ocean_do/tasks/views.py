import json
from datetime import datetime

from accounts.models import User, Notification
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from ocean_do.aws import upload_file_to_s3, upload_assignment_file_to_s3, delete_file_from_s3

from .form import TaskForm, CommentForm
from .models import Tag, Task, TaskAssignment, File, Folder


def user_folders(request):
    try:
        tasks = Task.objects.filter(creator=request.user)
        user_folders = Folder.objects.filter(folders_tasks__in=tasks).distinct()
        folders_data = [{'id': folder.id, 'name': folder.name} for folder in user_folders]
        print(folders_data)
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
    return assigned_query, created_query, solo_assignee_query


@login_required
def all_tasks(request):
    user = request.user
    assigned_tasks = Task.objects.filter(assignees__user=user, assignees__is_completed=False)
    created_tasks = Task.objects.filter(creator=user, is_completed=False)
    solo_assignee_tasks = created_tasks.annotate(assignees_count=Count('assignees')).filter(assignees_count=1).filter(
        assignees__user=user).filter(assignees__is_completed=False)
    created_tasks = created_tasks.exclude(id__in=solo_assignee_tasks)
    assigned_tasks = assigned_tasks.exclude(id__in=solo_assignee_tasks)

    print(assigned_tasks)
    print(created_tasks)
    print(solo_assignee_tasks)

    return render(request, "tasks/all-tasks.html",
                  {'solo_assignee_tasks': solo_assignee_tasks, 'assigned_tasks': assigned_tasks,
                   'created_tasks': created_tasks})


def calendar_view(request):
    assigned_tasks, created_tasks, assigned_tasks = get_tasks(request)

    assigned_tasks_transform = transform_tasks(request, assigned_tasks, True)
    created_tasks_transform = transform_tasks(request, created_tasks, False)
    tasks = assigned_tasks_transform + created_tasks_transform
    print("------------")
    print(tasks)

    tasks_json = json.dumps(tasks, cls=DjangoJSONEncoder)
    print("------------")
    print(tasks_json)

    return render(request, "tasks/calendar.html", {'tasks_json': tasks_json})


def transform_tasks(request, task_array, assigned):
    tasks = []
    for task in task_array:
        # if (assigned):
        #     is_completed = False
        #     user_folders = []
        #
        #     for assignment in task.assignees.all():
        #         if assignment.user == request.user:
        #             is_completed = assignment.is_completed
        #         for folder in assignment.folders.all():
        #             user_folders.append(folder.name)
        #         break
        # else:
        #     is_completed = False
        #     user_folders = []
        tasks.append({
            'id': task.id,
            # 'is_complete': is_completed,
            'category': 'Виконання' if assigned else 'Моніторинг',
            'folders': [] if assigned else [folder.name for folder in task.folders.all()],
            'name': task.title,
            'tags': [tag.name for tag in task.tags.all()],
            'users': task.assignees.count(),
            'day': task.deadline.day,
            'month': task.deadline.month,
            'year': task.deadline.year,
            'date': task.deadline.strftime('%d %B %Y'),
        })
    return tasks


def completed_tasks(request):
    user = request.user
    assigned_tasks = Task.objects.filter(assignees__user=user, assignees__is_completed=True)
    created_tasks = Task.objects.filter(creator=user, is_completed=True)
    solo_assignee_tasks = created_tasks.annotate(assignees_count=Count('assignees')).filter(assignees_count=1).filter(
        assignees__user=user)
    created_tasks = created_tasks.exclude(id__in=solo_assignee_tasks)
    assigned_tasks = assigned_tasks.exclude(id__in=solo_assignee_tasks)

    print(assigned_tasks)
    print(created_tasks)
    print(solo_assignee_tasks)

    return render(request, "tasks/completed-tasks.html",
                  {'solo_assignee_tasks': solo_assignee_tasks, 'assigned_tasks': assigned_tasks,
                   'created_tasks': created_tasks})


def folder_tasks(request, folder_id):
    user = request.user
    folder = Folder.objects.get(id=folder_id)

    assigned_tasks = Task.objects.filter(assignees__user=user, assignees__is_completed=False)
    created_tasks = Task.objects.filter(creator=user, folders=folder, is_completed=False)
    solo_assignee_tasks = created_tasks.annotate(assignees_count=Count('assignees')).filter(assignees_count=1).filter(
        assignees__user=user)
    created_tasks = created_tasks.exclude(id__in=solo_assignee_tasks)
    print(created_tasks)
    print(folder)
    return render(request, "tasks/folder-tasks.html",
                  {'folder': folder, 'assigned_tasks': assigned_tasks, 'created_tasks': created_tasks})


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
        return JsonResponse({'message': 'Файл успішно видалено'}, status=204)
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
    folders = task.folders.all()
    files = task.files.all()
    tags = task.tags.all()
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

            assignees = request.POST.getlist('assignees')[0].split(',')
            task.assignees.clear()

            for assignee_email in assignees:
                if assignee_email:
                    assignee = User.objects.get(email=assignee_email)
                    task_assignment = TaskAssignment.objects.create(
                        user=assignee,
                        is_completed=False,
                        completion_time=None,
                    )
                    task.assignees.add(task_assignment)

                    # Створення нотифікації для кожного виконавця
                    notification_message = f"Завдання \"{task.title}\" було оновлено"
                    notification = Notification.objects.create(
                        message=notification_message,
                    )
                    notification.users.set([assignee])
                    notification.save()
                    # task_url = request.build_absolute_uri(reverse('tasks:task_info', kwargs={'task_id': task.id}))
                    # send_task(request, assignee.email, task.title, task_url)

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

        print(tags)
        print(folders)
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
    return render(request, "tasks/assign-edit-task.html", {'task': task})


def get_users(request):
    if 'term' in request.GET:
        term = request.GET.get('term')
        users = User.objects.filter(
            Q(email__istartswith=term) | Q(username__istartswith=term)
        )
        users_data = list(users.values('email', 'username'))
        return JsonResponse(users_data, safe=False)
    return render(request, "tasks/create-task.html")


def task_info(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        # task_chat, created = TaskChat.objects.get_or_create(task=task)
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

                return JsonResponse({
                    'message': comment.message,
                    'username': comment.user.username,
                    'created': comment.created.strftime("%d.%m.%Y %H:%M"),
                })

        # if task_chat:
        #     comments = ChatComment.objects.filter(task_chat=task_chat).order_by('-created')
        # else:
        comments = None

        form = CommentForm()
    except Task.DoesNotExist:
        return redirect('tasks:all_tasks')

    return render(request, "tasks/task-info.html",
                  {'task': task, 'comments': comments, 'form': form, 'task_assignment': task_assignment})


def creator_task_view(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        assignment = task.assignees.all()
    except Task.DoesNotExist:
        return redirect('tasks:all_tasks')

    return render(request, "tasks/creator-task-view.html", {'task': task, 'assignments': assignment})