from django.contrib import admin

from .models import Task, Tag

admin.site.register(Tag)
admin.site.register(Task)
