from dateutil.relativedelta import relativedelta
from django.core.cache import cache  # Import cache
from django.utils import timezone
from rest_framework import serializers

from apps.books.models import Book
from apps.queues.models import BookQueue

from .models import Loan


# ... LoanSerializer remains the same ...
class LoanSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = Loan
        fields = [
            "id",
            "book",
            "user",
            "loan_date",
            "due_date",
            "return_date",
            "is_returned",
        ]


class CreateLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ["book"]

    def validate_book(self, book):
        """
        Check if the book can be borrowed by the current user.
        """
        user = self.context["request"].user

        # Check if the user has a reservation for this book
        reservation = BookQueue.objects.filter(
            book=book, user=user, status=BookQueue.QueueStatus.RESERVED
        ).first()

        if reservation:
            # User has a reservation, they are allowed to borrow.
            return book

        # No reservation, check if the book is generally available.
        if book.available_copies <= 0:
            raise serializers.ValidationError(
                "This book is not currently available. Please join the queue."
            )

        return book

    def create(self, validated_data):
        book = validated_data["book"]
        user = self.context["request"].user

        # Check if the user had a reservation and fulfill it
        reservation = BookQueue.objects.filter(
            book=book, user=user, status=BookQueue.QueueStatus.RESERVED
        ).first()

        if reservation:
            reservation.status = BookQueue.QueueStatus.FULFILLED
            reservation.save()
            # The promotion task already set copies to 0, so we don't decrement again.
        else:
            # Standard borrow, decrement available copies.
            book.available_copies -= 1
            book.save()

        # Invalidate cache
        cache.delete(f"book:detail:{book.pk}")
        cache.delete_pattern("books:list:*")

        loan = Loan.objects.create(
            book=book, user=user, due_date=timezone.now() + relativedelta(weeks=2)
        )
        return loan
