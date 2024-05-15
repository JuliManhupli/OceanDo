from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('profile', views.profile_view, name='profile'),
    path('groups', views.group_view, name='groups'),
    path('create-group/', views.create_group, name='create_group'),
    path('profile/edit-profile', views.edit_profile_view, name='edit-profile'),
    path('profile/personal-stats', views.personal_stats_view, name='personal-stats'),
    path('delete-avatar/', views.delete_avatar_view, name='delete-avatar'),
]
