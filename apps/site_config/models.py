from django.db import models
from solo.models import SingletonModel


class LibrarySettings(SingletonModel):
    fine_per_day = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.25,
        help_text="The amount charged per day for an overdue book.",
    )
    loan_duration_days = models.PositiveIntegerField(
        default=14, help_text="The number of days a member can borrow a book."
    )
    max_renewals = models.PositiveIntegerField(
        default=2, help_text="The maximum number of times a loan can be renewed."
    )
    reservation_expiry_hours = models.PositiveIntegerField(
        default=24,
        help_text="The number of hours a member has to borrow a reserved book before the reservation expires.",
    )

    def __str__(self):
        return "Library Settings"

    class Meta:
        verbose_name = "Library Settings"
