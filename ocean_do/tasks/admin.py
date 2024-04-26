from django.contrib import admin

from .models import Task, Tag, File, Folder, TaskAssignment, TaskChat, ChatComment

admin.site.register(Tag)
admin.site.register(File)
admin.site.register(Folder)
admin.site.register(TaskAssignment)
admin.site.register(Task)
admin.site.register(TaskChat)
admin.site.register(ChatComment)
