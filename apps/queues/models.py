from django.conf import settings
from django.db import models
from django.utils import timezone


class BookQueue(models.Model):
    class QueueStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        RESERVED = (
            "RESERVED",
            "Reserved",
        )
        FULFILLED = "FULFILLED", "Fulfilled"
        EXPIRED = (
            "EXPIRED",
            "Expired",
        )

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
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        unique_together = ("book", "user")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} in queue for {self.book.title}"
