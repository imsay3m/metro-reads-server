import uuid

from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone


def get_expiry_date():
    return timezone.now() + relativedelta(years=1)


class LibraryCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(default=get_expiry_date)
    pdf_card = models.FileField(upload_to="library_cards/", null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)
