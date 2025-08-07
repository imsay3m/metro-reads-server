from django.contrib import admin

from .models import LibraryCard


@admin.register(LibraryCard)
class LibraryCardAdmin(admin.ModelAdmin):
    list_display = ("id", "issue_date", "expiry_date", "is_active")
    search_fields = ("id",)
