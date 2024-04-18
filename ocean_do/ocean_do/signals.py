from accounts.models import Notification
from accounts.models import User
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Notification)
def notification_handler(sender, instance, created, **kwargs):
    if created:
        print("Notification created:", instance)
        message = instance.message
        users = User.objects.all()
        print("Users:", users)
        print("Message:", message)
        channel_layer = get_channel_layer()
        for user in users:
            print("User:", user)
            group_name = f"user-notifications-{user.id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_notification",
                    "message": message,
                }
            )
        instance.is_send = True
        instance.save()
