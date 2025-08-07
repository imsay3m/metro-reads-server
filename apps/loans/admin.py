from django.contrib import admin

from .models import Fine, Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "loan_date", "due_date", "is_returned")
    list_filter = ("is_returned", "loan_date")


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ("user", "loan", "amount", "status")
    list_filter = ("status",)
    # Make amount read-only as it's calculated automatically
    readonly_fields = ("amount",)
