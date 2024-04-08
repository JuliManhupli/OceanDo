from accounts.models import User
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class File(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    file = models.FileField(upload_to='files/')

    def __str__(self):
        return f"{self.title}"


class Task(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag)
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)
    assignees = models.ManyToManyField(User, related_name='assigned_tasks')
    files = models.ManyToManyField(File, related_name='files_tasks', blank=True)

    def __str__(self):
        return self.title


