from django.contrib import admin

from .models import Task, Tag, File

admin.site.register(Tag)
admin.site.register(Task)
admin.site.register(File)
