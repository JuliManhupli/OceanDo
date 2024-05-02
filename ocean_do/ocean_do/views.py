from django.shortcuts import render
from django.utils import timezone
from tasks.views import get_tasks, get_completed_tasks


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
        completed_tasks, _, created_complete = get_completed_tasks(request)
        all_assigned = set(list(assigned_tasks) + list(solo_assignee_tasks) + list(completed_tasks))
        all_created = set(list(created_tasks) + list(created_complete))
        ratio = [len(all_assigned), len(all_created)]
        print(ratio)
        return render(request, "ocean_do/index.html",
                      {'tasks_with_type': tasks_with_type, 'current_time': current_time,
                       'completed_tasks': completed_tasks, 'ratio': ratio})
    else:
        return render(request, "ocean_do/index.html")
