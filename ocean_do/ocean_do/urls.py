from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.decorators.cache import cache_control
from django.contrib.staticfiles.views import serve

from . import views
from . import settings

# app_name = 'main'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main, name='main'),
    path('auth/', include('accounts.urls')),
    path('tasks/', include('tasks.urls')),
    path('users/', include('users.urls')),
] + static(settings.STATIC_URL, view=cache_control(no_cache=True, must_revalidate=True)(serve))
