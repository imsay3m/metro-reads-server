from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.books.models import Book
from apps.users.tasks import send_verification_email_task

from .models import BookQueue


@shared_task
def promote_next_in_queue(book_id):
    """
    Promotes the next user in the queue for a given book.
    This is called when a book is returned or a reservation expires.
    """
    try:
        book = Book.objects.get(id=book_id)
        # Find the next user in the queue (oldest 'ACTIVE' entry)
        next_in_queue = (
            BookQueue.objects.filter(book=book, status=BookQueue.QueueStatus.ACTIVE)
            .order_by("created_at")
            .first()
        )

        if next_in_queue:
            user = next_in_queue.user
            # Reserve the book for this user
            next_in_queue.status = BookQueue.QueueStatus.RESERVED
            next_in_queue.expires_at = timezone.now() + timezone.timedelta(hours=24)
            next_in_queue.save()

            book.available_copies = 0
            book.save()

            # --- SEND NOTIFICATION EMAIL ---
            subject = f"Your Reserved Book is Waiting: '{book.title}'"

            # --- DYNAMIC URL LOGIC ---
            # Construct the full URL to the book's page on the frontend.
            book_detail_path = f"/books/{book.id}/"
            full_cta_url = f"{settings.FRONTEND_BASE_URL}{book_detail_path}"

            context = {
                "email_title": "Your Reservation is Ready!",
                "user_name": user.first_name,
                "user_email": user.email,
                "main_message": f"Great news! The book you were waiting for, '{book.title}', is now available. We have placed it on hold for you.",
                "book_title": book.title,
                "book_author": book.author,
                "alert_message": "Please borrow the book within the next 24 hours. After this period, your reservation will expire and the book will be offered to the next person in the queue.",
                "cta_url": full_cta_url,  # <-- Use the dynamic URL
                "cta_text": "View Your Book & Borrow",
            }

            send_verification_email_task.delay(
                subject, "emails/book_reservation_ready.html", context, [user.email]
            )

            return f"Reserved '{book.title}' and sent notification to {user.email}."

        else:
            # No one is in the queue, make the book available
            book.available_copies = 1
            book.save()
            return f"No active queue for '{book.title}'. Made book available."

    except Book.DoesNotExist:
        return f"Book with id {book_id} not found."


@shared_task
def check_expired_queues():
    """
    Finds and expires reservations that were not acted upon in time.
    """
    now = timezone.now()
    # Find reservations where the 24-hour window has passed
    expired_reservations = BookQueue.objects.filter(
        expires_at__lt=now, status=BookQueue.QueueStatus.RESERVED
    )

    expired_count = 0
    for reservation in expired_reservations:
        reservation.status = BookQueue.QueueStatus.EXPIRED
        reservation.save()
        expired_count += 1
        # The book is now free. Promote the next person.
        promote_next_in_queue.delay(reservation.book.id)

    if expired_count > 0:
        return f"Expired {expired_count} reservations and triggered promotions."

    return "No reservations to expire."
