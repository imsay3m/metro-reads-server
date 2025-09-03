from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .models import Wishlist
from .serializers import WishlistCreateSerializer, WishlistSerializer


class WishlistViewSet(viewsets.ModelViewSet):
    """
    Simple ViewSet for managing user wishlist items.
    """

    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return wishlist items for the authenticated user only.
        """
        return Wishlist.objects.filter(user=self.request.user).select_related("book")

    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == "create":
            return WishlistCreateSerializer
        return WishlistSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book_id = serializer.validated_data["book_id"]
        if Wishlist.objects.filter(user=request.user, book_id=book_id).exists():
            return Response(
                {"detail": "This book is already in your wishlist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)

        wishlist_item = Wishlist.objects.get(user=request.user, book_id=book_id)
        response_serializer = WishlistSerializer(wishlist_item)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
