from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.queues.models import BookQueue
from apps.queues.serializers import JoinQueueSerializer
from apps.users.permissions import IsAdminOrLibrarian

from .models import Book
from .serializers import BookSerializer

# Cache timeouts (in seconds)
CACHE_TTL_BOOKS_LIST = 60 * 5  # 5 minutes
CACHE_TTL_BOOK_DETAIL = 60 * 1  # 1 minute


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Books with caching.
    - list: Results are cached for 5 minutes.
    - retrieve: Book details are cached for 1 minute.
    - Caches are invalidated on update/destroy.
    """

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["title", "author", "isbn", "publisher"]
    filterset_fields = {
        "genres__slug": [
            "in",
            "exact",
        ],  # ?genres__slug=science-fiction or ?genres__slug__in=sci-fi,mystery
        "author": ["exact"],
        "publisher": ["exact"],
    }

    def get_permissions(self):
        if self.action in ["list", "retrieve", "join_queue"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            # All other actions (create, update, destroy) are restricted.
            permission_classes = [IsAdminOrLibrarian]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """
        Overrides the default list action to implement caching for search results.
        """
        search_query = request.query_params.get("search", "all")
        cache_key = f"books:list:{search_query}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)

        if response.status_code == 200:
            cache.set(cache_key, response.data, CACHE_TTL_BOOKS_LIST)

        return response

    def retrieve(self, request, *args, **kwargs):
        """
        Overrides the default retrieve action to implement caching for a single book.
        """
        book_id = self.kwargs.get("pk")
        cache_key = f"book:detail:{book_id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)

        if response.status_code == 200:
            cache.set(cache_key, response.data, CACHE_TTL_BOOK_DETAIL)

        return response

    def perform_update(self, serializer):
        """
        Invalidates the book detail cache on update.
        """
        instance = serializer.save()
        cache.delete(f"book:detail:{instance.pk}")
        cache.delete_pattern("books:list:*")

    def perform_destroy(self, instance):
        """
        Invalidates the book detail cache on delete.
        """
        book_id = instance.pk
        instance.delete()
        cache.delete(f"book:detail:{book_id}")
        cache.delete_pattern("books:list:*")

    @action(detail=True, methods=["post"], url_path="join-queue")
    def join_queue(self, request, pk=None):
        """
        Allows an authenticated user to join the waiting queue for a book.
        """
        book = self.get_object()
        serializer = JoinQueueSerializer(
            data={"book_id": book.id}, context={"request": request}
        )

        if serializer.is_valid():
            BookQueue.objects.create(book=book, user=request.user)
            return Response(
                {"status": "You have been added to the queue."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
