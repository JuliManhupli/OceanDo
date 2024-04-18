from django.contrib.auth.decorators import login_required



def notifications(request):
    user = request.user
    if user.is_authenticated:
        user_notifications = user.notifications_users.all().order_by('-created_at')
    else:
        user_notifications = []
    print("User's notifications:", user_notifications)

    return {'notifications': user_notifications}
