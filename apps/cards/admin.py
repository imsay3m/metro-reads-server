from django.contrib import admin

from .models import LibraryCard


@admin.register(LibraryCard)
class LibraryCardAdmin(admin.ModelAdmin):
    list_display = ("id", "user_email", "issue_date", "expiry_date", "is_active")
    readonly_fields = ("pdf_card",)

    def user_email(self, obj):
        if hasattr(obj, "user") and obj.user:
            return obj.user.email
        return "N/A"

    user_email.short_description = "User"
