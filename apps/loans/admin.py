from django.contrib import admin

from .models import Fine, Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "book",
        "user",
        "loan_date",
        "due_date",
        "is_returned",
        "renewals_made",
    )
    list_filter = ("is_returned", "loan_date")
    search_fields = ("user__email", "book__title")
    readonly_fields = ("checked_out_by",)


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ("user", "loan", "amount", "status")
    list_filter = ("status",)
    readonly_fields = ("amount",)
