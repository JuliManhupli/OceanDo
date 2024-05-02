from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/notifications/", consumers.NotificationConsumer.as_asgi()),
    # re_path(r"ws/comments/", consumers.CommentsConsumer.as_asgi()),
    path("ws/comments/<chat_name>/", consumers.CommentsConsumer.as_asgi()),
    # re_path(r"ws/comments/(?P<chat_name>[\w-]+)/$", consumers.CommentsConsumer.as_asgi()),
    # re_path(r"ws/comments/public-chat/", consumers.CommentsConsumer.as_asgi()),
    # re_path(r"ws/comments/<chat_name>/", consumers.CommentsConsumer.as_asgi()),
]