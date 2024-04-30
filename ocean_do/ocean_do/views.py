from django.shortcuts import render

from tasks.models import Task


def main(request):
    user = request.user
    assigned_query = Task.objects.filter(assignees__user=user, assignees__is_completed=False)
    created_query = Task.objects.filter(creator=user, is_completed=False)
    combined_query = assigned_query | created_query
    combined_query = combined_query.distinct()
    combined_query = combined_query.order_by('deadline')[:4]
    return render(request, "ocean_do/index.html", {'tasks': combined_query})

