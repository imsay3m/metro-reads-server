from django.contrib import admin, messages
from django.core.files.storage import default_storage

# Imports for the new action
from apps.cards.models import LibraryCard
from apps.cards.tasks import generate_library_card_pdf_task

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "student_id",
        "department",
        "role",
        "account_status",
        "is_active",
    )
    list_filter = ("role", "is_active", "account_status", "department")
    search_fields = (
        "email",
        "first_name",
        "last_name",
        "student_id",
        "department__name",
    )
    actions = ["generate_library_cards"]

    # Use fieldsets to group related fields for a cleaner layout
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "profile_picture",
                    "phone_number",
                    "address",
                )
            },
        ),
        ("Academic Info", {"fields": ("department", "student_id", "batch", "section")}),
        (
            "Permissions & Status",
            {
                "fields": (
                    "role",
                    "account_status",
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Library Card", {"fields": ("library_card",)}),
    )
    # Add password to readonly_fields to prevent accidental viewing of the hash
    readonly_fields = ("last_login", "date_joined")
    add_fieldsets = fieldsets  # Use the same layout for adding new users

    @admin.action(description="Generate or Re-generate library card(s)")
    def generate_library_cards(self, request, queryset):
        """
        A custom admin action to create a new library card and generate a PDF for it.
        """
        generated_count = 0
        for user in queryset:
            # If user already has a card, deactivate the old one.
            if hasattr(user, "library_card") and user.library_card:
                user.library_card.is_active = False
                user.library_card.save()

            # Create a new library card instance
            new_card = LibraryCard.objects.create()
            user.library_card = new_card
            user.save()

            # Enqueue async PDF generation task
            generate_library_card_pdf_task.delay(user.id, str(new_card.id))

            generated_count += 1

        self.message_user(
            request,
            f"{generated_count} library card(s) were successfully generated.",
            messages.SUCCESS,
        )
