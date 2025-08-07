from celery import shared_task

from .utils import send_metro_reads_email


@shared_task
def send_verification_email_task(subject, template_name, context, recipient_list):
    """
    A Celery task wrapper for the email sending utility.
    """
    send_metro_reads_email(subject, template_name, context, recipient_list)
