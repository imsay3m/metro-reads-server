from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.utils import timezone
from rest_framework import serializers

from apps.queues.models import BookQueue
from apps.site_config.models import LibrarySettings

from .models import Loan


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

        reservation = BookQueue.objects.filter(
            book=book, user=user, status=BookQueue.QueueStatus.RESERVED
        ).first()

        if reservation:
            return book

        if book.available_copies <= 0:
            raise serializers.ValidationError(
                "This book is not currently available. Please join the queue."
            )

        return book

    def create(self, validated_data):
        book = validated_data["book"]
        user = self.context["request"].user
        settings = LibrarySettings.get_solo()

        reservation = BookQueue.objects.filter(
            book=book, user=user, status=BookQueue.QueueStatus.RESERVED
        ).first()

        if reservation:
            reservation.status = BookQueue.QueueStatus.FULFILLED
            reservation.save()
        else:
            book.available_copies -= 1
            book.save()

        cache.delete(f"book:detail:{book.pk}")
        cache.delete_pattern("books:list:*")

        loan = Loan.objects.create(
            book=book,
            user=user,
            due_date=timezone.now() + relativedelta(days=settings.loan_duration_days),
        )
        return loan
