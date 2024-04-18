from django.contrib.auth.decorators import login_required


@login_required
def notifications(request):
    user = request.user
    user_notifications = user.notifications_users.all().order_by('-created_at')
    print("User's notifications:", user_notifications)
    return {'notifications': user_notifications}
