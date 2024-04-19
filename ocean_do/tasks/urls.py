from django.urls import path

from . import views

app_name = 'tasks'
urlpatterns = [
    path('all', views.all_tasks, name='all_tasks'),
    path('create-task/', views.create_task, name='create_task'),
    path('get-users/', views.get_users, name='get_users'),
    path('task-info/<int:task_id>/', views.task_info, name='task_info'),
    path('<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('<int:task_id>/update-status/', views.update_task_status, name='update-status'),

]
