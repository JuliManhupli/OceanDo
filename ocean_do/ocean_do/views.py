from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q

from tasks.views import get_tasks, get_completed_tasks, get_folders
import traceback


def main(request):
    if request.user.is_authenticated:
        assigned_tasks, created_tasks, solo_assignee_tasks = get_tasks(request)
        combined_query = set(list(assigned_tasks) + list(created_tasks) + list(solo_assignee_tasks))
        combined_query_deadline = sorted(combined_query, key=lambda x: x.deadline)[:4]
        tasks_with_type = []
        for task in combined_query_deadline:
            if task in assigned_tasks:
                tasks_with_type.append((task, 'assigned'))
            elif task in solo_assignee_tasks:
                tasks_with_type.append((task, 'solo'))
            else:
                tasks_with_type.append((task, 'created'))
        current_time = timezone.now()
        completed_tasks, _, created_complete, _ = get_completed_tasks(request)
        all_assigned = set(list(assigned_tasks) + list(solo_assignee_tasks) + list(completed_tasks))
        all_created = set(list(created_tasks) + list(created_complete))
        ratio = [len(all_assigned), len(all_created)]
        return render(request, "ocean_do/index.html",
                      {'tasks_with_type': tasks_with_type, 'current_time': current_time,
                       'completed_tasks': completed_tasks, 'ratio': ratio})
    else:
        return render(request, "ocean_do/index.html")


def get_all_data(request):
    try:
        if 'term' in request.GET:
            user = request.user
            term = request.GET.get('term')
            assigned_tasks, created_tasks, solo_assignee_tasks = get_tasks(request)
            _, solo_assigned_complete, created_complete, assigned_complete = get_completed_tasks(request)
            all_folders = get_folders(request)

            all_type_data = []
            added_task_ids = set()
            folders_ids = set()

            for folder in all_folders.filter(
                    Q(name__icontains=term)
            ):
                if folder.id not in folders_ids:
                    folder_data = {
                        'id': folder.id,
                        'title': folder.name,
                        'type': "folder",
                        'link': f'/tasks/folders/{folder.id}/'
                    }
                    all_type_data.append(folder_data)
                    folders_ids.add(folder.id)

            for task in assigned_tasks.filter(
                    Q(title__icontains=term) |
                    Q(assignees__user=user, assignees__tags__name__icontains=term) |
                    Q(assignees__folders__name__icontains=term)
            ):
                if task.id not in added_task_ids:
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'type': "task",
                        'task_type': "Виконання",
                        'tags': [tag.name
                                 for assignment in task.assignees.all()
                                 if assignment.user == request.user
                                 for tag in assignment.tags.all()],
                        'folders': [folder.name
                                    for assignment in task.assignees.all()
                                    if assignment.user == request.user
                                    for folder in assignment.folders.all()],
                        'link': f'/tasks/task-info/{task.id}/'
                    }
                    all_type_data.append(task_data)
                    added_task_ids.add(task.id)

            for task in created_tasks.filter(
                    Q(title__icontains=term) |
                    Q(tags__name__icontains=term) |
                    Q(folders__name__icontains=term)
            ):
                if task.id not in added_task_ids:
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'type': "task",
                        'task_type': "Моніторинг",
                        'tags': [tag.name for tag in task.tags.all()],
                        'folders': [folder.name for folder in task.folders.all()],
                        'link': f'/tasks/task-info-creator/{task.id}/'
                    }
                    all_type_data.append(task_data)
                    added_task_ids.add(task.id)

            for task in solo_assignee_tasks.filter(
                    Q(title__icontains=term) |
                    Q(tags__name__icontains=term) |
                    Q(folders__name__icontains=term)
            ):
                if task.id not in added_task_ids:
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'type': "task",
                        'task_type': "Виконання",
                        'tags': [tag.name for tag in task.tags.all()],
                        'folders': [folder.name for folder in task.folders.all()],
                        'link': f'/tasks/task-info/{task.id}/'
                    }
                    all_type_data.append(task_data)
                    added_task_ids.add(task.id)

            for task in solo_assigned_complete.filter(
                    Q(title__icontains=term) |
                    Q(tags__name__icontains=term) |
                    Q(folders__name__icontains=term)
            ):
                if task.id not in added_task_ids:
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'type': "task",
                        'task_type': "Виконання",
                        'tags': [tag.name for tag in task.tags.all()],
                        'folders': [folder.name for folder in task.folders.all()],
                        'link': f'/tasks/task-info/{task.id}/'
                    }
                    all_type_data.append(task_data)
                    added_task_ids.add(task.id)

            for task in created_complete.filter(
                    Q(title__icontains=term) |
                    Q(tags__name__icontains=term) |
                    Q(folders__name__icontains=term)
            ):
                if task.id not in added_task_ids:
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'type': "task",
                        'task_type': "Моніторинг",
                        'tags': [tag.name for tag in task.tags.all()],
                        'folders': [folder.name for folder in task.folders.all()],
                        'link': f'/tasks/task-info-creator/{task.id}/'
                    }
                    all_type_data.append(task_data)
                    added_task_ids.add(task.id)

            for task in assigned_complete.filter(
                    Q(title__icontains=term) |
                    Q(assignees__user=user, assignees__tags__name__icontains=term) |
                    Q(assignees__folders__name__icontains=term)
            ):
                if task.id not in added_task_ids:
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'type': "task",
                        'task_type': "Виконання",
                        'tags': [tag.name
                                 for assignment in task.assignees.all()
                                 if assignment.user == request.user
                                 for tag in assignment.tags.all()],
                        'folders': [folder.name
                                    for assignment in task.assignees.all()
                                    if assignment.user == request.user
                                    for folder in assignment.folders.all()],
                        'link': f'/tasks/task-info/{task.id}/'
                    }
                    all_type_data.append(task_data)
                    added_task_ids.add(task.id)

            return JsonResponse(all_type_data, safe=False)
        return render(request, "ocean_do/index.html")
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
