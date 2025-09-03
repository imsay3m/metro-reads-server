from celery import shared_task
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from .utils import send_metro_reads_email


@shared_task
def send_verification_email_task(subject, template_name, context, recipient_list):
    """
    Celery task to send a templated email with basic recipient validation.
    Invalid addresses are skipped to prevent SMTP 553 errors.
    """
    validator = EmailValidator()

    valid_recipients = []
    for recipient in recipient_list or []:
        try:
            validator(recipient)
            valid_recipients.append(recipient)
        except ValidationError:
            print(f"Skipping invalid email recipient: {recipient}")

    # De-duplicate while preserving order
    seen = set()
    valid_recipients_deduped = []
    for r in valid_recipients:
        if r not in seen:
            valid_recipients_deduped.append(r)
            seen.add(r)

    if not valid_recipients_deduped:
        print("No valid recipients after validation; email not sent.")
        return False

    return send_metro_reads_email(
        subject, template_name, context, valid_recipients_deduped
    )
