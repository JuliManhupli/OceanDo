from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from accounts.models import User


def send_task(request, email, task_name, task_url):
    user = User.objects.get(email=email)

    # відправка на пошту
    subject = f"Вам призначено нове завдання {task_name}"
    html_message = render_to_string('tasks/email_template.html', {'user_username': user.username,
                                                                  'task_name': task_name, 'task_url': task_url})
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = [user.email]

    mail = EmailMultiAlternatives(subject, plain_message, from_email, to_email)
    mail.attach_alternative(html_message, "text/html")
    mail.send()
