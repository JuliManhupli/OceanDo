from django.urls import path

from . import views

app_name = 'tasks'
urlpatterns = [
    path('all', views.all_tasks, name='all_tasks'),
]