from django.core.cache import cache
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.queues.tasks import promote_next_in_queue
from apps.users.permissions import IsAdminOrLibrarian

from .models import Loan
from .serializers import CreateLoanSerializer, LoanSerializer


class LoanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Loans.
    - list/retrieve: Members can see their own loans. Admins/Librarians can see all loans.
    - create (borrow): Members can borrow an available book.
    - return_book: Members can return a book they have loaned.
    """

    serializer_class = LoanSerializer

    def get_queryset(self):
        """
        This view should return a list of all the loans
        for the currently authenticated user.
        Admins/Librarians can see all loans.
        """
        user = self.request.user
        if user.role in ["ADMIN", "LIBRARIAN"]:
            return Loan.objects.all()
        return Loan.objects.filter(user=user)

    def get_serializer_class(self):
        """
        Return different serializers for create vs other actions.
        """
        if self.action == "create":
            return CreateLoanSerializer
        return LoanSerializer

    def get_permissions(self):
        """
        Admins/Librarians have full access. Authenticated members can create/return.
        """
        if self.action in ["list", "retrieve", "create", "return_book"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminOrLibrarian]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        loan = self.get_object()
        if loan.is_returned:
            return Response(
                {"detail": "This book has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        loan.is_returned = True
        loan.return_date = timezone.now()
        loan.save()

        book = loan.book

        promote_next_in_queue.delay(book.id)

        cache.delete(f"book:detail:{book.pk}")
        cache.delete_pattern("books:list:*")

        serializer = self.get_serializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)
