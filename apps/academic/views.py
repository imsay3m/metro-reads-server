from rest_framework import permissions, viewsets

from apps.books.serializers import GenreSerializer

from .models import Genre


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving genres.
    Provides read-only access to all genres.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticated]
