from django.urls import path

from . import views

app_name = 'tasks'
urlpatterns = [
    path('all', views.all_tasks, name='all_tasks'),
    path('calendar', views.calendar_view, name='calendar'),
    path('completed-tasks', views.completed_tasks, name='completed_tasks'),
    path('folders/<int:folder_id>/', views.folder_tasks, name='folder_tasks'),
    path('get-side-menu-folder/', views.user_folders, name='side_menu'),
    path('create-task/', views.create_task, name='create_task'),
    path('get-users/', views.get_users, name='get_users'),
    path('task-info-creator/<int:task_id>/', views.creator_task_view, name='creator_task_view'),
    path('task-info/<int:task_id>/', views.task_info, name='task_info'),
    path('<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('<int:task_id>/update-status/', views.update_task_status, name='update-status'),
    path('files/delete/<int:file_id>/', views.delete_file, name='delete_file'),

]
