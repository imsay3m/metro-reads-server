from rest_framework import serializers

from apps.books.serializers import BookSerializer

from .models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "book", "book_id", "added_date"]
        read_only_fields = ["id", "added_date"]


class WishlistCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating wishlist items.
    """

    class Meta:
        model = Wishlist
        fields = ["book_id"]

    def create(self, validated_data):
        """
        Create a new wishlist item.
        The user is automatically set from the request context.
        """
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
