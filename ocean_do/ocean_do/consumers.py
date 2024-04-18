import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


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
