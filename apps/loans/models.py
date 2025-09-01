from django.conf import settings
from django.db import models


class Loan(models.Model):
    book = models.ForeignKey(
        "books.Book", on_delete=models.CASCADE, related_name="loans"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loans"
    )
    loan_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    renewals_made = models.PositiveSmallIntegerField(default=0)
    checked_out_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_checkouts",
        limit_choices_to={"role__in": ["LIBRARIAN", "ADMIN"]},
    )

    def __str__(self):
        return f"{self.user.email} loaned {self.book.title}"


class Fine(models.Model):
    class FineStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        WAIVED = "WAIVED", "Waived"

    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name="fine")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fines"
    )
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20, choices=FineStatus.choices, default=FineStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fine of ${self.amount} for {self.user.email} on loan of '{self.loan.book.title}'"
