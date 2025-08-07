from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "isbn",
        "published_date",
        "total_copies",
        "available_copies",
    )
    search_fields = ("title", "author", "isbn")
