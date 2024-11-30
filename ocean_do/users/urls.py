from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('profile', views.profile_view, name='profile'),
    path('groups', views.group_view, name='groups'),
    path('create-group/', views.create_group, name='create_group'),
    path('<int:group_id>/delete/', views.delete_group, name='delete_group'),
    path('<int:group_id>/edit/', views.edit_group, name='edit_group'),
    # path('get-all-groups', views.get_all_groups, name='get_all_groups'),
    path('users-for-group', views.users_for_group, name='users_for_group'),
    path('profile/edit-profile', views.edit_profile_view, name='edit-profile'),
    path('profile/personal-stats', views.personal_stats_view, name='personal-stats'),
    path('delete-avatar/', views.delete_avatar_view, name='delete-avatar'),
]
