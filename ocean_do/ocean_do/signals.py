from accounts.models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.dispatch import receiver
from django.db.models.signals import m2m_changed


@receiver(m2m_changed, sender=Notification.users.through)
def notification_users_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add' and not reverse:
        print("Notification users updated:", instance)
        message = instance.message
        users = instance.users.all()
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
