from django.conf import settings
from django.db import models
from django.utils import timezone


class BookQueue(models.Model):
    class QueueStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"  # User is waiting in line.
        RESERVED = (
            "RESERVED",
            "Reserved",
        )  # User is at the front and the book is held for them.
        FULFILLED = "FULFILLED", "Fulfilled"  # User successfully borrowed the book.
        EXPIRED = (
            "EXPIRED",
            "Expired",
        )  # User's turn came up but they didn't borrow in time.

    book = models.ForeignKey(
        "books.Book", on_delete=models.CASCADE, related_name="queues"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="queues"
    )
    status = models.CharField(
        max_length=20, choices=QueueStatus.choices, default=QueueStatus.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # This field will now be updated when a reservation is made
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        unique_together = ("book", "user")

    def save(self, *args, **kwargs):
        # We no longer need the default expiration logic here
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} in queue for {self.book.title}"
