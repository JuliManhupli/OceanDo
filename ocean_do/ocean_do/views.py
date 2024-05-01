from django.shortcuts import render
from django.utils import timezone
from tasks.views import get_tasks


def main(request):
    if request.user.is_authenticated:
        assigned_tasks, created_tasks, solo_assignee_tasks = get_tasks(request)
        combined_query = set(list(assigned_tasks) + list(created_tasks) + list(solo_assignee_tasks))
        combined_query = sorted(combined_query, key=lambda x: x.deadline)[:4]
        tasks_with_type = []
        for task in combined_query:
            if task in assigned_tasks:
                tasks_with_type.append((task, 'assigned'))
            elif task in solo_assignee_tasks:
                tasks_with_type.append((task, 'solo'))
            else:
                tasks_with_type.append((task, 'created'))
        current_time = timezone.now()
        return render(request, "ocean_do/index.html", {'tasks_with_type': tasks_with_type, 'current_time': current_time})
    else:
        return render(request, "ocean_do/index.html")
