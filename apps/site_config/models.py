from django.db import models
from solo.models import SingletonModel


class LibrarySettings(SingletonModel):
    fine_per_day = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.25,
        help_text="The amount charged per day for an overdue book.",
    )
    # We can add more settings here later, like loan_duration_days

    def __str__(self):
        return "Library Settings"

    class Meta:
        verbose_name = "Library Settings"
