from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('profile', views.profile_view, name='profile'),
    path('profile/edit-profile', views.edit_profile_view, name='edit-profile'),
    path('delete-avatar/', views.delete_avatar_view, name='delete-avatar'),
]
