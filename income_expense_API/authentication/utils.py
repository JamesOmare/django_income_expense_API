from django.core.mail import EmailMessage
from django.conf import settings
from loguru import logger


class Util:
    @staticmethod
    def send_email(data):
        email_subject = data['email_subject']
        email_body = data['email_body']
        email_recipient = data['to_email']
        
        email = EmailMessage(
            email_subject, email_body,
            settings.DEFAULT_FROM_EMAIL, [email_recipient, ],
        )
        return email.send(fail_silently=False)

      