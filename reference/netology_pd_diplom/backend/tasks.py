from celery import shared_task
from celery.contrib.django.task import DjangoTask
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

@shared_task(base=DjangoTask)
def send_email(title, message, sender, recipients):
    
    print(f'settings.EMAIL_BACKEND={settings.EMAIL_BACKEND}')
    print(f'settings.EMAIL_HOST={settings.EMAIL_HOST}')
    print(f'settings.EMAIL_HOST_USER={settings.EMAIL_HOST_USER}')
    print(f'settings.EMAIL_HOST_PASSWORD={settings.EMAIL_HOST_PASSWORD}')
    print(f'settings.EMAIL_PORT={settings.EMAIL_PORT}')
    msg = EmailMultiAlternatives(
            # title:
            title,
            # message:
            message,
            # from:
            sender,
            # to:
            recipients
        )
    msg.send()