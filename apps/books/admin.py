from django.contrib import admin

from .models import Book, Review


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "isbn",
        "publisher",
        "total_copies",
        "available_copies",
    )
    search_fields = ("title", "author", "isbn", "publisher")
    list_filter = ("genres", "publisher")
    filter_horizontal = ("genres",)


# Register the Review model for admin management
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "created_at", "text")
    search_fields = ("book__title", "user__email", "text")
    list_filter = ("book", "user", "created_at")
