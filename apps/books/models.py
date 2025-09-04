from django.conf import settings
from django.db import models

from apps.academic.models import Genre


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField()
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover_image = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    page_count = models.PositiveIntegerField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, blank=True, related_name="books")

    def __str__(self):
        return f"{self.title} by {self.author}"


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]  # Show the newest reviews first

    def __str__(self):
        return f"Review by {self.user.email} for {self.book.title}"
