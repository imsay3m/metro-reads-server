from django.core.cache import cache
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.queues.tasks import promote_next_in_queue
from apps.users.permissions import IsAdminOrLibrarian

from .models import Fine, Loan
from .serializers import CreateLoanSerializer, FineSerializer, LoanSerializer


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

    @action(detail=True, methods=["post"], url_path="renew")
    def renew_loan(self, request, pk=None):
        """
        Allows the owning user to renew a loan if they have not
        exceeded the maximum number of renewals.
        """
        loan = self.get_object()
        settings = LibrarySettings.get_solo()

        # Validation
        if loan.user != request.user:
            return Response(
                {"detail": "You do not have permission to renew this loan."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if loan.is_returned:
            return Response(
                {"detail": "Cannot renew a loan that has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if loan.renewals_made >= settings.max_renewals:
            return Response(
                {
                    "detail": f"You have reached the maximum of {settings.max_renewals} renewals for this loan."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if another user is in the queue
        if loan.book.queues.filter(status="ACTIVE").exists():
            return Response(
                {
                    "detail": "Cannot renew this loan as other members are waiting in the queue."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update the loan
        loan.due_date += relativedelta(days=settings.loan_duration_days)
        loan.renewals_made += 1
        loan.save()

        serializer = self.get_serializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)

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


class FineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing fines. Librarians/Admins can also mark fines as paid or waived.
    """

    queryset = Fine.objects.all()
    serializer_class = FineSerializer
    permission_classes = [IsAdminOrLibrarian]  # Only staff can access

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_as_paid(self, request, pk=None):
        """Marks a fine as Paid."""
        fine = self.get_object()
        fine.status = Fine.FineStatus.PAID
        fine.save()
        # Potentially update user's account status
        # ...
        return Response({"status": "Fine marked as paid."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="mark-waived")
    def mark_as_waived(self, request, pk=None):
        """Marks a fine as Waived."""
        fine = self.get_object()
        fine.status = Fine.FineStatus.WAIVED
        fine.save()
        return Response({"status": "Fine marked as waived."}, status=status.HTTP_200_OK)
