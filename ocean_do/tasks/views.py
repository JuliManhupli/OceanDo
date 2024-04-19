import json

from accounts.models import User, Notification
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from ocean_do.aws import upload_file_to_s3

from .form import TaskForm
from .models import Tag, Task, TaskAssignment
from .utils import send_task


@login_required
def all_tasks(request):
    user = request.user
    assigned_tasks = Task.objects.filter(assignees__user=user, assignees__is_completed=False)
    created_tasks = Task.objects.filter(creator=user, is_completed=False)
    solo_assignee_tasks = created_tasks.annotate(assignees_count=Count('assignees')).filter(assignees_count=1).filter(assignees__user=user)
    created_tasks = created_tasks.exclude(id__in=solo_assignee_tasks)
    return render(request, "tasks/tasks.html", {'assigned_tasks': assigned_tasks, 'created_tasks': created_tasks})


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.creator == request.user:
        task.delete()
        return JsonResponse({'message': 'Завдання успішно видалено'}, status=204)
    else:
        return JsonResponse({'error': 'Ви не маєте права видаляти це завдання'}, status=403)


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
                send_task(request, assignee.email, task.title, task_url)

            # Завантаження файлів
            for file in request.FILES.getlist('files'):
                upload_file_to_s3(file, task.id)
            return redirect('tasks:all_tasks')
    else:
        form = TaskForm()
    return render(request, "tasks/create-task.html", {'form': form})


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
    except Task.DoesNotExist:
        return redirect('tasks:all_tasks')

    return render(request, "tasks/task-info.html", {'task': task})
