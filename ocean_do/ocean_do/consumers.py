import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from tasks.models import TaskChat, ChatComment
from tasks.views import send_notification


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        print("User:", self.user)
        if not self.user.is_authenticated:
            print("User is not authenticated. Closing connection.")
            self.close()
            return
        self.room_group_name = f"user-notifications-{self.user.id}"
        print("Room group name:", self.room_group_name)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name, self.channel_name
            )

    def send_notification(self, event):
        message = event["message"]
        print("Sending notification:", message)
        self.send(text_data=json.dumps({"message": message}))


class CommentsConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            self.close()
            return
        self.chat_name = self.scope["url_route"]["kwargs"].get("chat_name")
        print("Chat name:", self.chat_name)
        if not self.chat_name:
            self.close()
            return
        try:
            self.chat = TaskChat.objects.get(name=self.chat_name)
        except TaskChat.DoesNotExist:
            self.close()
            return
        self.group_name = f'comments_{self.chat_name}'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            if self.user.is_authenticated:
                async_to_sync(self.channel_layer.group_discard)(
                    self.group_name,
                    self.channel_name
                )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        comment = ChatComment.objects.create(
            task_chat=self.chat,
            user=self.user,
            message=message
        )

        for member in self.chat.members.all():
            if member != self.user:
                send_notification(f"{self.user.username} залишив коментар до завдання \"{self.chat.task.title}\"",
                                  member)

        event = {
            'type': 'message_handler',
            'comment_id': comment.id,
        }
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, event
        )

    def message_handler(self, event):
        comment_id = event["comment_id"]
        comment = ChatComment.objects.get(id=comment_id)
        html = render_to_string("tasks/partials/task-comment.html", context={'comment': comment})
        self.send(text_data=json.dumps({
            'html': html
        }))
