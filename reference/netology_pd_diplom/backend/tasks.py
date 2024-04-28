from celery import shared_task
from celery.contrib.django.task import DjangoTask
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

@shared_task(base=DjangoTask)
def send_email(title, message, sender, recipients):
    
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