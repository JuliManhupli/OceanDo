from accounts.models import Notification


def notifications(request):
    all_notifications = Notification.objects.all().order_by('-created_at')
    print("Notifications:", all_notifications)
    return {'notifications': all_notifications}
