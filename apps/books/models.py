from django.db import models

from apps.academic.models import Genre


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField()
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover_image = models.ImageField(upload_to="book_covers/", null=True, blank=True)
    description = models.TextField(blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    page_count = models.PositiveIntegerField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, blank=True, related_name="books")

    def __str__(self):
        return f"{self.title} by {self.author}"
