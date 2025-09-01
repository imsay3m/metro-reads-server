from django.test import TestCase
from django.utils import timezone

from apps.books.models import Book
from apps.queues.models import BookQueue
from apps.queues.tasks import promote_next_in_queue
from apps.users.models import User


class QueueLogicTests(TestCase):

    def setUp(self):
        """Set up a book and two users for testing."""
        self.book = Book.objects.create(
            title="Test Book for Queues",
            author="Test Author",
            isbn="9999999999999",
            published_date=timezone.now().date(),
            total_copies=1,
            available_copies=0,
        )
        self.user1 = User.objects.create_user(email="user1@test.com", password="p")
        self.user2 = User.objects.create_user(email="user2@test.com", password="p")

    def test_queue_fifo_promotion(self):
        """
        Tests that the first user to join the queue is the first to be promoted.
        """
        # User1 joins the queue first.
        BookQueue.objects.create(book=self.book, user=self.user1)
        # User2 joins second.
        BookQueue.objects.create(book=self.book, user=self.user2)

        promote_next_in_queue(self.book.id)

        q1 = BookQueue.objects.get(user=self.user1, book=self.book)
        q2 = BookQueue.objects.get(user=self.user2, book=self.book)

        self.assertEqual(q1.status, BookQueue.QueueStatus.RESERVED)
        self.assertEqual(q2.status, BookQueue.QueueStatus.ACTIVE)
