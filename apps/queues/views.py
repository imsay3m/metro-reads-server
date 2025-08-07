from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response

from .models import BookQueue
from .serializers import BookQueueSerializer


class QueueViewSet(
    mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """
    ViewSet for managing a user's own queue entries.
    - list: Shows all active queues for the authenticated user.
    - destroy: Allows a user to leave (delete) their queue entry.
    """

    serializer_class = BookQueueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Users can only see and manage their own queue entries.
        """
        return BookQueue.objects.filter(
            user=self.request.user, status=BookQueue.QueueStatus.ACTIVE
        ).select_related(
            "book"
        )  # Optimization

    def perform_destroy(self, instance):
        """
        Override destroy to just mark the queue entry as 'EXPIRED'
        instead of deleting, for historical tracking.
        """
        instance.status = BookQueue.QueueStatus.EXPIRED
        instance.save()
