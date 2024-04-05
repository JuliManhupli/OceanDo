from django.urls import path

from . import views

app_name = 'tasks'
urlpatterns = [
    path('all', views.all_tasks, name='all_tasks'),
    path('create-task/', views.create_task, name='create_task'),
    path('<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('<int:task_id>/update-status/', views.update_task_status, name='update-status'),

]
