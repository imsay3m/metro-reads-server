from rest_framework import serializers

# Corrected Imports:
from apps.books.models import Book  # <-- IMPORT Book from the correct app

from .models import BookQueue  # <-- IMPORT BookQueue from the local models


class BookQueueSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying a user's position in a book queue.
    """

    book_title = serializers.CharField(source="book.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    position = serializers.SerializerMethodField()

    class Meta:
        model = BookQueue
        fields = [
            "id",
            "book",
            "book_title",
            "user",
            "user_email",
            "status",
            "created_at",
            "position",
        ]

    def get_position(self, obj):
        """
        Calculates the user's current position in the queue for a specific book.
        """
        position = (
            BookQueue.objects.filter(
                book=obj.book,
                status=BookQueue.QueueStatus.ACTIVE,
                created_at__lt=obj.created_at,
            ).count()
            + 1
        )
        return position


class JoinQueueSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(write_only=True)

    def validate(self, data):
        user = self.context["request"].user
        try:
            book = Book.objects.get(pk=data["book_id"])
        except Book.DoesNotExist:
            raise serializers.ValidationError({"detail": "Book not found."})

        # --- IMPROVED VALIDATION LOGIC ---
        # We now check for any existing queue entry for this user and book,
        # regardless of its status.
        existing_queue_entry = BookQueue.objects.filter(book=book, user=user).first()
        if existing_queue_entry:
            # Provide a specific message based on the status.
            if existing_queue_entry.status == BookQueue.QueueStatus.ACTIVE:
                raise serializers.ValidationError(
                    {"detail": "You are already in the active queue for this book."}
                )
            if existing_queue_entry.status == BookQueue.QueueStatus.RESERVED:
                raise serializers.ValidationError(
                    {
                        "detail": "This book is already reserved for you. Please borrow it directly."
                    }
                )
            # You could add more checks here for FULFILLED or EXPIRED if you want,
            # but for now, preventing re-joining is the key.
            # A more advanced option would be to "reactivate" an expired entry.
            # For now, we'll just block it.
            raise serializers.ValidationError(
                {
                    "detail": "You have a previous queue entry for this book and cannot rejoin at this time."
                }
            )

        if book.available_copies > 0:
            raise serializers.ValidationError(
                {"detail": "This book is currently available and cannot be queued for."}
            )

        if user.loans.filter(book=book, is_returned=False).exists():
            raise serializers.ValidationError(
                {
                    "detail": "You cannot join the queue for a book you currently have on loan."
                }
            )

        return data
