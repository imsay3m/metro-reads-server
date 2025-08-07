from django.contrib import admin

from .models import BookQueue


@admin.register(BookQueue)
class BookQueueAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "status", "created_at", "expires_at")
    search_fields = ("book__title", "user__email")
    list_filter = ("status",)
