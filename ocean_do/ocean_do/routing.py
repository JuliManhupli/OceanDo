from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/notifications/", consumers.NotificationConsumer.as_asgi()),
    path("ws/comments/<chat_name>/", consumers.CommentsConsumer.as_asgi()),
]