from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .form import TaskForm
from .models import Tag


@login_required
def all_tasks(request):

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
            return redirect('main')
    else:
        form = TaskForm()
    return render(request, "tasks/tasks.html", {'form': form})

    # return render(request, "tasks/tasks.html")
