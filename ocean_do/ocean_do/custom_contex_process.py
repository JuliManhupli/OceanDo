
def notifications(request):
    user = request.user
    if user.is_authenticated:
        user_notifications = user.notifications_users.order_by('-created_at')
        unread_notification_count = user.notifications_users.filter(is_read=False).count()
    else:
        user_notifications = []
        unread_notification_count = 0

    return {'notifications': user_notifications, 'unread_notification_count': unread_notification_count}
