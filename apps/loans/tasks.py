from celery import shared_task
from django.conf import settings
from django.db.models import F  # For atomic updates
from django.utils import timezone

from apps.site_config.models import LibrarySettings
from apps.users.tasks import send_verification_email_task

from .models import Loan


@shared_task
def send_due_date_reminders():
    """
    Finds loans due tomorrow and sends a reminder email.
    """
    tomorrow = timezone.now().date() + timezone.timedelta(days=1)
    loans_due_tomorrow = Loan.objects.filter(due_date__date=tomorrow, is_returned=False)

    for loan in loans_due_tomorrow:
        user = loan.user
        book = loan.book
        subject = f"Reminder: Your book '{book.title}' is due tomorrow!"
        account_path = "/loans/"
        full_cta_url = f"{settings.FRONTEND_BASE_URL}{account_path}"

        context = {
            "email_title": "Due Date Reminder",
            "user_name": user.first_name,
            "user_email": user.email,
            "book_title": book.title,
            "due_date": loan.due_date.strftime("%A, %B %d, %Y"),
            "cta_url": full_cta_url,  # <-- Use the dynamic URL
            "cta_text": "View Your Loans",
        }
        send_verification_email_task.delay(
            subject, "emails/due_date_reminder.html", context, [user.email]
        )
    return f"Sent {loans_due_tomorrow.count()} due date reminders."


@shared_task
def calculate_and_notify_fines():
    """
    A daily task to calculate fines for all overdue, unreturned books.
    If a fine is active and greater than 0, it sends a notification.
    """
    settings = LibrarySettings.get_solo()
    fine_per_day = settings.fine_per_day

    if fine_per_day <= 0:
        return "Fine system is disabled (fine per day is 0 or less)."

    today = timezone.now().date()

    # Find all loans that are overdue and not yet returned.
    overdue_loans = Loan.objects.filter(due_date__date__lt=today, is_returned=False)

    fines_updated = 0
    notifications_sent = 0

    for loan in overdue_loans:
        days_overdue = (today - loan.due_date.date()).days
        calculated_fine = days_overdue * fine_per_day

        # Get or create the fine object for this loan
        fine, created = Fine.objects.get_or_create(
            loan=loan, user=loan.user, defaults={"amount": calculated_fine}
        )

        # If the fine already existed, update its amount
        if not created and fine.amount != calculated_fine:
            fine.amount = calculated_fine
            fine.save()
            fines_updated += 1

        # --- Send Notification Email ---
        # We only send if the fine is PENDING.
        if fine.status == Fine.FineStatus.PENDING and fine.amount > 0:
            user = loan.user
            book = loan.book
            subject = f"Action Required: Overdue Book and Fine Notification"
            context = {
                "email_title": "Overdue Book Notice",
                "user_name": user.first_name,
                "user_email": user.email,
                "main_message": f"Our records show that the book '{book.title}' is overdue. A fine has been applied to your account.",
                "book_title": book.title,
                "due_date": loan.due_date.strftime("%A, %B %d, %Y"),
                "fine_amount": f"${fine.amount:.2f}",
                "alert_message": "Please return the book as soon as possible to prevent further fines. You can view your account details by clicking the button below.",
                "cta_url": f"{settings.FRONTEND_BASE_URL}/account/fines/",
                "cta_text": "View My Fines",
            }
            send_verification_email_task.delay(
                subject, "emails/fine_notification.html", context, [user.email]
            )
            notifications_sent += 1

    return f"Processed {overdue_loans.count()} overdue loans. Updated {fines_updated} fines. Sent {notifications_sent} notifications."
