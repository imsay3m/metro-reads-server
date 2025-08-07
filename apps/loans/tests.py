from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.books.models import Book
from apps.site_config.models import LibrarySettings
from apps.users.models import User

from .models import Loan
from .tasks import calculate_and_notify_fines


class FineCalculationTests(TestCase):
    def setUp(self):
        # Ensure library settings exist with a fine
        LibrarySettings.get_solo().fine_per_day = 0.50
        LibrarySettings.get_solo().save()

        self.user = User.objects.create_user(email="member@test.com", password="p")
        self.book = Book.objects.create(title="Test Book", author="Author", isbn="111")

        # Create a loan that became overdue yesterday
        self.loan = Loan.objects.create(
            user=self.user, book=self.book, due_date=timezone.now() - timedelta(days=1)
        )

    def test_overdue_loan_creates_fine(self):
        """Tests that the daily task creates a fine for an overdue book."""
        # Run the Celery task synchronously for testing
        calculate_and_notify_fines()

        self.loan.refresh_from_db()
        self.assertTrue(hasattr(self.loan, "fine"))
        self.assertEqual(self.loan.fine.amount, 0.50)
