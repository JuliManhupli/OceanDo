from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count
from tasks.views import get_tasks, get_completed_tasks
from tasks.models import Task
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
        print(ratio)
        return render(request, "ocean_do/index.html",
                      {'tasks_with_type': tasks_with_type, 'current_time': current_time,
                       'completed_tasks': completed_tasks, 'ratio': ratio})
    else:
        return render(request, "ocean_do/index.html")


def get_all_data(request):
    try:
        if 'term' in request.GET:
            term = request.GET.get('term')
            assigned_tasks, created_tasks, solo_assignee_tasks = get_tasks(request)
            _, solo_assigned_complete, created_complete, assigned_complete = get_completed_tasks(request)

            all_type_data = []
            added_task_ids = set()
            for task in assigned_tasks.filter(
                    Q(title__istartswith=term) |
                    Q(description__istartswith=term) |
                    Q(tags__name__istartswith=term) |
                    Q(folders__name__istartswith=term)
            ):
                if task.id not in added_task_ids:  # Check if task has not been added already
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'category': "Виконання",
                        'tags': [tag.name for tag in task.tags.all()],
                        'folders': [folder.name for folder in task.folders.all()]
                    }
                    all_type_data.append(task_data)
                    added_task_ids.add(task.id)

            print("1")
            print(all_type_data)


            for task in created_tasks.filter(
                    Q(title__istartswith=term) |
                    Q(description__istartswith=term) |
                    Q(tags__name__istartswith=term) |
                    Q(folders__name__istartswith=term)
            ):
                if task.id not in added_task_ids:  # Check if task has not been added already
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'category': "Моніторинг",
                        'tags': [tag.name for tag in task.tags.all()],
                        'folders': [folder.name for folder in task.folders.all()]
                    }
                    all_type_data.append(task_data)
                    added_task_ids.add(task.id)

            print("2")
            print(all_type_data)

            for task in solo_assignee_tasks.filter(
                    Q(title__istartswith=term) |
                    Q(description__istartswith=term) |
                    Q(tags__name__istartswith=term) |
                    Q(folders__name__istartswith=term)
            ):
                if task.id not in added_task_ids:  # Check if task has not been added already
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'category': "Виконання",
                        'tags': [tag.name for tag in task.tags.all()],
                        'folders': [folder.name for folder in task.folders.all()]
                    }
                    all_type_data.append(task_data)
                    added_task_ids.add(task.id)

            print("3")
            print(all_type_data)

            for task in solo_assigned_complete.filter(
                    Q(title__istartswith=term) |
                    Q(description__istartswith=term) |
                    Q(tags__name__istartswith=term) |
                    Q(folders__name__istartswith=term)
            ):
                if task.id not in added_task_ids:  # Check if task has not been added already
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'category': "Виконання",
                        'tags': [tag.name for tag in task.tags.all()],
                        'folders': [folder.name for folder in task.folders.all()]
                    }
                    all_type_data.append(task_data)
                    added_task_ids.add(task.id)

            print("4")
            print(all_type_data)

            for task in created_complete.filter(
                    Q(title__istartswith=term) |
                    Q(description__istartswith=term) |
                    Q(tags__name__istartswith=term) |
                    Q(folders__name__istartswith=term)
            ):
                if task.id not in added_task_ids:  # Check if task has not been added already
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'category': "Моніторинг",
                        'tags': [tag.name for tag in task.tags.all()],
                        'folders': [folder.name for folder in task.folders.all()]
                    }
                    all_type_data.append(task_data)
                    added_task_ids.add(task.id)

            print("5")
            print(all_type_data)

            for task in assigned_complete.filter(
                    Q(title__istartswith=term) |
                    Q(description__istartswith=term) |
                    Q(tags__name__istartswith=term) |
                    Q(folders__name__istartswith=term)
            ):
                if task.id not in added_task_ids:  # Check if task has not been added already
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'category': task.description,
                        'tags': [tag.name for tag in task.tags.all()],
                        'folders': [folder.name for folder in task.folders.all()]
                    }
                    all_type_data.append(task_data)
                    added_task_ids.add(task.id)

            print("6")
            print(all_type_data)

            return JsonResponse(all_type_data, safe=False)
        return render(request, "ocean_do/index.html")
    except Exception as e:
        traceback.print_exc()  # Print the stack trace to the console for debugging
        return JsonResponse({'error': str(e)}, status=500)
