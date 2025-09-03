from django.conf import settings
from django.db import models


class Wishlist(models.Model):
    """
    Model representing a user's wishlist of books.
    Each user can have multiple books in their wishlist.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    book = models.ForeignKey(
        "books.Book", on_delete=models.CASCADE, related_name="wishlist_items"
    )
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "book"]
        ordering = ["-added_date"]

    def __str__(self):
        return f"{self.user.email} - {self.book.title}"
