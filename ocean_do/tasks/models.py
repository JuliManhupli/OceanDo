import shortuuid as shortuuid
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


class Folder(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class TaskAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completion_time = models.DateTimeField(null=True, blank=True)
    files = models.ManyToManyField(File, related_name='files_assignments', blank=True)
    tags = models.ManyToManyField(Tag, related_name='tags_assignments', blank=True)
    folders = models.ManyToManyField(Folder, related_name='folders_assignments', blank=True)

    def __str__(self):
        return f"{self.user.username}"


class Task(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, related_name='tags_tasks', blank=True)
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)
    assignees = models.ManyToManyField(TaskAssignment, related_name='assigned_tasks')
    folders = models.ManyToManyField(Folder, related_name='folders_tasks', blank=True)
    files = models.ManyToManyField(File, related_name='files_tasks', blank=True)

    def __str__(self):
        return self.title


class TaskChat(models.Model):
    name = models.CharField(max_length=128, unique=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='task_chats', blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.task.title

    @classmethod
    def create_or_get_private(cls, task, creator, assignee):
        chat = cls.objects.filter(task=task, is_private=True, members=creator).filter(members=assignee).first()

        if chat:
            return chat, False
        else:
            chat = cls.objects.create(task=task, is_private=True)
            chat.members.add(creator, assignee)
            chat.name = shortuuid.uuid()
            chat.save()
            return chat, True


class ChatComment(models.Model):
    task_chat = models.ForeignKey(TaskChat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
