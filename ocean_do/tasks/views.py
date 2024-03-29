import json

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .form import TaskForm
from .models import Tag, Task


@login_required
def all_tasks(request):
    user = request.user
    assigned_tasks = Task.objects.filter(assignees=user, is_completed=False)
    created_tasks = Task.objects.filter(creator=user, is_completed=False)

    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():
            creator = request.user
            form.instance.creator = creator
            tags = request.POST.getlist('tags')
            task = form.save()
            for tag_name in tags:
                tag_name = tag_name.strip().title()
                if tag_name:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    task.tags.add(tag)
            return redirect('tasks:all_tasks')
    else:
        form = TaskForm()
    return render(request, "tasks/tasks.html", {'assigned_tasks': assigned_tasks, 'created_tasks': created_tasks,
                                                'form': form})


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return JsonResponse({'message': 'Task deleted successfully'}, status=204)


def update_task_status(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        is_completed = body_data.get('is_completed')
        if is_completed is not None:  # Перевірка, чи параметр is_completed був надісланий
            task.is_completed = bool(int(is_completed))
            task.save()
            return JsonResponse({'message': 'Статус завдання успішно оновлено.'})
        else:
            return JsonResponse({'error': 'Не вдалося оновити статус завдання. Необхідний параметр is_completed.'}, status=400)

    return JsonResponse({'error': 'Метод запиту не підтримується.'}, status=405)